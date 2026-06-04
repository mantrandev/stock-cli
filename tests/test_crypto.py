import json
import unittest
from io import BytesIO
from unittest.mock import patch
from urllib.error import HTTPError

from stockcli.crypto import fetch_crypto


class FakeResponse:
    def __init__(self, payload):
        self._data = json.dumps(payload).encode("utf-8")

    def read(self):
        return self._data

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return None


def _quote(symbol, price):
    return {"data": {symbol: {"symbol": symbol, "quote": {"USD": {"price": price}}}}}


class CryptoTests(unittest.TestCase):
    def setUp(self):
        patcher = patch("stockcli.crypto._load_api_key", return_value="test-key")
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_fetch_crypto_returns_price(self):
        with patch("stockcli.crypto.urlopen", return_value=FakeResponse(_quote("BTC", 78000.00))):
            result = fetch_crypto("btc")

        self.assertEqual(result, {"symbol": "BTC", "pair": "BTC/USD", "price": 78000.0})

    def test_fetch_crypto_handles_duplicate_symbol_list(self):
        payload = {"data": {"BNB": [{"symbol": "BNB", "quote": {"USD": {"price": 600.0}}}]}}
        with patch("stockcli.crypto.urlopen", return_value=FakeResponse(payload)):
            result = fetch_crypto("bnb")

        self.assertEqual(result["price"], 600.0)

    def test_fetch_crypto_raises_on_invalid_symbol(self):
        body = b'{"status":{"error_message":"Invalid value for \\"symbol\\""}}'
        error = HTTPError(url=None, code=400, msg="Bad Request", hdrs=None, fp=BytesIO(body))
        with patch("stockcli.crypto.urlopen", side_effect=error):
            with self.assertRaisesRegex(RuntimeError, "Invalid value"):
                fetch_crypto("INVALID")


if __name__ == "__main__":
    unittest.main()
