from __future__ import annotations

import hashlib
import sqlite3
import uuid
import shutil
from pathlib import Path
from pypdf import PdfReader

from src.db import init_db, utc_now_iso
from src.config import build_paths


def sha256_file(path: Path) -> str:
    """Compute SHA-256 for a file without loading it all into memory."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def extract_preview_text(pdf_path: Path, *, char_limit: int = 1000, max_pages: int = 2) -> str | None:
    """
    Extract a short text preview from the first pages of a PDF.
    Returns None if extraction fails or yields no text.
    """
    try:
        reader = PdfReader(str(pdf_path))
        chunks: list[str] = []
        for page in reader.pages[:max_pages]:
            txt = page.extract_text() or ""
            if txt:
                chunks.append(txt)
            if sum(len(c) for c in chunks) >= char_limit:
                break

        preview = "\n".join(chunks).strip()
        return preview[:char_limit] if preview else None
    except Exception:
        return None

def derive_display_title(original_filename: str, content_preview: str | None) -> str:
    """
    Prefer a human-readable title from the document text preview.
    Falls back to the original filename.
    """
    if content_preview:
        for line in content_preview.splitlines():
            line = line.strip()
            if line:
                return line[:80]
    return original_filename

def ingest_pdf(
    source_pdf: Path,
    *,
    original_filename: str | None = None,
    db_path: Path | None = None,
    storage_dir: Path | None = None,
    category: str | None = None,
    tags: str | None = None,
    doc_date: str | None = None,
    sensitivity: str | None = None,
    expires_at: str | None = None,
) -> int:
    """
    Ingest a PDF by copying it into managed local storage and recording metadata in SQLite.

    Notes (prototype constraints):
    - - Extracts a short text preview (first 1–2 pages) for retrieval UX; full-text/semantic indexing is future work.
    - Assumes file is a PDF based on extension (basic check).
    - tags is stored as a comma-separated string for now.
    """
    source_pdf = Path(source_pdf)

    if not source_pdf.exists() or not source_pdf.is_file():
        raise FileNotFoundError(f"Source file not found: {source_pdf}")

    if source_pdf.suffix.lower() != ".pdf":
        raise ValueError("Only .pdf files are supported for ingestion in this prototype.")

    # Ensure DB exists (and schema exists)
    db_path = init_db(db_path=db_path)

    # Default storage: data/documents/
    storage_dir = storage_dir or (Path("data") / "documents")
    storage_dir.mkdir(parents=True, exist_ok=True)

    # Create a safe non-overwriting filename
    # Example: "statement_2024__a1b2c3d4.pdf"
    metadata_filename = original_filename or source_pdf.name
    stem = source_pdf.stem
    safe_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_", " ")).strip().replace(" ", "_")
    suffix = uuid.uuid4().hex[:8]
    stored_filename = f"{safe_stem}__{suffix}.pdf"
    stored_path = storage_dir / stored_filename

    # Hash after copy (hashing either source or stored is fine; stored proves integrity of what we keep)
    file_hash = sha256_file(source_pdf)

    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()

        # Duplicate check (single place)
        cur.execute("SELECT id FROM documents WHERE sha256 = ?", (file_hash,))
        existing = cur.fetchone()
        if existing:
            raise ValueError(f"This document has already been imported (ID {existing[0]}).")

        shutil.copy2(source_pdf, stored_path)

        content_preview = extract_preview_text(source_pdf)
        display_title = derive_display_title(metadata_filename, content_preview)

        sensitivity = (sensitivity or "moderate").strip().lower()
        expires_at = expires_at.strip() if expires_at else None

        cur.execute(
            """
            INSERT INTO documents (
                display_title,
                original_filename,
                stored_path,
                sha256,
                category,
                tags,
                doc_date,
                ingested_at,
                content_preview,
                sensitivity,
                expires_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                display_title,
                metadata_filename,
                str(stored_path),
                file_hash,
                category,
                tags,
                doc_date,
                utc_now_iso(),
                content_preview,
                sensitivity,
                expires_at,
            ),
        )

        conn.commit()
        return int(cur.lastrowid)

    finally:
        conn.close()