import unittest

from src.hash_table import HashTable
from src.linear_probing import LinearProbingHashTable
from src.shortener import URLShortener


class URLShortenerTests(unittest.TestCase):
    def test_shortens_and_expands_urls(self):
        for table_class in (HashTable, LinearProbingHashTable):
            with self.subTest(table=table_class.__name__):
                shortener = URLShortener(table_class=table_class)
                url = "https://example.com/a?b=1#fragment"
                code = shortener.shorten(url)
                self.assertEqual(code, "0")
                self.assertEqual(shortener.expand(code), url)
                self.assertEqual(shortener.shorten(url), code)

    def test_distinct_urls_get_distinct_sequential_codes(self):
        for table_class in (HashTable, LinearProbingHashTable):
            with self.subTest(table=table_class.__name__):
                shortener = URLShortener(table_class=table_class)
                self.assertEqual(shortener.shorten("https://one.example"), "0")
                self.assertEqual(shortener.shorten("http://two.example"), "1")

    def test_invalid_urls_are_rejected_without_allocating_codes(self):
        for table_class in (HashTable, LinearProbingHashTable):
            with self.subTest(table=table_class.__name__):
                shortener = URLShortener(table_class=table_class)
                for url in (
                    "",
                    " https://example.com",
                    "https://example.com ",
                    "/relative/path",
                    "ftp://example.com",
                    "https:///missing-host",
                    "https://example.com:invalid",
                ):
                    with self.subTest(url=url), self.assertRaises(ValueError):
                        shortener.shorten(url)
                self.assertEqual(shortener.shorten("https://example.com"), "0")

    def test_unknown_code_raises_key_error(self):
        for table_class in (HashTable, LinearProbingHashTable):
            with self.subTest(table=table_class.__name__), self.assertRaises(KeyError):
                URLShortener(table_class=table_class).expand("missing")

    def test_table_implementation_can_be_injected(self):
        for table_class in (HashTable, LinearProbingHashTable):
            with self.subTest(table=table_class.__name__):
                shortener = URLShortener(table_class=table_class, initial_capacity=4)
                self.assertEqual(
                    shortener.expand(shortener.shorten("https://example.org")),
                    "https://example.org",
                )


if __name__ == "__main__":
    unittest.main()
