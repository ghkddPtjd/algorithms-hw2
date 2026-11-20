#!/usr/bin/env python3
"""HTTP interface for the URL shortener."""

import argparse
import html
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

if __package__:
    from .shortener import URLShortener
else:
    from shortener import URLShortener


class RequestHandler(BaseHTTPRequestHandler):
    server: "ShortenerHTTPServer"
    max_request_bytes = 16_384

    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, status: int, payload: dict[str, str]) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self._send(status, body, "application/json; charset=utf-8")

    def _wants_json(self) -> bool:
        return self.headers.get("Content-Type", "").split(";", 1)[0].strip() == "application/json"

    def _error(self, status: int, message: str, as_json: bool) -> None:
        if as_json:
            self._send_json(status, {"error": message})
            return
        body = (
            "<!doctype html><html lang=\"ko\"><meta charset=\"utf-8\">"
            f"<title>오류</title><p>{html.escape(message)}</p>"
            "<p><a href=\"/\">돌아가기</a></p></html>"
        ).encode("utf-8")
        self._send(status, body, "text/html; charset=utf-8")

    def do_GET(self) -> None:
        if self.path == "/":
            body = (
                "<!doctype html><html lang=\"ko\"><meta charset=\"utf-8\">"
                "<title>URL 단축기</title><h1>URL 단축기</h1>"
                "<form method=\"post\" action=\"/shorten\">"
                "<label for=\"url\">긴 URL</label> "
                "<input id=\"url\" name=\"url\" type=\"url\" required "
                "placeholder=\"https://example.com\"> "
                "<button type=\"submit\">단축하기</button></form>"
                "<p><a href=\"/health\">상태 확인</a></p></html>"
            ).encode("utf-8")
            self._send(200, body, "text/html; charset=utf-8")
            return

        if self.path == "/health":
            self._send_json(200, {"status": "ok"})
            return

        code = self.path.removeprefix("/")
        if code and "/" not in code and "?" not in code and "#" not in code:
            url = self.server.shortener.expand(code)
            if url is not None:
                self.send_response(302)
                self.send_header("Location", url)
                self.send_header("Content-Length", "0")
                self.end_headers()
                return

        self._send_json(404, {"error": "not found"})

    def do_POST(self) -> None:
        if self.path != "/shorten":
            self._send_json(404, {"error": "not found"})
            return

        as_json = self._wants_json()
        try:
            content_length = int(self.headers.get("Content-Length", ""))
        except ValueError:
            self._error(400, "A valid Content-Length header is required.", as_json)
            return
        if content_length < 0:
            self._error(400, "Content-Length cannot be negative.", as_json)
            return
        if content_length > self.max_request_bytes:
            self._error(413, "Request body is too large.", as_json)
            return

        body = self.rfile.read(content_length)
        content_type = self.headers.get("Content-Type", "").split(";", 1)[0].strip()
        try:
            if content_type == "application/json":
                data = json.loads(body)
                url = data.get("url") if isinstance(data, dict) else None
            elif content_type == "application/x-www-form-urlencoded":
                fields = parse_qs(body.decode("utf-8"), strict_parsing=False)
                url = fields.get("url", [None])[0]
            else:
                self._error(
                    415,
                    "Use application/json or application/x-www-form-urlencoded.",
                    as_json,
                )
                return
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._error(400, "Request body is not valid JSON or UTF-8 form data.", as_json)
            return

        try:
            code = self.server.shortener.shorten(url)
        except (ValueError, TypeError) as error:
            self._error(400, str(error), as_json)
            return

        short_url = self._public_url(code)
        if as_json:
            self._send_json(201, {"code": code, "short_url": short_url})
            return

        body = (
            "<!doctype html><html lang=\"ko\"><meta charset=\"utf-8\">"
            "<title>단축 URL</title><h1>단축 URL</h1><p>"
            f"<a href=\"{html.escape('/' + code, quote=True)}\">"
            f"{html.escape(short_url)}</a></p><p><a href=\"/\">새 URL 단축하기</a></p></html>"
        ).encode("utf-8")
        self._send(201, body, "text/html; charset=utf-8")

    def _public_url(self, code: str) -> str:
        host_header = self.headers.get("Host", "")
        parsed_host = urlsplit(f"//{host_header}")
        if not parsed_host.hostname or parsed_host.path or parsed_host.query or parsed_host.fragment:
            return f"/{code}"
        scheme = self.headers.get("X-Forwarded-Proto", "http").split(",", 1)[0].strip()
        if scheme not in ("http", "https"):
            scheme = "http"
        return f"{scheme}://{parsed_host.netloc}/{code}"


class ShortenerHTTPServer(ThreadingHTTPServer):
    def __init__(self, address: tuple[str, int]) -> None:
        self.shortener = URLShortener()
        super().__init__(address, RequestHandler)


def create_server(host: str, port: int) -> ShortenerHTTPServer:
    return ShortenerHTTPServer((host, port))


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the URL shortener web server.")
    parser.add_argument("--host", default="0.0.0.0", help="interface to listen on")
    parser.add_argument("--port", type=int, default=8000, help="port to listen on")
    args = parser.parse_args()

    with create_server(args.host, args.port) as server:
        print(f"Serving on http://{args.host}:{args.port}", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.", flush=True)


if __name__ == "__main__":
    main()
