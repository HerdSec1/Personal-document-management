import getpass
import platform
import uuid
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

        # Core documents table
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

        # Session / audit table (records timeframe + user/device info)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                started_at TEXT NOT NULL,
                ended_at TEXT,
                username TEXT NOT NULL,
                hostname TEXT NOT NULL,
                vault_root TEXT,
                notes TEXT
            )
        """)

        conn.commit()
    finally:
        conn.close()

    return db_path


def utc_now_iso() -> str:
    """Convenience helper for ISO timestamps (UTC)."""
    return datetime.now(timezone.utc).isoformat()


def start_session(db_path: Path, vault_root: Path | None = None, notes: str | None = None) -> str:
    """
    Create a new session record and return the session_id.
    This is intended to run when PerDocMan starts.
    """
    session_id = uuid.uuid4().hex
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO sessions (session_id, started_at, username, hostname, vault_root, notes)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                session_id,
                utc_now_iso(),
                getpass.getuser(),
                platform.node(),
                str(vault_root) if vault_root else None,
                notes,
            ),
        )
        conn.commit()
    finally:
        conn.close()

    return session_id


def end_session(db_path: Path, session_id: str) -> None:
    """
    Mark a session as ended. Safe to call once (won't overwrite an existing ended_at).
    Intended to run when PerDocMan exits.
    """
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE sessions
            SET ended_at = ?
            WHERE session_id = ? AND ended_at IS NULL
            """,
            (utc_now_iso(), session_id),
        )
        conn.commit()
    finally:
        conn.close()
