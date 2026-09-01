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


def _binance_404():
    body = b'{"code":-1121,"msg":"Invalid symbol."}'
    return HTTPError(url=None, code=400, msg="Bad Request", hdrs=None, fp=BytesIO(body))


class CryptoTests(unittest.TestCase):
    def test_fetch_crypto_reads_binance_first(self):
        with patch("stockcli.crypto.urlopen", return_value=FakeResponse({"price": "78000.00"})):
            result = fetch_crypto("btc")

        self.assertEqual(result, {"symbol": "BTC", "pair": "BTC/USDT", "price": 78000.0})

    def test_fetch_crypto_falls_back_to_cmc_without_usdt_pair(self):
        payload = {"data": {"OKB": {"symbol": "OKB", "quote": {"USD": {"price": 45.5}}}}}
        responses = [_binance_404(), FakeResponse(payload)]

        def fake_urlopen(*_, **__):
            item = responses.pop(0)
            if isinstance(item, HTTPError):
                raise item
            return item

        with patch("stockcli.crypto._load_api_key", return_value="test-key"):
            with patch("stockcli.crypto.urlopen", side_effect=fake_urlopen):
                result = fetch_crypto("okb")

        self.assertEqual(result, {"symbol": "OKB", "pair": "OKB/USD", "price": 45.5})

    def test_fetch_crypto_handles_duplicate_symbol_list(self):
        payload = {"data": {"BNB": [{"symbol": "BNB", "quote": {"USD": {"price": 600.0}}}]}}
        responses = [_binance_404(), FakeResponse(payload)]

        def fake_urlopen(*_, **__):
            item = responses.pop(0)
            if isinstance(item, HTTPError):
                raise item
            return item

        with patch("stockcli.crypto._load_api_key", return_value="test-key"):
            with patch("stockcli.crypto.urlopen", side_effect=fake_urlopen):
                result = fetch_crypto("bnb")

        self.assertEqual(result["price"], 600.0)

    def test_fetch_crypto_errors_without_pair_or_key(self):
        with patch("stockcli.crypto._load_api_key", return_value=None):
            with patch("stockcli.crypto.urlopen", side_effect=_binance_404()):
                with self.assertRaisesRegex(RuntimeError, "No Binance USDT pair for OKB"):
                    fetch_crypto("okb")


if __name__ == "__main__":
    unittest.main()
