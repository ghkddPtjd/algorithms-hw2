import http.client
import threading
import unittest
from urllib.parse import urlencode

from src.server import create_server
from src.shortener import URLShortener


class ServerTests(unittest.TestCase):
    def setUp(self):
        self.server = create_server(0, URLShortener())
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.port = self.server.server_address[1]

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()

    def request(self, method, path, body=None, headers=None):
        connection = http.client.HTTPConnection("127.0.0.1", self.port)
        connection.request(method, path, body=body, headers=headers or {})
        response = connection.getresponse()
        content = response.read().decode("utf-8")
        result = response.status, response.getheaders(), content
        connection.close()
        return result

    def test_home_form_and_shortening_result(self):
        status, _, page = self.request("GET", "/")
        self.assertEqual(status, 200)
        self.assertIn('<form method="post"', page)

        status, _, page = self.request(
            "POST",
            "/",
            urlencode({"url": "https://example.com/a"}),
            {"Content-Type": "application/x-www-form-urlencoded"},
        )
        self.assertEqual(status, 200)
        self.assertIn("/s/0", page)

    def test_redirect_and_not_found(self):
        self.request(
            "POST",
            "/",
            urlencode({"url": "https://example.com/path"}),
            {"Content-Type": "application/x-www-form-urlencoded"},
        )
        status, headers, _ = self.request("GET", "/s/0")
        self.assertEqual(status, 302)
        self.assertEqual(dict(headers)["Location"], "https://example.com/path")
        status, _, _ = self.request("GET", "/s/missing")
        self.assertEqual(status, 404)

    def test_invalid_url_and_table_diagnostics(self):
        status, _, page = self.request(
            "POST",
            "/",
            urlencode({"url": "not a url"}),
            {"Content-Type": "application/x-www-form-urlencoded"},
        )
        self.assertEqual(status, 400)
        self.assertIn("Invalid URL", page)

        self.request(
            "POST",
            "/",
            urlencode({"url": "https://example.com"}),
            {"Content-Type": "application/x-www-form-urlencoded"},
        )
        status, _, page = self.request("GET", "/table")
        self.assertEqual(status, 200)
        self.assertIn("Horner:", page)
        self.assertIn("count=1", page)
        self.assertIn("https://example.com", page)

    def test_linear_table_can_be_selected_and_inspected(self):
        status, _, page = self.request("GET", "/?table=linear")
        self.assertEqual(status, 200)
        self.assertIn('value="linear" selected', page)

        status, _, page = self.request(
            "POST",
            "/",
            urlencode({"url": "https://linear.example", "table": "linear"}),
            {"Content-Type": "application/x-www-form-urlencoded"},
        )
        self.assertEqual(status, 200)
        self.assertIn("/s/0?table=linear", page)

        status, _, page = self.request("GET", "/table?table=linear")
        self.assertEqual(status, 200)
        self.assertIn("Linear table internals", page)
        self.assertIn("Inspected cells=", page)
        self.assertIn("Horner:", page)

        status, headers, _ = self.request("GET", "/s/0?table=linear")
        self.assertEqual(status, 302)
        self.assertEqual(dict(headers)["Location"], "https://linear.example")


if __name__ == "__main__":
    unittest.main()
