#!/usr/bin/env python3
"""Minimal HTTP entry point for the URL shortener project."""

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == "/":
            body = (
                "<!doctype html><html lang=\"ko\"><meta charset=\"utf-8\">"
                "<title>URL 단축기</title><h1>서버가 실행 중입니다</h1>"
                "<p>URL 단축기 기능은 아직 구현되지 않았습니다.</p>"
                "<p><a href=\"/health\">상태 확인</a></p></html>"
            ).encode("utf-8")
            content_type = "text/html; charset=utf-8"
            status = 200
        elif self.path == "/health":
            body = json.dumps({"status": "ok"}).encode("utf-8")
            content_type = "application/json; charset=utf-8"
            status = 200
        else:
            body = json.dumps({"error": "not found"}).encode("utf-8")
            content_type = "application/json; charset=utf-8"
            status = 404

        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def create_server(host: str, port: int) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), RequestHandler)


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
