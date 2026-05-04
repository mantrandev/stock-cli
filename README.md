# StockCLI

Terminal CLI for Vietnam stock quotes and a local JSON portfolio.

Live prices come from a public VPS quote feed.
Portfolio state is local only in [db/portfolio.json](/Users/maybe/Desktop/StockCLI/db/portfolio.json).
`buy` and `sell` do not place real orders.

## Commands

```bash
stock <symbol>
stock mine
stock buy <symbol> <amount>
stock sell <symbol> <amount>
```

## Setup

1. Install the package locally:

```bash
pip3 install --user --no-build-isolation -e .
```

2. Run it:

```bash
stock HPG
stock buy HPG 100
stock mine
```

## Notes

- `stock HPG` fetches the latest quote from `https://bgapidatafeed.vps.com.vn/getliststockdata/<SYMBOL>`
- `stock mine` calculates realized and unrealized PnL with average cost
- `stock buy` and `stock sell` store trades in local JSON using the current fetched price

## Sources

- Vnstock docs: https://vnstocks.com/docs/vnstock
- Vnstock GitHub: https://github.com/thinh-vu/vnstock
# stock-cli
