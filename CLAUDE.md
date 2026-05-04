# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Setup & Install

```bash
pip3 install --user --no-build-isolation -e .
```

## Commands

```bash
stock <symbol>              # fetch live quote
stock mine                  # show portfolio with live PnL
stock buy <symbol> <amount>
stock sell <symbol> <amount>
```

## Running Tests

```bash
python -m pytest tests/
# or single file:
python -m pytest tests/test_portfolio.py
```

No external dependencies — stdlib only (`urllib`, `json`, `pathlib`, `dataclasses`, `uuid`).

## Architecture

Four modules, each with a single responsibility:

- **`cli.py`** — argument dispatch and output formatting. Entry point: `main()`.
- **`quote.py`** — HTTP fetch from VPS API (`bgapidatafeed.vps.com.vn`). `_pick_price` tries keys in order: `closePrice → lastPrice → highPrice → lowPrice → r`.
- **`portfolio.py`** — pure functions for trade validation, position tracking, and PnL calculation. `summarize_portfolio(trades, live_prices)` is the core; called twice in `show_mine` — once without prices to get symbols, once with live prices for the final display.
- **`db.py`** — thin JSON read/write layer. DB path is hardcoded relative to the package root: `../../db/portfolio.json`.

## Key Constraints

- `db/portfolio.json` path resolves relative to `stockcli/db.py`, so it only points to the correct location when installed in editable mode from the project root.
- `sell` raises `ValueError` on oversell — `summarize_portfolio` validates shares before modifying position.
- Prices stored in VND as raw floats (no rounding until display via `format_vnd`).
