# StockCLI

Terminal CLI for Vietnam stocks, foreign stocks, and crypto prices with a local JSON portfolio.

## Commands

```bash
stock <symbol>              # Global stock quote (Yahoo Finance) — e.g. AAPL, TSLA
stock mine                  # Portfolio with live PnL
stock buy <symbol> <price> <amount>
stock sell <symbol> <price> <amount>
stock clear                 # Reset portfolio

stockvn <symbol>            # Vietnam stock quote (VPS) — e.g. TCI, HPG
fstock <symbol>             # Alias for stock
crypto <symbol>             # Crypto/USDT price (Binance) — e.g. BTC, ETH
gold                        # Gold spot price (USD/oz)
```

## Setup

```bash
pip3 install --user --no-build-isolation -e .
```

## Data Sources

| Command  | Source | URL |
|----------|--------|-----|
| `stock`  | Yahoo Finance | `https://query1.finance.yahoo.com/v8/finance/chart/<SYMBOL>` |
| `stockvn` | VPS DataFeed | `https://bgapidatafeed.vps.com.vn/getliststockdata/<SYMBOL>` |
| `fstock` | Yahoo Finance | `https://query1.finance.yahoo.com/v8/finance/chart/<SYMBOL>` |
| `crypto` | Binance | `https://api.binance.com/api/v3/ticker/price?symbol=<SYMBOL>USDT` |
| `gold`   | Yahoo Finance (`GC=F`) | `https://query1.finance.yahoo.com/v8/finance/chart/GC=F` |

## Notes

- Portfolio state is local only in `db/portfolio.json`. `buy` and `sell` do not place real orders.
- `stock mine` calculates realized and unrealized PnL with average cost basis.
- Prices are VND for Vietnam stocks, USD for foreign stocks and crypto.
