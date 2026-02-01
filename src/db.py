import sqlite3
from pathlib import Path
from datetime import datetime, timezone

DEFAULT_DATA_DIR = Path("data")
DEFAULT_DB_PATH = DEFAULT_DATA_DIR / "documents.db"


def init_db(db_path: Path | None = None) -> Path:
    """
    Initialize the SQLite database and create required tables if they do not exist.
    If db_path is not provided, defaults to data/documents.db.
    Returns the path to the database file.
    """
    db_path = db_path or DEFAULT_DB_PATH
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_filename TEXT NOT NULL,
                stored_path TEXT NOT NULL,
                sha256 TEXT,
                category TEXT,
                tags TEXT,
                doc_date TEXT,
                ingested_at TEXT NOT NULL
            )
        """)
        conn.commit()
    finally:
        conn.close()

    return db_path


def utc_now_iso() -> str:
    """Convenience helper for ISO timestamps (UTC)."""
    return datetime.now(timezone.utc).isoformat()
