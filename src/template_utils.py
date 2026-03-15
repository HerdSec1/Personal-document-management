from pathlib import Path


def html_escape(value: object) -> str:
    """
    Escape text for safe HTML rendering.
    """
    text = "" if value is None else str(value)

    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def load_template(name: str) -> str:
    """
    Load a template file from the templates directory.
    """
    template_path = Path("templates") / name

    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()


def render_template(template_name: str, replacements: dict[str, str]) -> str:
    """
    Render a template by replacing {{tokens}} with values.
    """
    html = load_template(template_name)

    for key, value in replacements.items():
        html = html.replace(f"{{{{{key}}}}}", str(value))

    return html


def send_html(handler, html: str, status: int = 200) -> None:
    """
    Send HTML through the HTTP handler.
    """
    body = html.encode("utf-8")

    handler.send_response(status)
    handler.send_header("Content-Type", "text/html; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()

    handler.wfile.write(body)


def render_page(handler, template_name: str, replacements: dict[str, str], status: int = 200) -> None:
    """
    Render and send a template in one step.
    """
    html = render_template(template_name, replacements)
    send_html(handler, html, status)