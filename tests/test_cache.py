import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from argus.ingest.cache import fetch


class CacheTests(unittest.TestCase):
    def test_incomplete_http_body_is_not_cached(self):
        class Headers(dict):
            def get_content_type(self): return "application/pdf"
        class Response:
            headers = Headers({"Content-Length": "20"})
            def __enter__(self): return self
            def __exit__(self, *args): return False
            def geturl(self): return "https://example.org/report.pdf"
            def read(self, size):
                if not hasattr(self, "sent"):
                    self.sent = True
                    return b"%PDF-short"
                return b""
        with tempfile.TemporaryDirectory() as tmp:
            with patch("argus.ingest.cache.urlopen", return_value=Response()):
                with self.assertRaisesRegex(RuntimeError, "download was incomplete"):
                    fetch("https://example.org/report.pdf", cache_dir=tmp)
            self.assertEqual(list(Path(tmp).iterdir()), [])


if __name__ == "__main__": unittest.main()
