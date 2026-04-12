from __future__ import annotations

import cgi
import shutil
import sqlite3
import tempfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, quote, urlparse

from src.template_utils import (
    html_escape,
    load_template,
    render_page,
    send_html,
)
from src.db import (
    get_doc_count,
    init_db,
    list_documents,
    list_expiring_documents,
    search_documents,
    sensitivity_counts,
)
from src.ingest import ingest_pdf
from src.reset_db import reset_database


class PerDocManHandler(BaseHTTPRequestHandler):
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

        if parsed.path == "/search":
            self.handle_search(parsed.query)
            return

        if parsed.path == "/doc":
            self.handle_doc(parsed.query)
            return

        if parsed.path == "/doc_raw":
            self.handle_doc_raw(parsed.query)
            return

        self.render_error("Not Found", "The requested page could not be found.", status=404)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)

        if parsed.path == "/ingest":
            self.handle_ingest()
            return

        if parsed.path == "/reset":
            self.handle_reset()
            return

        self.render_error("Not Found", "The requested page could not be found.", status=404)

    def render_error(self, title: str, message: str, status: int = 400) -> None:
        render_page(
            self,
            "error.html",
            {
                "title": html_escape(title),
                "message": html_escape(message),
            },
            status=status,
        )

    def handle_reset(self) -> None:
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
        level = params.get("level", ["info"])[0]

        sens_counts = sensitivity_counts(self.db_path)

        stats = {
            "low": 0,
            "moderate": 0,
            "high": 0,
            "critical": 0,
        }

        for (sens, n) in sens_counts:
            key = (sens or "").lower()
            if key in stats:
                stats[key] = n

        stats_html = (
            "<div class='row g-2'>"
            f"<div class='col-6'><div class='border rounded p-2'><div class='text-muted small'>Total</div><div class='fw-semibold'>{count}</div></div></div>"
            f"<div class='col-6'><div class='border rounded p-2'><div class='text-muted small'>Low</div><div class='fw-semibold'>{stats['low']}</div></div></div>"
            f"<div class='col-6'><div class='border rounded p-2'><div class='text-muted small'>Moderate</div><div class='fw-semibold'>{stats['moderate']}</div></div></div>"
            f"<div class='col-6'><div class='border rounded p-2'><div class='text-muted small'>High</div><div class='fw-semibold'>{stats['high']}</div></div></div>"
            f"<div class='col-12'><div class='border rounded p-2'><div class='text-muted small'>Critical</div><div class='fw-semibold'>{stats['critical']}</div></div></div>"
            "</div>"
        )

        expiring = list_expiring_documents(self.db_path, days=365, limit=10)
        exp_trs: list[str] = []
        for (doc_id, display_title, sensitivity, expires_at) in expiring:
            exp_trs.append(
                "<tr>"
                f"<td>{doc_id}</td>"
                f"<td>{html_escape(display_title)}</td>"
                f"<td>{html_escape(sensitivity or '')}</td>"
                f"<td>{html_escape(expires_at or '')}</td>"
                f"<td><a class='btn btn-sm btn-outline-primary' href='/doc?id={doc_id}' target='_blank'>Open</a></td>"
                "</tr>"
            )

        exp_table = (
            "<table class='table table-striped table-hover align-middle'>"
            "<thead><tr><th>ID</th><th>Filename</th><th>Sensitivity</th><th>Expires</th><th>Preview</th></tr></thead>"
            "<tbody>"
            + ("".join(exp_trs) if exp_trs else "<tr><td colspan='5'>(no expiring documents)</td></tr>")
            + "</tbody></table>"
        )

        sens_items: list[str] = []
        for (sens, n) in sens_counts:
            raw_sens = (sens or "").lower()
            badge_class = {
                "low": "success",
                "moderate": "warning",
                "high": "danger",
                "critical": "dark",
                "unspecified": "secondary",
            }.get(raw_sens, "secondary")

            badge_extra = " text-dark" if raw_sens == "moderate" else ""

            sens_items.append(
                "<div class='d-flex justify-content-between align-items-center border rounded p-2 mb-2'>"
                f"<span class='badge bg-{badge_class}{badge_extra}'>{html_escape(sens)}</span>"
                f"<strong>{n}</strong>"
                "</div>"
            )

        sens_html = "".join(sens_items) if sens_items else "<p class='text-muted mb-0'>(no documents yet)</p>"

        banner = ""
        if msg:
            alert_class = "success" if level == "success" else "danger" if level == "error" else "primary"
            banner = (
                f'<div class="alert alert-{alert_class}" role="alert">'
                f"<strong>{html_escape(level).upper()}:</strong> {html_escape(msg)}"
                f"</div>"
            )

        template = load_template("dashboard.html")
        html = (
            template
            .replace("{{banner}}", banner)
            .replace("{{count}}", str(count))
            .replace("{{stats_html}}", stats_html)
            .replace("{{sens_html}}", sens_html)
            .replace("{{exp_table}}", exp_table)
        )

        send_html(self, html)

    def handle_search(self, query: str) -> None:
        params = parse_qs(query)
        q = params.get("q", [""])[0].strip()
        sens = params.get("sensitivity", [""])[0].strip().lower()

        rows = search_documents(self.db_path, q, limit=200) if q else list_documents(self.db_path, limit=200)

        trs: list[str] = []
        for (doc_id, display_title, category, tags, doc_date, ingested_at, stored_path, sha256) in rows:
            if sens:
                conn = sqlite3.connect(self.db_path)
                try:
                    cur = conn.cursor()
                    cur.execute("SELECT sensitivity FROM documents WHERE id = ?", (doc_id,))
                    r = cur.fetchone()
                finally:
                    conn.close()

                doc_sens = (r[0] or "").lower() if r else ""
                tiers = ["low", "moderate", "high", "critical"]

                if doc_sens not in tiers or tiers.index(doc_sens) < tiers.index(sens):
                    continue

            trs.append(
                "<tr>"
                f"<td>{doc_id}</td>"
                f"<td>{html_escape(display_title)}</td>"
                f"<td>{html_escape(category)}</td>"
                f"<td>{html_escape(tags)}</td>"
                f"<td>{html_escape(doc_date)}</td>"
                f"<td>{html_escape(ingested_at)}</td>"
                f"<td><a class='btn btn-sm btn-outline-primary' href='/doc?id={doc_id}' target='_blank'>Open</a></td>"
                "</tr>"
            )

        result_count = len(trs)

        if q and sens:
            results_summary = f'Showing {result_count} result(s) for "{html_escape(q)}" with sensitivity filter "{html_escape(sens)}".'
        elif q:
            results_summary = f'Showing {result_count} result(s) for "{html_escape(q)}".'
        elif sens:
            results_summary = f'Showing {result_count} result(s) with sensitivity filter "{html_escape(sens)}".'
        else:
            results_summary = f"Showing {result_count} document(s)."

        results_table = (
            "<table class='table table-striped table-hover align-middle'>"
            "<thead><tr>"
            "<th>ID</th><th>Filename</th><th>Category</th><th>Tags</th><th>Doc Date</th><th>Ingested</th><th>Preview</th>"
            "</tr></thead><tbody>"
            + ("".join(trs) if trs else "<tr><td colspan='7'>(no matching documents)</td></tr>")
            + "</tbody></table>"
        )

        template = load_template("search.html")
        html = (
            template
            .replace("{{query}}", html_escape(q))
            .replace("{{results_summary}}", results_summary)
            .replace("{{results_table}}", results_table)
            .replace("{{low_selected}}", "selected" if sens == "low" else "")
            .replace("{{moderate_selected}}", "selected" if sens == "moderate" else "")
            .replace("{{high_selected}}", "selected" if sens == "high" else "")
            .replace("{{critical_selected}}", "selected" if sens == "critical" else "")
        )

        send_html(self, html)

    def handle_documents(self) -> None:
        rows = list_documents(self.db_path, limit=50)

        trs: list[str] = []
        for (doc_id, display_title, category, tags, doc_date, ingested_at, stored_path, sha256) in rows:
            trs.append(
                "<tr>"
                f"<td>{doc_id}</td>"
                f"<td>{html_escape(display_title)}</td>"
                f"<td>{html_escape(category)}</td>"
                f"<td>{html_escape(tags)}</td>"
                f"<td>{html_escape(doc_date)}</td>"
                f"<td>{html_escape(ingested_at)}</td>"
                f"<td><a class='btn btn-sm btn-outline-primary' href='/doc?id={doc_id}' target='_blank'>Open</a></td>"
                "</tr>"
            )

        documents_table = (
            "<table class='table table-striped table-hover align-middle'>"
            "<thead><tr>"
            "<th>ID</th><th>Filename</th><th>Category</th><th>Tags</th><th>Doc Date</th><th>Ingested At</th><th>Preview</th>"
            "</tr></thead>"
            "<tbody>"
            + ("".join(trs) if trs else "<tr><td colspan='7'>(no documents yet)</td></tr>")
            + "</tbody></table>"
        )

        template = load_template("documents.html")
        html = (
            template
            .replace("{{banner}}", "")
            .replace("{{documents_table}}", documents_table)
        )

        send_html(self, html)

    def handle_doc(self, query: str) -> None:
        params = parse_qs(query)
        doc_id_str = params.get("id", [""])[0]

        if not doc_id_str.isdigit():
            self.render_error("Invalid Document ID", "The document id must be a number.", status=400)
            return

        doc_id = int(doc_id_str)

        conn = sqlite3.connect(self.db_path)
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT stored_path, original_filename, sensitivity FROM documents WHERE id = ?",
                (doc_id,),
            )
            row = cur.fetchone()
        finally:
            conn.close()

        if not row:
            self.render_error("Document Not Found", "No document exists with that id.", status=404)
            return

        stored_path, original_filename, sensitivity = row
        path = Path(stored_path)

        if not path.exists():
            self.render_error("File Missing", "The document record exists, but the file is missing on disk.", status=404)
            return

        if (sensitivity or "").lower() in {"high", "critical"}:
            render_page(
                self,
                "sensitivity_warning.html",
                {
                    "sensitivity": html_escape(sensitivity),
                    "filename": html_escape(original_filename),
                    "doc_id": str(doc_id),
                },
            )
            return

        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "application/pdf")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Content-Disposition", f'inline; filename="{original_filename}"')
        self.end_headers()
        self.wfile.write(data)

    def handle_doc_raw(self, query: str) -> None:
        params = parse_qs(query)
        doc_id_str = params.get("id", [""])[0]

        if not doc_id_str.isdigit():
            self.render_error("Invalid Document ID", "The document id must be a number.", status=400)
            return

        doc_id = int(doc_id_str)

        conn = sqlite3.connect(self.db_path)
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT stored_path, original_filename FROM documents WHERE id = ?",
                (doc_id,),
            )
            row = cur.fetchone()
        finally:
            conn.close()

        if not row:
            self.render_error("Document Not Found", "No document exists with that id.", status=404)
            return

        stored_path, original_filename = row
        path = Path(stored_path)

        if not path.exists():
            self.render_error("File Missing", "The document record exists, but the file is missing on disk.", status=404)
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
            self.render_error("Upload Error", "Missing form field: file", status=400)
            return

        file_item = form["file"]
        filename = getattr(file_item, "filename", None)
        if not filename:
            self.render_error("Upload Error", "No file selected.", status=400)
            return

        sensitivity = form.getfirst("sensitivity")
        expires_at = form.getfirst("expires_at")

        tmp_path: Path | None = None
        tmpdir: str | None = None

        try:
            tmpdir = tempfile.mkdtemp()
            safe_name = Path(filename).name
            tmp_path = Path(tmpdir) / safe_name

            with open(tmp_path, "wb") as tmp:
                shutil.copyfileobj(file_item.file, tmp)

            storage_dir = (self.vault_root / "documents") if self.vault_root else (Path("data") / "documents")
            storage_dir.mkdir(parents=True, exist_ok=True)

            doc_id = ingest_pdf(
                tmp_path,
                original_filename=filename,
                db_path=self.db_path,
                storage_dir=storage_dir,
                category="manual_upload",
                tags="uploaded",
                sensitivity=sensitivity,
                expires_at=expires_at,
            )

            msg = quote(f'Imported "{filename}" successfully (ID {doc_id})')

            self.send_response(303)
            self.send_header("Location", f"/?level=success&msg={msg}")
            self.end_headers()

        except Exception as e:
            msg = quote(f"Ingestion failed: {e}")
            self.send_response(303)
            self.send_header("Location", f"/?level=error&msg={msg}")
            self.end_headers()

        finally:
            if tmp_path is not None:
                tmp_path.unlink(missing_ok=True)
            if tmpdir is not None:
                shutil.rmtree(tmpdir, ignore_errors=True)

    def log_message(self, format: str, *args) -> None:
        return


def make_server(host: str, port: int, *, db_path: Path, vault_root: Path | None = None) -> ThreadingHTTPServer:
    PerDocManHandler.db_path = db_path
    PerDocManHandler.vault_root = vault_root
    return ThreadingHTTPServer((host, port), PerDocManHandler)