import unittest

from src.shortener import URLShortener


class URLShortenerTests(unittest.TestCase):
    def test_http_and_https_urls_can_be_shortened_and_expanded(self):
        shortener = URLShortener()
        urls = (
            "https://example.com/a?b=1#fragment",
            "http://example.org/path",
        )

        for url in urls:
            with self.subTest(url=url):
                code = shortener.shorten(url)
                self.assertEqual(shortener.expand(code), url)

    def test_same_url_reuses_code_and_distinct_url_gets_another(self):
        shortener = URLShortener()
        first_url = "https://example.com/"
        second_url = "https://example.com"

        first_code = shortener.shorten(first_url)
        self.assertEqual(first_code, "0")
        self.assertEqual(shortener.shorten(first_url), first_code)

        second_code = shortener.shorten(second_url)
        self.assertEqual(second_code, "1")
        self.assertNotEqual(second_code, first_code)
        self.assertEqual(shortener.expand(first_code), first_url)
        self.assertEqual(shortener.expand(second_code), second_url)

    def test_invalid_urls_are_rejected(self):
        shortener = URLShortener()
        invalid_urls = (
            "",
            "/relative/path",
            "ftp://example.com/",
            "https:///missing-host",
            " https://example.com/",
            "https://example.com/ ",
        )

        for url in invalid_urls:
            with self.subTest(url=url), self.assertRaises(ValueError):
                shortener.shorten(url)

        self.assertEqual(shortener.shorten("https://example.com/"), "0")

    def test_unregistered_code_cannot_be_expanded(self):
        with self.assertRaises(KeyError):
            URLShortener().expand("not-registered")


if __name__ == "__main__":
    unittest.main()
