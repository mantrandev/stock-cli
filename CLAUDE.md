# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Setup & Install

```bash
pip3 install --user --no-build-isolation -e .
```

Users install from git with `pipx install "git+https://github.com/mantrandev/stock-cli.git"` (see README).

## Commands

```bash
stock <symbol>                  # Vietnam stock quote
stock buy|sell <symbol> <price> <qty>
stock remove <symbol> <qty>     # Correction, no realized PnL

crypto <symbol>                 # Crypto price (Binance; CMC fallback needs key)
crypto buy|sell <symbol> <price> <qty>
crypto remove <symbol> <qty>

gold                            # Gold spot (USD/oz, Yahoo GC=F)
gold buy|sell <price> <qty_oz>
gold remove <qty_oz>

port-mine                       # All holdings with live PnL
port-mine clear|remove <symbol> <qty>

fstock <symbol>                 # Foreign stock quote (Yahoo Finance)
stockvn <symbol>                # Alias for `stock <symbol>`
stockcli                        # Show all commands
```

## Running Tests

```bash
python3 -m unittest discover -s tests -v
# or single file:
python3 -m unittest tests.test_portfolio
```

No external dependencies — stdlib only (`urllib`, `json`, `pathlib`, `concurrent.futures`).

## Architecture

Six modules, each with a single responsibility:

- **`cli.py`** — argument dispatch and output formatting. Entry points: `main`, `crypto_main`, `fstock_main`, `gold_main`, `stockvn_main`, `port_mine_main`, `help_main` (wired in `pyproject.toml`). `show_all_portfolio` fetches VN, crypto, and gold prices concurrently, then prints one section per asset via `_build_holdings`.
- **`quote.py`** — HTTP fetch from Entrade DNSE chart API (`services.entrade.com.vn/chart-api/v2/ohlcs/stock`, `resolution=1D`). Takes the last daily close from the `c` array; the API quotes in thousands of VND, so the value is multiplied by `PRICE_UNIT` (1000). A 400 response means an unknown symbol.
- **`fstock.py`** — HTTP fetch from Yahoo Finance v8 chart API. Returns price and currency for any exchange-listed symbol. Also backs `gold` via `GC=F`.
- **`crypto.py`** — Binance `ticker/price` on `<SYMBOL>USDT` first (no key). A 400 means no such pair, and it falls back to CoinMarketCap `cryptocurrency/quotes/latest` using `cmc_api_key` from `~/.stockcli/config.json`; the CMC path guards the duplicate-symbol list case. `pair` in the result marks which source answered.
- **`portfolio.py`** — pure functions over a positions dict; no I/O. `apply_buy`, `apply_sell`, `apply_remove` mutate in place, `resolve_asset` maps a bare symbol back to its asset type, and `format_vnd` / `format_usd` handle display.
- **`db.py`** — thin JSON read/write layer over `~/.stocklocal`.

Positions are keyed `"<asset>:<symbol>"` (e.g. `crypto:BTC`), where asset is one of `vn`, `crypto`, `gold`. Each value holds `quantity`, `avgCost`, `currency`, and `realizedPnl`.

## Key Constraints

- Quantities are integer-only for `vn` and fractional for `crypto` / `gold` — `parse_quantity(..., integer_only=True)` enforces it. Any command path that picks the wrong asset therefore rejects valid input with a misleading "positive integer" error.
- `port-mine remove <symbol>` has no asset argument, so it calls `resolve_asset` to look the symbol up in stored positions. Never infer the asset from the symbol string.
- `apply_sell` and `apply_remove` raise `ValueError` on oversell/overremove, checked before the position is modified.
- Prices stored in VND as raw floats (no rounding until display via `format_vnd`). Foreign stock, crypto, and gold prices are in their native currency (USD).
- After adding a new entry point, reinstall the package; with the `pip3 install --user` path above, symlink the new binary from `~/Library/Python/3.14/bin/` to `~/.local/bin/`.
