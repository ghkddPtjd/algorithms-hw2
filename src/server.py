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

from src.shortener import URLShortener


def _page(content: str) -> bytes:
    document = (
        "<!doctype html><html lang=\"ko\"><meta charset=\"utf-8\">"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
        "<title>URL Shortener</title><body>"
        "<nav><a href=\"/\">Shorten</a> · <a href=\"/table\">Hash table</a></nav>"
        f"{content}</body></html>"
    )
    return document.encode("utf-8")


class URLShortenerHandler(BaseHTTPRequestHandler):
    shortener = URLShortener()

    def do_GET(self) -> None:
        if self.path == "/":
            self._send_html(
                200,
                "<h1>URL Shortener</h1>"
                "<form method=\"post\" action=\"/\">"
                "<label>URL <input name=\"url\" type=\"url\" required></label>"
                "<button type=\"submit\">Shorten</button></form>",
            )
            return
        if self.path == "/table":
            self._send_html(200, self._table_html())
            return
        if self.path.startswith("/s/"):
            code = unquote(self.path[len("/s/") :])
            if not code or "/" in code:
                self.send_error(404, "Short code not found")
                return
            try:
                url = self.shortener.expand(code)
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
        for key, value in parse_qsl(raw_body, keep_blank_values=True):
            if key == "url":
                url = value
                break
        try:
            code = self.shortener.shorten(url)
        except (TypeError, ValueError) as error:
            self._send_html(
                400,
                f"<h1>Invalid URL</h1><p>{escape(str(error))}</p><p><a href=\"/\">Try again</a></p>",
            )
            return

        short_url = f"{self.server_url()}/s/{escape(code)}"
        self._send_html(
            200,
            "<h1>Short URL created</h1>"
            f"<p><a href=\"{short_url}\">{short_url}</a></p>"
            f"<p>Original: {escape(url)}</p>",
        )

    def _table_html(self) -> str:
        table = self.shortener.table
        rows = []
        for index in range(table.capacity):
            entries = table.bucket_entries(index)
            if not entries:
                continue
            details = []
            for position, (key, value) in enumerate(entries, start=1):
                bucket, steps = table.hash_calculation(key)
                calculation = "h=0"
                for character, codepoint, previous, current in steps:
                    calculation += f"; (31×{previous}+{codepoint}) mod {table.capacity}={current}"
                details.append(
                    "<li>"
                    f"key=<code>{escape(key)}</code>, code=<code>{escape(str(value))}</code>, "
                    f"bucket={bucket}, compared nodes={position}<br>"
                    f"<small>Horner: {escape(calculation)}</small>"
                    "</li>"
                )
            rows.append(
                f"<section><h2>Bucket {index}</h2><ol>{''.join(details)}</ol></section>"
            )
        if not rows:
            rows.append("<p>The table is empty.</p>")
        return "<h1>Hash table internals</h1>" + "".join(rows)

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
    handler = type(
        "ConfiguredURLShortenerHandler",
        (URLShortenerHandler,),
        {"shortener": shortener or URLShortener()},
    )
    return ThreadingHTTPServer(("", port), handler)


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
