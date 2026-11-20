import json
import threading
import unittest
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import (
    HTTPRedirectHandler,
    Request,
    build_opener,
    urlopen,
)

from src.server import create_server
from src.shortener import URLShortener, encode_base62


class ServerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.server = create_server("127.0.0.1", 0)
        self.thread = threading.Thread(target=self.server.serve_forever)
        self.thread.start()
        self.base_url = f"http://127.0.0.1:{self.server.server_port}"

    def tearDown(self) -> None:
        self.server.shutdown()
        self.thread.join()
        self.server.server_close()

    def test_home_page_reports_server_is_running(self) -> None:
        with urlopen(self.base_url) as response:
            self.assertEqual(response.status, 200)
            page = response.read().decode("utf-8")
            self.assertIn("<form", page)
            self.assertIn('action="/shorten"', page)

    def test_health_endpoint_returns_ok(self) -> None:
        with urlopen(f"{self.base_url}/health") as response:
            self.assertEqual(response.status, 200)
            self.assertEqual(json.load(response), {"status": "ok"})

    def test_api_shortens_and_redirects_to_original_url(self) -> None:
        original_url = "https://example.com/path?q=one"
        request = Request(
            f"{self.base_url}/shorten",
            data=json.dumps({"url": original_url}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(request) as response:
            self.assertEqual(response.status, 201)
            result = json.load(response)

        self.assertEqual(result["short_url"], f"{self.base_url}/{result['code']}")
        opener = build_opener(HTTPRedirectHandlerWithoutFollowing())
        with self.assertRaises(HTTPError) as error:
            opener.open(f"{self.base_url}/{result['code']}")
        self.assertEqual(error.exception.code, 302)
        self.assertEqual(error.exception.headers["Location"], original_url)

    def test_html_form_creates_clickable_short_link(self) -> None:
        body = urlencode({"url": "https://example.com"}).encode("utf-8")
        request = Request(
            f"{self.base_url}/shorten",
            data=body,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )
        with urlopen(request) as response:
            page = response.read().decode("utf-8")

        self.assertEqual(response.status, 201)
        self.assertIn(f'href="/1"', page)

    def test_invalid_url_returns_bad_request(self) -> None:
        request = Request(
            f"{self.base_url}/shorten",
            data=json.dumps({"url": "not a URL"}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with self.assertRaises(HTTPError) as error:
            urlopen(request)
        self.assertEqual(error.exception.code, 400)

    def test_unknown_path_returns_not_found(self) -> None:
        with self.assertRaises(HTTPError) as error:
            urlopen(f"{self.base_url}/missing")

        self.assertEqual(error.exception.code, 404)
        self.assertEqual(json.load(error.exception), {"error": "not found"})


class Base62Tests(unittest.TestCase):
    def test_base62_encodes_zero_and_rolls_over(self) -> None:
        self.assertEqual(encode_base62(0), "0")
        self.assertEqual(encode_base62(61), "Z")
        self.assertEqual(encode_base62(62), "10")

    def test_base62_rejects_negative_values(self) -> None:
        with self.assertRaises(ValueError):
            encode_base62(-1)

    def test_shortener_deduplicates_urls_and_rejects_invalid_urls(self) -> None:
        shortener = URLShortener()
        code = shortener.shorten("https://example.com")

        self.assertEqual(shortener.shorten("https://example.com"), code)
        self.assertEqual(shortener.expand(code), "https://example.com")
        self.assertIsNone(shortener.expand("missing"))
        with self.assertRaises(ValueError):
            shortener.shorten("http://[invalid")


class HTTPRedirectHandlerWithoutFollowing(HTTPRedirectHandler):
    def redirect_request(self, request, response, code, message, headers, new_url):
        return None


if __name__ == "__main__":
    unittest.main()
