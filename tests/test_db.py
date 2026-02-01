import sqlite3
from pathlib import Path

from src.db import init_db


def test_init_db_creates_db_and_documents_table(tmp_path: Path):
    # Arrange: use a temp database path
    db_path = tmp_path / "test_documents.db"

    # Act
    created_path = init_db(db_path=db_path)

    # Assert: DB file exists
    assert created_path.exists()

    # Assert: documents table exists
    conn = sqlite3.connect(created_path)
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='documents';
        """)
        row = cur.fetchone()
        assert row is not None
        assert row[0] == "documents"
    finally:
        conn.close()
