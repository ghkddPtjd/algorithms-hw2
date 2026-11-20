"""URL validation and bidirectional URL/code lookup."""

from urllib.parse import urlsplit

from src.base62 import encode
from src.hash_table import HashTable


class URLShortener:
    def __init__(
        self,
        table_class: type = HashTable,
        initial_capacity: int = 8,
        max_load_factor: float | None = 0.75,
    ) -> None:
        self._url_to_code = table_class(
            initial_capacity=initial_capacity,
            max_load_factor=max_load_factor,
        )
        self._code_to_url = table_class(
            initial_capacity=initial_capacity,
            max_load_factor=max_load_factor,
        )
        self._next_id = 0

    @property
    def table(self) -> HashTable:
        return self._url_to_code

    def shorten(self, url: str) -> str:
        self._validate_url(url)
        existing_code = self._url_to_code.get(url)
        if existing_code is not None:
            return existing_code

        code = encode(self._next_id)
        self._next_id += 1
        self._url_to_code.put(url, code)
        self._code_to_url.put(code, url)
        return code

    def expand(self, code: str) -> str:
        if not isinstance(code, str):
            raise TypeError("code must be a string")
        url = self._code_to_url.get(code)
        if url is None:
            raise KeyError(code)
        return url

    @staticmethod
    def _validate_url(url: str) -> None:
        if not isinstance(url, str):
            raise TypeError("url must be a string")
        if not url or url != url.strip() or any(character.isspace() for character in url):
            raise ValueError("url must not contain whitespace")
        try:
            parts = urlsplit(url)
            port = parts.port
        except ValueError as error:
            raise ValueError("url is invalid") from error
        if parts.scheme not in ("http", "https") or not parts.hostname:
            raise ValueError("url must be an absolute HTTP or HTTPS URL with a host")
        if port is not None and not 1 <= port <= 65535:
            raise ValueError("url port must be between 1 and 65535")
