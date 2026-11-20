"""Standard-library HTTP interface for the URL shortener."""

import argparse
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import os
from pathlib import Path
import sys
from urllib.parse import parse_qsl, unquote


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.linear_probing import LinearProbingHashTable
from src.shortener import URLShortener


def _page(content: str) -> bytes:
    document = (
        "<!doctype html><html lang=\"ko\"><meta charset=\"utf-8\">"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
        "<title>URL Shortener</title><style>"
        "body{font-family:sans-serif;line-height:1.5;margin:2rem auto;max-width:72rem;padding:0 1rem}"
        "nav{margin-bottom:1.5rem}.table-grid{display:grid;gap:1rem;"
        "grid-template-columns:repeat(auto-fit,minmax(18rem,1fr))}"
        ".bucket{border:1px solid #bbb;border-radius:.5rem;padding:1rem;min-width:0}"
        ".bucket h2{margin-top:0}.chain{align-items:stretch;display:flex;gap:.75rem;"
        "overflow-x:auto;padding:.25rem}.node{border:1px solid #ddd;border-radius:.4rem;"
        "flex:0 0 17rem;padding:.75rem;overflow-wrap:anywhere}"
        ".chain-arrow{align-self:center;font-size:1.5rem}.empty{color:#666;font-style:italic}"
        ".horner-details{margin-top:.75rem}.horner-details ol{padding-left:1.5rem}"
        "</style><body>"
        "<nav><a href=\"/\">Shorten</a> · <a href=\"/table\">Hash table</a></nav>"
        f"<main>{content}</main></body></html>"
    )
    return document.encode("utf-8")


class URLShortenerHandler(BaseHTTPRequestHandler):
    shorteners = (
        ("chaining", URLShortener()),
        ("linear", URLShortener(table_class=LinearProbingHashTable)),
    )

    def do_GET(self) -> None:
        path, _, query = self.path.partition("?")
        table_name = "chaining"
        for key, value in parse_qsl(query, keep_blank_values=True):
            if key == "table":
                table_name = value
        shortener = self._get_shortener(table_name)
        if shortener is None:
            self.send_error(400, "Unknown table implementation")
            return

        if path == "/":
            chaining_selected = ' selected' if table_name == "chaining" else ""
            linear_selected = ' selected' if table_name == "linear" else ""
            self._send_html(
                200,
                "<h1>URL Shortener</h1>"
                "<form method=\"post\" action=\"/\">"
                "<label>URL <input name=\"url\" type=\"url\" required></label>"
                "<label>Table <select name=\"table\">"
                f'<option value="chaining"{chaining_selected}>Chaining</option>'
                f'<option value="linear"{linear_selected}>Linear probing</option>'
                "</select></label>"
                "<button type=\"submit\">Shorten</button></form>",
            )
            return
        if path == "/table":
            self._send_html(200, self._table_html(shortener, table_name))
            return
        if path.startswith("/s/"):
            code = unquote(path[len("/s/") :])
            if not code or "/" in code:
                self.send_error(404, "Short code not found")
                return
            try:
                url = shortener.expand(code)
            except KeyError:
                self.send_error(404, "Short code not found")
                return
            self.send_response(302)
            self.send_header("Location", url)
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        self.send_error(404, "Page not found")

    def do_POST(self) -> None:
        if self.path != "/":
            self.send_error(404, "Page not found")
            return
        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length).decode("utf-8")
        url = ""
        table_name = "chaining"
        for key, value in parse_qsl(raw_body, keep_blank_values=True):
            if key == "url":
                url = value
            elif key == "table":
                table_name = value
        shortener = self._get_shortener(table_name)
        if shortener is None:
            self._send_html(400, "<h1>Unknown table implementation</h1>")
            return
        try:
            code = shortener.shorten(url)
        except (TypeError, ValueError) as error:
            self._send_html(
                400,
                f"<h1>Invalid URL</h1><p>{escape(str(error))}</p><p><a href=\"/\">Try again</a></p>",
            )
            return

        table_query = "?table=linear" if table_name == "linear" else ""
        short_url = f"{self.server_url()}/s/{escape(code)}{table_query}"
        self._send_html(
            200,
            "<h1>Short URL created</h1>"
            f"<p>Table: {escape(table_name)}</p>"
            f"<p><a href=\"{short_url}\">{short_url}</a></p>"
            f"<p>Original: {escape(url)}</p>",
        )

    def _table_html(self, shortener: URLShortener, table_name: str) -> str:
        table = shortener.table
        rows = []
        table_query = "?table=linear" if table_name == "linear" else ""
        cell_name = "Slot" if table_name == "linear" else "Bucket"
        for index in range(table.capacity):
            entries = table.bucket_entries(index)
            nodes = []
            for node_index, (key, value) in enumerate(entries):
                if node_index:
                    nodes.append(
                        '<span class="chain-arrow" aria-hidden="true">→</span>'
                    )
                bucket, steps = table.hash_calculation(key)
                code = str(value)
                step_details = []
                for character, codepoint, previous, current in steps:
                    step_details.append(
                        "<li>"
                        f"<code>{escape(character)}</code> (U+{codepoint:04X}): "
                        f"({previous} × 31 + {codepoint}) mod {table.capacity} = {current}"
                        "</li>"
                    )
                trace = table.lookup_trace(key)
                inspected = " → ".join(str(cell) for cell in trace)
                inspection_label = (
                    "Inspected cells" if table_name == "linear" else "Inspected bucket nodes"
                )
                short_link = (
                    f"{self.server_url()}/s/{escape(code)}{table_query}"
                )
                nodes.append(
                    '<article class="node">'
                    f"<p><strong>URL key</strong><br><code>{escape(key)}</code></p>"
                    f"<p><strong>Short code</strong><br><code>{escape(code)}</code></p>"
                    f"<p><strong>Short link</strong><br><a href=\"{short_link}\">"
                    f"{short_link}</a></p>"
                    f"<p>Home bucket: {bucket}; {inspection_label}="
                    f"{escape(inspected)} (count={len(trace)})</p>"
                    '<details class="horner-details">'
                    "<summary>Horner: hash calculation</summary>"
                    f"<p>Start with h = 0; final bucket: {bucket}.</p>"
                    f"<ol>{''.join(step_details)}</ol>"
                    "</details></article>"
                )
            chain_content = "".join(nodes) if nodes else '<p class="empty">Empty</p>'
            rows.append(
                f'<section class="bucket" data-index="{index}">'
                f"<h2>{cell_name} {index}</h2>"
                f'<div class="chain" aria-label="{cell_name} {index} chain">'
                f"{chain_content}</div></section>"
            )
        return (
            f"<h1>{escape(table_name.title())} table internals</h1>"
            f"<p>Capacity: {table.capacity}; entries: {len(table)}.</p>"
            f'<div class="table-grid">{"".join(rows)}</div>'
        )

    def _get_shortener(self, table_name: str) -> URLShortener | None:
        for name, shortener in self.shorteners:
            if name == table_name:
                return shortener
        return None

    def server_url(self) -> str:
        host = self.headers.get("Host", "localhost")
        return f"http://{escape(host)}"

    def _send_html(self, status: int, content: str) -> None:
        body = _page(content)
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        print(f"{self.address_string()} - {format % args}")


def create_server(port: int = 8000, shortener: URLShortener | None = None) -> ThreadingHTTPServer:
    chaining_shortener = shortener if shortener is not None else URLShortener()

    class ConfiguredURLShortenerHandler(URLShortenerHandler):
        shorteners = (
            ("chaining", chaining_shortener),
            ("linear", URLShortener(table_class=LinearProbingHashTable)),
        )

    return ThreadingHTTPServer(("", port), ConfiguredURLShortenerHandler)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the URL shortener web server.")
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", "8000")))
    args = parser.parse_args()
    server = create_server(args.port)
    print(f"Serving on http://0.0.0.0:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
