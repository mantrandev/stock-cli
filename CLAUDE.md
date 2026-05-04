# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Setup & Install

```bash
pip3 install --user --no-build-isolation -e .
```

## Commands

```bash
stock <symbol>              # Vietnam stock quote
stock mine                  # Portfolio with live PnL
stock buy <symbol> <amount>
stock sell <symbol> <amount>
fstock <symbol>             # Foreign stock quote (Yahoo Finance)
crypto <symbol>             # Crypto/USDT price (Binance)
```

## Running Tests

```bash
python3 -m unittest discover -s tests -v
# or single file:
python3 -m unittest tests.test_portfolio
```

No external dependencies — stdlib only (`urllib`, `json`, `pathlib`, `dataclasses`, `uuid`).

## Architecture

Five modules, each with a single responsibility:

- **`cli.py`** — argument dispatch and output formatting. Entry points: `main()`, `fstock_main()`, `crypto_main()`.
- **`quote.py`** — HTTP fetch from VPS API (`bgapidatafeed.vps.com.vn`). `_pick_price` tries keys in order: `closePrice → lastPrice → highPrice → lowPrice → r`.
- **`fstock.py`** — HTTP fetch from Yahoo Finance v8 chart API. Returns price and currency for any exchange-listed symbol.
- **`crypto.py`** — HTTP fetch from Binance public ticker. Appends `USDT` to the symbol (e.g. `BTC` → `BTCUSDT`).
- **`portfolio.py`** — pure functions for trade validation, position tracking, and PnL calculation. `summarize_portfolio(trades, live_prices)` is the core; called twice in `show_mine` — once without prices to get symbols, once with live prices for the final display.
- **`db.py`** — thin JSON read/write layer. DB path is hardcoded relative to the package root: `../../db/portfolio.json`.

## Key Constraints

- `db/portfolio.json` path resolves relative to `stockcli/db.py`, so it only points to the correct location when installed in editable mode from the project root.
- `sell` raises `ValueError` on oversell — `summarize_portfolio` validates shares before modifying position.
- Prices stored in VND as raw floats (no rounding until display via `format_vnd`). Foreign stock and crypto prices are in their native currency (USD).
- After adding a new entry point, reinstall the package and symlink the new binary from `~/Library/Python/3.14/bin/` to `~/.local/bin/`.
