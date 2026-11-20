import json
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import urlopen

from src.server import create_server


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
            self.assertIn("서버가 실행 중입니다", response.read().decode("utf-8"))

    def test_health_endpoint_returns_ok(self) -> None:
        with urlopen(f"{self.base_url}/health") as response:
            self.assertEqual(response.status, 200)
            self.assertEqual(json.load(response), {"status": "ok"})

    def test_unknown_path_returns_not_found(self) -> None:
        with self.assertRaises(HTTPError) as error:
            urlopen(f"{self.base_url}/missing")

        self.assertEqual(error.exception.code, 404)
        self.assertEqual(json.load(error.exception), {"error": "not found"})


if __name__ == "__main__":
    unittest.main()
