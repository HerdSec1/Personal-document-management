from __future__ import annotations

import sqlite3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


def get_doc_count(db_path: Path) -> int:
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM documents")
        (count,) = cur.fetchone()
        return int(count)
    finally:
        conn.close()


class PerDocManHandler(BaseHTTPRequestHandler):
    # These get injected by the server factory
    db_path: Path = Path("data") / "documents.db"
    vault_root: Path | None = None

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/":
            self.handle_dashboard()
            return

        self.send_response(404)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"Not Found")

    def handle_dashboard(self) -> None:
        count = get_doc_count(self.db_path)
        vault = str(self.vault_root) if self.vault_root else "(not set)"

        html = f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>PerDocMan</title>
</head>
<body>
  <h1>PerDocMan (Prototype)</h1>
  <p><strong>Status:</strong> Running locally</p>
  <p><strong>Database:</strong> {self.db_path}</p>
  <p><strong>Vault Root:</strong> {vault}</p>
  <p><strong>Documents indexed:</strong> {count}</p>

  <hr/>
  <p>Next: add ingestion + search pages.</p>
</body>
</html>"""

        body = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    # Keep the console clean (optional)
    def log_message(self, format: str, *args) -> None:
        return


def make_server(host: str, port: int, *, db_path: Path, vault_root: Path | None = None) -> ThreadingHTTPServer:
    # Inject config onto handler class
    PerDocManHandler.db_path = db_path
    PerDocManHandler.vault_root = vault_root
    return ThreadingHTTPServer((host, port), PerDocManHandler)
