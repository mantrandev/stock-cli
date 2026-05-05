from __future__ import annotations

import sys

from stockcli.crypto import fetch_crypto
from stockcli.fstock import fetch_fstock
from stockcli.db import append_trade, load_db
from stockcli.portfolio import create_trade, format_vnd, parse_share_amount, summarize_portfolio
from stockcli.quote import fetch_quote


def print_usage() -> None:
    print(
        "Usage:\n"
        "  stock <symbol>\n"
        "  stock mine\n"
        "  stock buy <symbol> <price> <amount>\n"
        "  stock sell <symbol> <price> <amount>"
    )


def format_optional_vnd(value: float | None) -> str:
    return "N/A" if value is None else format_vnd(value)


def fetch_live_prices(symbols: list[str]) -> dict[str, float | None]:
    prices: dict[str, float | None] = {}
    for symbol in symbols:
        try:
            prices[symbol] = fetch_quote(symbol)["price"]
        except Exception as exc:  # pragma: no cover - keeps CLI resilient
            prices[symbol] = None
            print(f"Warning: could not fetch {symbol}: {exc}", file=sys.stderr)
    return prices


def show_quote(symbol: str) -> int:
    quote = fetch_quote(symbol)
    exchange = f" ({quote['exchange']})" if quote.get("exchange") else ""
    print(f"{quote['symbol']}{exchange}: {format_vnd(quote['price'])}")
    return 0


def record_trade(trade_type: str, symbol: str, price_input: str, amount_input: str) -> int:
    try:
        price = float(price_input)
        if price <= 0:
            raise ValueError
    except ValueError:
        raise ValueError("Price must be a positive number.")
    amount = parse_share_amount(amount_input)
    db = load_db()
    trade = create_trade(trade_type, symbol, amount, price)

    if trade_type == "sell":
        summarize_portfolio([*db["trades"], trade])

    append_trade(trade)
    print(f"{trade_type.upper()} {trade['shares']} {trade['symbol']} @ {format_vnd(trade['price'])}")
    return 0


def print_mine(summary: dict) -> None:
    if not summary["holdings"]:
        print("No open positions.")
    else:
        print("SYMBOL  SHARES  AVG COST     COST         LAST         VALUE        UPNL")
        for holding in summary["holdings"]:
            total_cost = holding["averageCost"] * holding["shares"]
            row = [
                holding["symbol"].ljust(6),
                str(holding["shares"]).rjust(6),
                format_vnd(holding["averageCost"]).rjust(12),
                format_vnd(total_cost).rjust(12),
                format_optional_vnd(holding["lastPrice"]).rjust(12),
                format_vnd(holding["marketValue"]).rjust(12),
                format_vnd(holding["unrealizedPnl"]).rjust(12),
            ]
            print("  ".join(row))

    print("")
    print(f"Realized PnL:   {format_vnd(summary['realizedPnl'])}")
    print(f"Unrealized PnL: {format_vnd(summary['unrealizedPnl'])}")
    print(f"Total PnL:      {format_vnd(summary['totalPnl'])}")


def show_mine() -> int:
    db = load_db()
    if not db["trades"]:
        print("Portfolio is empty.")
        return 0

    base_summary = summarize_portfolio(db["trades"])
    live_prices = fetch_live_prices([holding["symbol"] for holding in base_summary["holdings"]])
    summary = summarize_portfolio(db["trades"], live_prices)
    print_mine(summary)
    return 0


def main() -> int:
    args = sys.argv[1:]
    if not args or args[0] in {"help", "--help", "-h"}:
        print_usage()
        return 0 if args else 1

    try:
        if args[0] == "mine":
            return show_mine()

        if args[0] in {"buy", "sell"}:
            if len(args) != 4:
                print_usage()
                return 1
            return record_trade(args[0], args[1], args[2], args[3])

        if len(args) == 1:
            return show_quote(args[0])
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print_usage()
    return 1


def show_crypto(symbol: str) -> int:
    result = fetch_crypto(symbol)
    print(f"{result['symbol']}/USDT: ${result['price']:,.2f}")
    return 0


def show_fstock(symbol: str) -> int:
    result = fetch_fstock(symbol)
    exchange = f" ({result['exchange']})" if result.get("exchange") else ""
    print(f"{result['symbol']}{exchange}: {result['price']:,.2f} {result['currency']}")
    return 0


def fstock_main() -> int:
    args = sys.argv[1:]
    if not args or args[0] in {"help", "--help", "-h"}:
        print("Usage:\n  fstock <symbol>")
        return 0 if args else 1

    try:
        if len(args) == 1:
            return show_fstock(args[0])
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print("Usage:\n  fstock <symbol>")
    return 1


def crypto_main() -> int:
    args = sys.argv[1:]
    if not args or args[0] in {"help", "--help", "-h"}:
        print("Usage:\n  crypto <symbol>")
        return 0 if args else 1

    try:
        if len(args) == 1:
            return show_crypto(args[0])
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print("Usage:\n  crypto <symbol>")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
