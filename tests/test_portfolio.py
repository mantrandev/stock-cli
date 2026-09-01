import unittest

from stockcli.portfolio import (
    apply_buy, apply_remove, apply_sell, parse_share_amount, resolve_asset,
)


class PortfolioTests(unittest.TestCase):
    def test_parse_share_amount_accepts_positive_integers(self):
        self.assertEqual(parse_share_amount("100"), 100)
        with self.assertRaisesRegex(ValueError, "positive integer"):
            parse_share_amount("1.5")
        with self.assertRaisesRegex(ValueError, "positive integer"):
            parse_share_amount("0")

    def test_apply_buy_creates_and_updates_position(self):
        positions = {}
        apply_buy(positions, "vn", "HPG", 100, 20000)
        apply_buy(positions, "vn", "HPG", 100, 22000)

        pos = positions["vn:HPG"]
        self.assertEqual(pos["quantity"], 200)
        self.assertEqual(pos["avgCost"], 21000)

    def test_apply_sell_updates_realized_pnl(self):
        positions = {}
        apply_buy(positions, "vn", "HPG", 200, 21000)
        apply_sell(positions, "vn", "HPG", 50, 25000)

        pos = positions["vn:HPG"]
        self.assertEqual(pos["quantity"], 150)
        self.assertEqual(pos["realizedPnl"], 200000)

    def test_apply_sell_rejects_oversell(self):
        positions = {}
        apply_buy(positions, "vn", "FPT", 10, 100000)

        with self.assertRaisesRegex(ValueError, "Not enough FPT"):
            apply_sell(positions, "vn", "FPT", 11, 110000)

    def test_apply_remove_reduces_quantity(self):
        positions = {}
        apply_buy(positions, "crypto", "BTC", 0.015, 70000)
        apply_remove(positions, "crypto", "BTC", 0.005)

        self.assertAlmostEqual(positions["crypto:BTC"]["quantity"], 0.01)

    def test_apply_remove_deletes_position_when_fully_removed(self):
        positions = {}
        apply_buy(positions, "crypto", "BTC", 0.015, 70000)
        apply_remove(positions, "crypto", "BTC", 0.015)

        self.assertNotIn("crypto:BTC", positions)

    def test_apply_buy_float_quantity(self):
        positions = {}
        apply_buy(positions, "crypto", "BTC", 0.015, 70000)
        apply_sell(positions, "crypto", "BTC", 0.005, 75000)

        self.assertAlmostEqual(positions["crypto:BTC"]["quantity"], 0.01)
        self.assertAlmostEqual(positions["crypto:BTC"]["realizedPnl"], 25.0)


class ResolveAssetTests(unittest.TestCase):
    def setUp(self):
        self.positions = {}
        apply_buy(self.positions, "crypto", "BTC", 0.5, 70000.0)
        apply_buy(self.positions, "vn", "HPG", 100, 22250.0)
        apply_buy(self.positions, "gold", "GOLD", 1.5, 3200.0)

    def test_resolves_asset_from_stored_position(self):
        self.assertEqual(resolve_asset(self.positions, "btc"), "crypto")
        self.assertEqual(resolve_asset(self.positions, "HPG"), "vn")
        self.assertEqual(resolve_asset(self.positions, "GOLD"), "gold")

    def test_rejects_symbol_with_no_open_position(self):
        with self.assertRaisesRegex(ValueError, "No open position for ETH"):
            resolve_asset(self.positions, "ETH")

    def test_ignores_fully_closed_position(self):
        apply_remove(self.positions, "vn", "HPG", 100)
        with self.assertRaisesRegex(ValueError, "No open position for HPG"):
            resolve_asset(self.positions, "HPG")

    def test_rejects_symbol_held_under_two_assets(self):
        apply_buy(self.positions, "vn", "BTC", 10, 15000.0)
        with self.assertRaisesRegex(ValueError, "held as crypto and vn"):
            resolve_asset(self.positions, "BTC")


if __name__ == "__main__":
    unittest.main()
