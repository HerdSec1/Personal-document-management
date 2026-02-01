import sqlite3
from pathlib import Path

from src.db import init_db
from src.ingest import ingest_pdf, sha256_file


def test_ingest_copies_file_and_inserts_row(tmp_path: Path):
    # Arrange: temp DB + temp storage dir
    db_path = tmp_path / "test_documents.db"
    storage_dir = tmp_path / "documents"
    init_db(db_path=db_path)

    # Create a fake PDF (minimal header is enough for our prototype)
    source_pdf = tmp_path / "test.pdf"
    source_pdf.write_bytes(b"%PDF-1.4\n%Fake PDF for test\n")

    # Act
    doc_id = ingest_pdf(
        source_pdf,
        db_path=db_path,
        storage_dir=storage_dir,
        category="finance",
        tags="statement,bank",
        doc_date="2026-02-01",
    )

    # Assert: file copied
    copied_files = list(storage_dir.glob("*.pdf"))
    assert len(copied_files) == 1
    stored_file = copied_files[0]
    assert stored_file.exists()

    # Assert: DB row inserted and points to stored file
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT original_filename, stored_path, sha256, category, tags, doc_date FROM documents WHERE id = ?",
            (doc_id,),
        )
        row = cur.fetchone()
        assert row is not None

        original_filename, stored_path, sha256, category, tags, doc_date = row
        assert original_filename == "test.pdf"
        assert Path(stored_path).exists()
        assert Path(stored_path).resolve() == stored_file.resolve()
        assert category == "finance"
        assert tags == "statement,bank"
        assert doc_date == "2026-02-01"

        # Hash should match what's stored
        assert sha256 == sha256_file(stored_file)
    finally:
        conn.close()
