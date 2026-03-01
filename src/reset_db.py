from __future__ import annotations

import sqlite3
from pathlib import Path

from src.db import init_db

def reset_database(db_path: Path) -> None:
    """
    Reset database contents without deleting the DB file.
    This avoids Windows file-lock issues when the server is running.
    """
    db_path = init_db(db_path=db_path)  # ensure tables exist
    docs_dir = Path("data") / "documents"
    if docs_dir.exists():
        for f in docs_dir.glob("*.pdf"):
            try:
                f.unlink()
            except OSError:
                pass

    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM documents;")
        cur.execute("DELETE FROM sessions;")
        conn.commit()
    finally:
        conn.close()