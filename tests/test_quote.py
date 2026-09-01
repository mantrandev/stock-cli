import json
import unittest
from io import BytesIO
from unittest.mock import patch
from urllib.error import HTTPError

from stockcli.quote import fetch_quote


class FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def read(self):
        return json.dumps(self._payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return None


def _ohlc(*closes):
    return {
        "t": list(range(len(closes))),
        "o": list(closes),
        "h": list(closes),
        "l": list(closes),
        "c": list(closes),
        "v": [0] * len(closes),
        "nextTime": 0,
    }


class QuoteTests(unittest.TestCase):
    def test_fetch_quote_uses_latest_close_in_vnd(self):
        with patch("stockcli.quote.urlopen", return_value=FakeResponse(_ohlc(22.05, 22.25))):
            quote = fetch_quote("hpg")

        self.assertEqual(quote, {"symbol": "HPG", "price": 22250.0})

    def test_fetch_quote_errors_when_payload_has_no_candles(self):
        with patch("stockcli.quote.urlopen", return_value=FakeResponse({"t": [], "c": []})):
            with self.assertRaisesRegex(RuntimeError, "No price returned"):
                fetch_quote("HPG")

    def test_fetch_quote_errors_on_invalid_symbol(self):
        body = b'{"status":400,"code":"BAD_REQUEST","message":"invalid symbol"}'
        error = HTTPError(url=None, code=400, msg="Bad Request", hdrs=None, fp=BytesIO(body))
        with patch("stockcli.quote.urlopen", side_effect=error):
            with self.assertRaisesRegex(RuntimeError, "Symbol not found: ZZZZ"):
                fetch_quote("zzzz")


if __name__ == "__main__":
    unittest.main()
