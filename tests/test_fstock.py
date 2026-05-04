import json
import unittest
from io import BytesIO
from unittest.mock import patch
from urllib.error import HTTPError

from stockcli.fstock import fetch_fstock


FAKE_PAYLOAD = {
    "chart": {
        "result": [{
            "meta": {
                "symbol": "AAPL",
                "fullExchangeName": "NasdaqGS",
                "regularMarketPrice": 189.5,
                "currency": "USD",
            }
        }],
        "error": None,
    }
}


class FakeResponse:
    def __init__(self, payload):
        self._data = json.dumps(payload).encode("utf-8")

    def read(self):
        return self._data

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return None


class FstockTests(unittest.TestCase):
    def test_fetch_fstock_returns_quote(self):
        with patch("stockcli.fstock.urlopen", return_value=FakeResponse(FAKE_PAYLOAD)):
            result = fetch_fstock("aapl")

        self.assertEqual(result, {"symbol": "AAPL", "exchange": "NasdaqGS", "price": 189.5, "currency": "USD"})

    def test_fetch_fstock_raises_on_404(self):
        error = HTTPError(url=None, code=404, msg="Not Found", hdrs=None, fp=BytesIO(b""))
        with patch("stockcli.fstock.urlopen", side_effect=error):
            with self.assertRaisesRegex(RuntimeError, "Symbol not found"):
                fetch_fstock("INVALID")


if __name__ == "__main__":
    unittest.main()
