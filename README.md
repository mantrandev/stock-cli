# StockCLI

Terminal CLI for Vietnam stocks, crypto, and gold — with a local portfolio tracker and live PnL.

## Install

```bash
pipx install "git+https://github.com/mantrandev/stock-cli.git"
```

Upgrade:

```bash
pipx upgrade stockcli
```

## Commands

```bash
stockcli                              # Show all commands

stock <symbol>                        # Vietnam stock quote — e.g. VCB, HPG
stock buy <symbol> <price> <qty>
stock sell <symbol> <price> <qty>
stock remove <symbol> <qty>           # Remove entry (correction, no PnL)

crypto <symbol>                       # Crypto/USDT price — e.g. BTC, ETH
crypto buy <symbol> <price> <qty>
crypto sell <symbol> <price> <qty>
crypto remove <symbol> <qty>

gold                                  # Gold spot price (USD/oz)
gold buy <price> <qty_oz>
gold sell <price> <qty_oz>
gold remove <qty_oz>

port-mine                             # All holdings with live PnL and PnL%
port-mine clear                       # Reset portfolio
port-mine remove <symbol> <qty>

fstock <symbol>                       # Foreign stock quote — e.g. AAPL, TSLA
stockvn <symbol>                      # Vietnam stock quote (alias for stock)
```

## Examples

```bash
stock VCB
stock buy VCB 87000 100
stock sell VCB 90000 50

crypto BTC
crypto buy BTC 70000 0.015
crypto sell BTC 75000 0.005

gold
gold buy 3200 1.5

port-mine
```

## Portfolio

`port-mine` shows all open positions grouped by asset type with live prices:

```
=== VN STOCKS (VND) ===
SYMBOL         QTY        AVG COST            LAST           VALUE            UPNL    UPNL%
VCB            100    87,000 VND      90,000 VND    9,000,000 VND    300,000 VND   +3.45%

Realized: 0 VND  Unrealized: 300,000 VND (+3.45%)  Total: 300,000 VND

=== CRYPTO (USD) ===
SYMBOL          QTY    AVG COST        LAST       VALUE        UPNL    UPNL%
BTC            0.01   $70,000.00   $80,000.00    $800.00     $100.00  +14.29%

Realized: $25.00  Unrealized: $100.00 (+14.29%)  Total: $125.00
```

Portfolio is stored locally at `~/.stocklocal`. No real orders are placed.

## Data Sources

| Command | Source |
|---------|--------|
| `stock`, `stockvn` | VPS DataFeed |
| `fstock` | Yahoo Finance |
| `crypto` | Binance |
| `gold` | Yahoo Finance (`GC=F`) |
