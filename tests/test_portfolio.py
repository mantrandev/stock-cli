import unittest

from stockcli.portfolio import create_trade, parse_share_amount, summarize_portfolio


class PortfolioTests(unittest.TestCase):
    def test_parse_share_amount_accepts_positive_integers(self):
        self.assertEqual(parse_share_amount("100"), 100)
        with self.assertRaisesRegex(ValueError, "positive integer"):
            parse_share_amount("1.5")
        with self.assertRaisesRegex(ValueError, "positive integer"):
            parse_share_amount("0")

    def test_summarize_portfolio_calculates_realized_and_unrealized_pnl(self):
        trades = [
            create_trade("buy", "HPG", 100, 20000, "2026-01-01T00:00:00+00:00"),
            create_trade("buy", "HPG", 100, 22000, "2026-01-02T00:00:00+00:00"),
            create_trade("sell", "HPG", 50, 25000, "2026-01-03T00:00:00+00:00"),
        ]

        summary = summarize_portfolio(trades, {"HPG": 24000})

        self.assertEqual(len(summary["holdings"]), 1)
        self.assertEqual(summary["holdings"][0]["shares"], 150)
        self.assertEqual(summary["holdings"][0]["averageCost"], 21000)
        self.assertEqual(summary["holdings"][0]["marketValue"], 3600000)
        self.assertEqual(summary["realizedPnl"], 200000)
        self.assertEqual(summary["unrealizedPnl"], 450000)
        self.assertEqual(summary["totalPnl"], 650000)

    def test_summarize_portfolio_rejects_oversell(self):
        trades = [
            create_trade("buy", "FPT", 10, 100000, "2026-01-01T00:00:00+00:00"),
            create_trade("sell", "FPT", 11, 110000, "2026-01-02T00:00:00+00:00"),
        ]

        with self.assertRaisesRegex(ValueError, "Not enough shares"):
            summarize_portfolio(trades)


if __name__ == "__main__":
    unittest.main()
