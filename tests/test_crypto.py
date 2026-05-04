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


class CryptoTests(unittest.TestCase):
    def test_fetch_crypto_returns_price(self):
        with patch("stockcli.crypto.urlopen", return_value=FakeResponse({"symbol": "BTCUSDT", "price": "78000.00"})):
            result = fetch_crypto("btc")

        self.assertEqual(result, {"symbol": "BTC", "pair": "BTCUSDT", "price": 78000.0})

    def test_fetch_crypto_raises_on_invalid_symbol(self):
        error = HTTPError(url=None, code=400, msg="Bad Request", hdrs=None, fp=BytesIO(b'{"code":-1121,"msg":"Invalid symbol."}'))
        with patch("stockcli.crypto.urlopen", side_effect=error):
            with self.assertRaisesRegex(RuntimeError, "Invalid symbol"):
                fetch_crypto("INVALID")


if __name__ == "__main__":
    unittest.main()
