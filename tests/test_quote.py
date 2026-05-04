import json
import unittest
from unittest.mock import patch

from stockcli.quote import _pick_price, fetch_quote


class FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def read(self):
        return json.dumps(self._payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return None


class QuoteTests(unittest.TestCase):
    def test_pick_price_prefers_close_then_match_then_reference(self):
        self.assertEqual(_pick_price({"closePrice": "25300"}), 25300)
        self.assertEqual(_pick_price({"lastPrice": "25200"}), 25200)
        self.assertEqual(_pick_price({"r": "25000"}), 25000)
        self.assertIsNone(_pick_price({"closePrice": None}))

    def test_fetch_quote_reads_from_vps_payload(self):
        with patch(
            "stockcli.quote.urlopen",
            return_value=FakeResponse([{"sym": "HPG", "boardId": "G1", "closePrice": "25300"}]),
        ):
            quote = fetch_quote("hpg")

        self.assertEqual(quote, {"symbol": "HPG", "exchange": "G1", "price": 25300})

    def test_fetch_quote_errors_when_payload_is_empty(self):
        with patch("stockcli.quote.urlopen", return_value=FakeResponse([])):
            with self.assertRaisesRegex(RuntimeError, "No price returned"):
                fetch_quote("HPG")


if __name__ == "__main__":
    unittest.main()
