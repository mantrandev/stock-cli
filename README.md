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

## Setup (crypto)

No key needed for coins with a Binance USDT pair — that covers BTC, ETH and most of the market.

Only symbols Binance does not list (OKB, GT, ...) need a CoinMarketCap key. Get a free one from the [CoinMarketCap API dashboard](https://pro.coinmarketcap.com/account), then save it to `~/.stockcli/config.json`:

```bash
mkdir -p ~/.stockcli
printf '{\n  "cmc_api_key": "PASTE_KEY_HERE"\n}\n' > ~/.stockcli/config.json
```

The file must contain:

```json
{
  "cmc_api_key": "your-coinmarketcap-key"
}
```

Without it, `crypto BTC` still works; `crypto OKB` reports that no Binance pair exists. `stock`, `fstock`, and `gold` never need a key.

## Commands

```bash
stockcli                              # Show all commands

stock <symbol>                        # Vietnam stock quote — e.g. VCB, HPG
stock buy <symbol> <price> <qty>
stock sell <symbol> <price> <qty>
stock remove <symbol> <qty>           # Remove entry (correction, no PnL)

crypto <symbol>                       # Crypto price (Binance, CMC fallback) — e.g. BTC, OKB, GT
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
| `stock`, `stockvn` | Entrade DNSE chart API |
| `fstock` | Yahoo Finance |
| `crypto` | Binance spot, CoinMarketCap fallback (key only for non-Binance symbols) |
| `gold` | Yahoo Finance (`GC=F`) |
