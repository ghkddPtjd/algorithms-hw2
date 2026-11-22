import http.client
import threading
import unittest
from urllib.parse import urlencode

from src.server import _codespaces_public_base_url, create_server
from src.shortener import URLShortener


class ServerTests(unittest.TestCase):
    def setUp(self):
        self.shortener = URLShortener()
        self.server = create_server(0, self.shortener)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.port = self.server.server_address[1]

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()

    def request(self, method, path, body=None, headers=None, server=None):
        target_server = server if server is not None else self.server
        connection = http.client.HTTPConnection(
            "127.0.0.1", target_server.server_address[1]
        )
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
        self.assertIn(f"http://127.0.0.1:{self.port}/0/", page)
        self.assertIn('href="/0/"', page)
        self.assertIn("Short link", page)

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

    def test_root_short_code_path_redirects(self):
        self.request(
            "POST",
            "/",
            urlencode({"url": "https://example.com/root-route"}),
            {"Content-Type": "application/x-www-form-urlencoded"},
        )

        status, headers, _ = self.request("GET", "/0/")

        self.assertEqual(status, 302)
        self.assertEqual(dict(headers)["Location"], "https://example.com/root-route")

    def test_public_base_url_is_used_for_shareable_links(self):
        server = create_server(0, public_base_url="http://s")
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            status, _, page = self.request(
                "POST",
                "/",
                urlencode({"url": "https://example.com/public"}),
                {"Content-Type": "application/x-www-form-urlencoded"},
                server=server,
            )
        finally:
            server.shutdown()
            server.server_close()
            thread.join()

        self.assertEqual(status, 200)
        self.assertIn('href="http://s/0/"', page)

    def test_request_host_is_used_when_public_base_url_is_not_set(self):
        status, _, page = self.request(
            "POST",
            "/",
            urlencode({"url": "https://example.com/host-fallback"}),
            {
                "Content-Type": "application/x-www-form-urlencoded",
                "Host": "localhost:8123",
            },
        )

        self.assertEqual(status, 200)
        self.assertIn('href="http://localhost:8123/0/"', page)

    def test_codespaces_public_base_url_is_derived_from_environment(self):
        environment = {
            "CODESPACE_NAME": "animated-space-waddle-g4g4qwj66jj73w5j4",
            "GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN": "app.github.dev",
        }

        self.assertEqual(
            _codespaces_public_base_url(8000, environment),
            "https://animated-space-waddle-g4g4qwj66jj73w5j4-8000.app.github.dev",
        )

    def test_codespaces_public_base_url_requires_both_environment_values(self):
        self.assertIsNone(_codespaces_public_base_url(8000, {}))
        self.assertIsNone(
            _codespaces_public_base_url(
                8000,
                {"CODESPACE_NAME": "test-codespace"},
            )
        )

    def test_public_base_url_must_be_an_http_origin(self):
        with self.assertRaises(ValueError):
            create_server(0, public_base_url="https://s/base")

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

    def test_table_shows_bucket_chains_and_expandable_horner_steps(self):
        first_url = "https://example.com/collision/0"
        bucket_index = self.shortener.table.hash_index(first_url)
        colliding_url = next(
            f"https://example.com/collision/{number}"
            for number in range(1, 1000)
            if self.shortener.table.hash_index(
                f"https://example.com/collision/{number}"
            )
            == bucket_index
        )
        urls = (first_url, colliding_url)
        codes = tuple(self.shortener.shorten(url) for url in urls)

        status, _, page = self.request("GET", "/table")

        self.assertEqual(status, 200)
        self.assertEqual(page.count('class="bucket"'), self.shortener.table.capacity)
        self.assertIn('class="empty">Empty<', page)
        self.assertIn(f'data-index="{bucket_index}"', page)
        self.assertEqual(page.count('class="chain-arrow"'), 1)
        self.assertEqual(page.count('class="horner-details"'), 2)
        for url, code in zip(urls, codes):
            self.assertIn(f"<code>{url}</code>", page)
            self.assertIn(f"<code>{code}</code>", page)
            self.assertIn(
                f'href="http://127.0.0.1:{self.port}/{code}/"',
                page,
            )

    def test_linear_table_can_be_selected_and_inspected(self):
        status, _, page = self.request("GET", "/?table=linear")
        self.assertEqual(status, 200)
        self.assertIn('value="linear" selected', page)
        self.assertIn('href="/table?table=linear"', page)

        status, _, page = self.request(
            "POST",
            "/",
            urlencode({"url": "https://linear.example", "table": "linear"}),
            {"Content-Type": "application/x-www-form-urlencoded"},
        )
        self.assertEqual(status, 200)
        self.assertIn("/0/?table=linear", page)
        self.assertIn('href="/table?table=linear"', page)

        status, _, page = self.request("GET", "/table?table=linear")
        self.assertEqual(status, 200)
        self.assertIn("Linear table internals", page)
        self.assertIn("Inspected cells=", page)
        self.assertIn("Horner:", page)

        status, headers, _ = self.request("GET", "/0/?table=linear")
        self.assertEqual(status, 302)
        self.assertEqual(dict(headers)["Location"], "https://linear.example")

        status, headers, _ = self.request("GET", "/s/0?table=linear")
        self.assertEqual(status, 302)
        self.assertEqual(dict(headers)["Location"], "https://linear.example")


if __name__ == "__main__":
    unittest.main()
