"""In-memory URL shortening with sequential base62 codes."""

from threading import Lock
from urllib.parse import urlsplit


ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


def encode_base62(number: int) -> str:
    if number < 0:
        raise ValueError("number must be non-negative")
    if number == 0:
        return ALPHABET[0]

    encoded = []
    while number:
        number, remainder = divmod(number, len(ALPHABET))
        encoded.append(ALPHABET[remainder])
    return "".join(reversed(encoded))


class URLShortener:
    def __init__(self) -> None:
        self._url_to_code: dict[str, str] = {}
        self._code_to_url: dict[str, str] = {}
        self._next_id = 1
        self._lock = Lock()

    def shorten(self, url: str) -> str:
        if not isinstance(url, str):
            raise ValueError("url must be a string")
        try:
            parsed = urlsplit(url)
        except ValueError as error:
            raise ValueError("url must be a valid absolute http or https URL") from error
        if parsed.scheme not in ("http", "https") or not parsed.hostname:
            raise ValueError("url must be an absolute http or https URL")
        try:
            parsed.port
        except ValueError as error:
            raise ValueError("url contains an invalid port") from error

        with self._lock:
            existing = self._url_to_code.get(url)
            if existing is not None:
                return existing

            code = encode_base62(self._next_id)
            self._next_id += 1
            self._url_to_code[url] = code
            self._code_to_url[code] = url
            return code

    def expand(self, code: str) -> str | None:
        with self._lock:
            return self._code_to_url.get(code)
