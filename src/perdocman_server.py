from __future__ import annotations

import cgi
import shutil
import sqlite3
import tempfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs, quote
from src.reset_db import reset_database
from src.db import init_db, get_doc_count, list_documents
from src.ingest import ingest_pdf

def _html_escape(value: object) -> str:
    text = "" if value is None else str(value)
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


class PerDocManHandler(BaseHTTPRequestHandler):
    # Injected by make_server()
    db_path: Path = Path("data") / "documents.db"
    vault_root: Path | None = None

    def do_GET(self) -> None:
        parsed = urlparse(self.path)

        if parsed.path == "/":
            self.handle_dashboard(parsed.query)
            return

        if parsed.path == "/documents":
            self.handle_documents()
            return
        
        if parsed.path == "/doc":
            self.handle_doc(parsed.query)
            return

        self.send_response(404)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"Not Found")

    def do_POST(self) -> None:
        parsed = urlparse(self.path)

        if parsed.path == "/ingest":
            self.handle_ingest()
            return
        
        if parsed.path == "/reset":
            self.handle_reset()
            return

        self.send_response(404)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"Not Found")

    def handle_reset(self) -> None:
        from src.reset_db import reset_database
        from urllib.parse import quote
        from src.db import init_db

        try:
            reset_database(db_path=self.db_path)
            init_db(db_path=self.db_path)

            msg = quote("Database reset successful")
            self.send_response(303)
            self.send_header("Location", f"/?level=success&msg={msg}")
            self.end_headers()

        except Exception as e:
            msg = quote(f"Reset failed: {e}")
            self.send_response(303)
            self.send_header("Location", f"/?level=error&msg={msg}")
            self.end_headers()
    
    def handle_dashboard(self, query: str = "") -> None:
        count = get_doc_count(self.db_path)
        vault = str(self.vault_root) if self.vault_root else "(not set)"
        params = parse_qs(query)
        msg = params.get("msg", [""])[0]
        level = params.get("level", ["info"])[0]  # info|success|error

        banner = ""
        if msg:
            safe_msg = _html_escape(msg)
            safe_level = _html_escape(level)
            banner = f"<p><strong>{safe_level.upper()}:</strong> {safe_msg}</p><hr/>"

        html = f"""<!doctype html>
            <html>
            <head>
            <meta charset="utf-8" />
            <title>PerDocMan</title>
            </head>
            <body>
            <h1>PerDocMan (Prototype)</h1>
            {banner}

            <p><strong>Documents indexed:</strong> {count}</p>
            <p><a href="/documents">View documents</a></p>
            <p><strong>Database:</strong> {_html_escape(self.db_path)}</p>
            <p><strong>Vault Root:</strong> {_html_escape(vault)}</p>

            <hr/>
            <h2>Upload PDF</h2>
            <form method="POST" action="/ingest" enctype="multipart/form-data">
                <input type="file" name="file" accept=".pdf" required />
                <button type="submit">Ingest</button>
            </form>

            <hr/>

            <h2>Admin</h2>
            <form method="POST" action="/reset" onsubmit="return confirm('Are you sure? This will wipe the database and cannot be undone.');">
            <button type="submit">Wipe Database</button>
            </form>

            </body>
            </html>"""

        body = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def handle_documents(self) -> None:
        rows = list_documents(self.db_path, limit=50)

        trs: list[str] = []
        for (doc_id, original_filename, category, tags, doc_date, ingested_at, stored_path, sha256) in rows:
            trs.append(
                "<tr>"
                f"<td>{doc_id}</td>"
                f"<td>{_html_escape(original_filename)}</td>"
                f"<td>{_html_escape(category)}</td>"
                f"<td>{_html_escape(tags)}</td>"
                f"<td>{_html_escape(doc_date)}</td>"
                f"<td>{_html_escape(ingested_at)}</td>"
                f"<td><a href='/doc?id={doc_id}' target='_blank'>Open</a></td>"
                "</tr>"
            )

        table_html = (
            "<table border='1' cellpadding='6' cellspacing='0'>"
            "<thead><tr>"
            "<th>ID</th><th>Filename</th><th>Category</th><th>Tags</th><th>Doc Date</th><th>Ingested At</th><th>Preview</th>"
            "</tr></thead>"
            "<tbody>"
            + ("".join(trs) if trs else "<tr><td colspan='7'>(no documents yet)</td></tr>")
            + "</tbody></table>"
        )

        html = f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>PerDocMan - Documents</title>
</head>
<body>
  <h1>Documents</h1>
  <p><a href="/">← Back to Dashboard</a></p>
  {table_html}
</body>
</html>"""

        body = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def handle_doc(self, query: str) -> None:
        params = parse_qs(query)
        doc_id_str = params.get("id", [""])[0]

        if not doc_id_str.isdigit():
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Invalid document id")
            return

        doc_id = int(doc_id_str)

        # Look up stored path in DB
        conn = sqlite3.connect(self.db_path)
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT stored_path, original_filename FROM documents WHERE id = ?",
                (doc_id,)
            )
            row = cur.fetchone()
        finally:
            conn.close()

        if not row:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Document not found")
            return

        stored_path, original_filename = row
        path = Path(stored_path)

        if not path.exists():
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"File not found on disk")
            return

        data = path.read_bytes()

        self.send_response(200)
        self.send_header("Content-Type", "application/pdf")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Content-Disposition", f'inline; filename="{original_filename}"')
        self.end_headers()
        self.wfile.write(data)

    def handle_ingest(self) -> None:
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={
                "REQUEST_METHOD": "POST",
                "CONTENT_TYPE": self.headers.get("Content-Type", ""),
                "CONTENT_LENGTH": self.headers.get("Content-Length", "0"),
            },
        )

        if "file" not in form:
            self.send_response(400)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"Missing form field: file")
            return

        file_item = form["file"]
        filename = getattr(file_item, "filename", None)
        if not filename:
            self.send_response(400)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"No file selected")
            return

        tmp_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                shutil.copyfileobj(file_item.file, tmp)
                tmp_path = Path(tmp.name)

            storage_dir = (self.vault_root / "documents") if self.vault_root else (Path("data") / "documents")
            storage_dir.mkdir(parents=True, exist_ok=True)

            ingest_pdf(
                tmp_path,
                db_path=self.db_path,
                storage_dir=storage_dir,
                category="manual_upload",
                tags="uploaded",
            )

            self.send_response(303)
            self.send_header("Location", "/?level=success&msg=Ingestion%20successful")
            self.end_headers()

        except Exception as e:
    # Redirect back to dashboard with an error message
            msg = quote(f"Ingestion failed: {e}")
            self.send_response(303)
            self.send_header("Location", f"/?level=error&msg={msg}")
            self.end_headers()

        finally:
            if tmp_path is not None:
                tmp_path.unlink(missing_ok=True)

    # Keep the console clean
    def log_message(self, format: str, *args) -> None:
        return


def make_server(host: str, port: int, *, db_path: Path, vault_root: Path | None = None) -> ThreadingHTTPServer:
    PerDocManHandler.db_path = db_path
    PerDocManHandler.vault_root = vault_root
    return ThreadingHTTPServer((host, port), PerDocManHandler)
