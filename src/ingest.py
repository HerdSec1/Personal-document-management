from __future__ import annotations

import hashlib
import shutil
import sqlite3
import uuid
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

def ingest_pdf(
    source_pdf: Path,
    *,
    db_path: Path | None = None,
    storage_dir: Path | None = None,
    category: str | None = None,
    tags: str | None = None,
    doc_date: str | None = None,
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
    stem = source_pdf.stem
    safe_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_", " ")).strip().replace(" ", "_")
    suffix = uuid.uuid4().hex[:8]
    stored_filename = f"{safe_stem}__{suffix}.pdf"
    stored_path = storage_dir / stored_filename

    # Copy file
    shutil.copy2(source_pdf, stored_path)

    # Hash after copy (hashing either source or stored is fine; stored proves integrity of what we keep)
    file_hash = sha256_file(stored_path)

    # Check for duplicate by SHA-256
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        "SELECT id FROM documents WHERE sha256 = ?",
        (file_hash,)
    )
    existing = cur.fetchone()

    if existing:
        conn.close()
        # Option 1: Raise an error
        raise ValueError(f"This document has already been imported (ID {existing[0]}).")

    # Insert metadata row
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()

        # Check for duplicate by hash
        cur.execute(
            "SELECT id FROM documents WHERE sha256 = ?",
            (file_hash,)
        )
        existing = cur.fetchone()

        if existing:
            raise ValueError(
                f"This document has already been imported (ID {existing[0]})."
            )

        content_preview = extract_preview_text(stored_path)

        cur.execute(
            """
            INSERT INTO documents (
                original_filename,
                stored_path,
                sha256,
                category,
                tags,
                doc_date,
                ingested_at,
                content_preview
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                source_pdf.name,
                str(stored_path),
                file_hash,
                category,
                tags,
                doc_date,
                utc_now_iso(),
                content_preview,
            ),
        )

        conn.commit()
        return int(cur.lastrowid)

    finally:
        conn.close()