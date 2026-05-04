# StockCLI

Terminal CLI for Vietnam stocks, foreign stocks, and crypto prices with a local JSON portfolio.

## Commands

```bash
stock <symbol>              # Vietnam stock quote (VPS feed)
stock mine                  # Portfolio with live PnL
stock buy <symbol> <amount>
stock sell <symbol> <amount>

fstock <symbol>             # Foreign stock quote (Yahoo Finance) — e.g. AAPL, TSLA
crypto <symbol>             # Crypto/USDT price (Binance) — e.g. BTC, ETH
```

## Setup

```bash
pip3 install --user --no-build-isolation -e .
```

## Notes

- Portfolio state is local only in `db/portfolio.json`. `buy` and `sell` do not place real orders.
- `stock mine` calculates realized and unrealized PnL with average cost basis.
- Prices are VND for Vietnam stocks, USD for foreign stocks and crypto.
