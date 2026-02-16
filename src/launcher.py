from __future__ import annotations

import threading
import time
import webbrowser
from pathlib import Path

from src.db import init_db, start_session, end_session
from src.perdocman_server import make_server


def run(vault_root: Path | None = None) -> int:
    if vault_root:
        db_path = init_db(vault_root / "perdocman_documents.db")
    else:
        db_path = init_db()  # later: init_db(vault_root/db file)
    session_id = start_session(db_path=db_path, vault_root=vault_root, notes="PerDocMan launcher session")

    server = make_server("127.0.0.1", 0, db_path=db_path, vault_root=vault_root)  # port=0 picks an open port
    host, port = server.server_address
    url = f"http://{host}:{port}/"

    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    # Give the server a moment to come up
    time.sleep(0.1)
    webbrowser.open(url)

    print(f"PerDocMan running at {url}")
    print("Press Ctrl+C to stop.")

    try:
        while thread.is_alive():
            time.sleep(0.25)
    except KeyboardInterrupt:
        pass
    finally:
        server.shutdown()
        server.server_close()
        end_session(db_path=db_path, session_id=session_id)
        print("PerDocMan stopped.")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
