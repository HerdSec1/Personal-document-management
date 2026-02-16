import sqlite3
from pathlib import Path

from src.db import init_db, start_session, end_session


def test_session_start_and_end(tmp_path: Path):
    db_path = tmp_path / "test.db"
    init_db(db_path=db_path)

    session_id = start_session(db_path=db_path, vault_root=tmp_path, notes="unit test")
    assert session_id

    end_session(db_path=db_path, session_id=session_id)

    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT session_id, started_at, ended_at, username, hostname, vault_root, notes FROM sessions WHERE session_id = ?",
            (session_id,),
        )
        row = cur.fetchone()
        assert row is not None
        assert row[0] == session_id
        assert row[1] is not None  # started_at
        assert row[2] is not None  # ended_at
        assert row[5] is not None  # vault_root
        assert row[6] == "unit test"
    finally:
        conn.close()
