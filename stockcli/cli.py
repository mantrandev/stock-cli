from __future__ import annotations

import sys
from concurrent.futures import ThreadPoolExecutor

from stockcli.crypto import fetch_crypto
from stockcli.fstock import fetch_fstock
from stockcli.db import load_positions, save_positions
from stockcli.portfolio import (
    apply_buy, apply_remove, apply_sell,
    format_usd, format_vnd, parse_quantity,
)
from stockcli.quote import fetch_quote


def _usage_all() -> None:
    print(
        "Commands:\n"
        "  stock <symbol>                    Vietnam stock quote\n"
        "  stock buy <symbol> <price> <qty>\n"
        "  stock sell <symbol> <price> <qty>\n"
        "  stock remove <symbol> <qty>\n"
        "\n"
        "  crypto <symbol>                   Crypto quote (CoinMarketCap)\n"
        "  crypto buy <symbol> <price> <qty>\n"
        "  crypto sell <symbol> <price> <qty>\n"
        "  crypto remove <symbol> <qty>\n"
        "\n"
        "  gold                              Gold spot price\n"
        "  gold buy <price> <qty_oz>\n"
        "  gold sell <price> <qty_oz>\n"
        "  gold remove <qty_oz>\n"
        "\n"
        "  port-mine                         All holdings with live PnL\n"
        "  port-mine clear\n"
        "  port-mine remove <symbol> <qty>\n"
        "\n"
        "  fstock <symbol>                   Foreign stock quote (Yahoo Finance)\n"
        "  stockvn <symbol>                  Vietnam stock quote (alias)"
    )


def _usage_stock() -> None:
    print(
        "Usage:\n"
        "  stock <symbol>\n"
        "  stock buy <symbol> <price> <qty>\n"
        "  stock sell <symbol> <price> <qty>\n"
        "  stock remove <symbol> <qty>"
    )


def _usage_crypto() -> None:
    print(
        "Usage:\n"
        "  crypto <symbol>\n"
        "  crypto buy <symbol> <price> <qty>\n"
        "  crypto sell <symbol> <price> <qty>\n"
        "  crypto remove <symbol> <qty>"
    )


def _usage_gold() -> None:
    print(
        "Usage:\n"
        "  gold\n"
        "  gold buy <price> <qty_oz>\n"
        "  gold sell <price> <qty_oz>\n"
        "  gold remove <qty_oz>"
    )


def _usage_mine() -> None:
    print(
        "Usage:\n"
        "  port-mine\n"
        "  port-mine clear\n"
        "  port-mine remove <symbol> <qty>"
    )


def _parse_price(value: str) -> float:
    try:
        price = float(value)
        if price <= 0:
            raise ValueError
        return price
    except ValueError:
        raise ValueError("Price must be a positive number.")


def show_quote_vn(symbol: str) -> int:
    quote = fetch_quote(symbol)
    exchange = f" ({quote['exchange']})" if quote.get("exchange") else ""
    print(f"{quote['symbol']}{exchange}: {format_vnd(quote['price'])}")
    return 0


def show_crypto(symbol: str) -> int:
    result = fetch_crypto(symbol)
    print(f"{result['symbol']}/USDT: {format_usd(result['price'])}")
    return 0


def fetch_live_prices_vn(symbols: list[str]) -> dict[str, float | None]:
    def fetch_one(symbol: str) -> tuple[str, float | None]:
        try:
            return symbol, fetch_quote(symbol)["price"]
        except Exception as exc:
            print(f"Warning: could not fetch {symbol}: {exc}", file=sys.stderr)
            return symbol, None

    with ThreadPoolExecutor(max_workers=len(symbols) or 1) as executor:
        return dict(executor.map(fetch_one, symbols))


def fetch_live_prices_crypto(symbols: list[str]) -> dict[str, float | None]:
    def fetch_one(symbol: str) -> tuple[str, float | None]:
        try:
            return symbol, fetch_crypto(symbol)["price"]
        except Exception as exc:
            print(f"Warning: could not fetch {symbol}: {exc}", file=sys.stderr)
            return symbol, None

    with ThreadPoolExecutor(max_workers=len(symbols) or 1) as executor:
        return dict(executor.map(fetch_one, symbols))


def _record(asset: str, symbol: str, price_str: str, qty_str: str, trade_type: str) -> int:
    price = _parse_price(price_str)
    qty = parse_quantity(qty_str, integer_only=(asset == "vn"))
    positions = load_positions()

    if trade_type == "buy":
        apply_buy(positions, asset, symbol, qty, price)
    else:
        apply_sell(positions, asset, symbol, qty, price)

    save_positions(positions)

    if asset == "vn":
        qty_str_fmt = str(int(qty))
        price_fmt = format_vnd(price)
    else:
        qty_str_fmt = f"{qty:.8f}".rstrip("0").rstrip(".")
        price_fmt = format_usd(price)

    print(f"{trade_type.upper()} {qty_str_fmt} {symbol.upper()} @ {price_fmt}")
    return 0


def _remove(asset: str, symbol: str, qty_str: str) -> int:
    qty = parse_quantity(qty_str, integer_only=(asset == "vn"))
    positions = load_positions()
    apply_remove(positions, asset, symbol, qty)
    save_positions(positions)
    qty_fmt = str(int(qty)) if asset == "vn" else f"{qty:.8f}".rstrip("0").rstrip(".")
    print(f"Removed {qty_fmt} {symbol.upper()}.")
    return 0


def _pnl_pct(upnl: float, cost: float) -> str:
    if cost == 0:
        return "N/A"
    pct = upnl / cost * 100
    sign = "+" if pct >= 0 else ""
    return f"{sign}{pct:.2f}%"


def _print_section_vnd(holdings: list[dict], realized_pnl: float) -> None:
    print(f"{'SYMBOL':<6}  {'QTY':>10}  {'AVG COST':>16}  {'LAST':>16}  {'VALUE':>16}  {'UPNL':>14}  {'UPNL%':>8}")
    total_cost = 0.0
    total_value = 0.0
    total_upnl = 0.0

    for h in holdings:
        cost = h["avgCost"] * h["quantity"]
        last = format_vnd(h["lastPrice"]) if h["lastPrice"] is not None else "N/A"
        upnl_fmt = format_vnd(h["unrealizedPnl"])
        pct = _pnl_pct(h["unrealizedPnl"], cost)
        print(
            f"{h['symbol']:<6}  "
            f"{int(h['quantity']):>10}  "
            f"{format_vnd(h['avgCost']):>16}  "
            f"{last:>16}  "
            f"{format_vnd(h['marketValue']):>16}  "
            f"{upnl_fmt:>14}  "
            f"{pct:>8}"
        )
        total_cost += cost
        total_value += h["marketValue"]
        total_upnl += h["unrealizedPnl"]

    total_pct = _pnl_pct(total_upnl, total_cost)
    print(
        f"\nRealized: {format_vnd(realized_pnl)}  "
        f"Unrealized: {format_vnd(total_upnl)} ({total_pct})  "
        f"Total: {format_vnd(realized_pnl + total_upnl)}"
    )


def _print_section_usd(holdings: list[dict], realized_pnl: float) -> None:
    print(f"{'SYMBOL':<6}  {'QTY':>12}  {'AVG COST':>11}  {'LAST':>11}  {'VALUE':>11}  {'UPNL':>11}  {'UPNL%':>8}")
    total_cost = 0.0
    total_upnl = 0.0

    for h in holdings:
        cost = h["avgCost"] * h["quantity"]
        qty_str = f"{h['quantity']:.8f}".rstrip("0").rstrip(".")
        last = format_usd(h["lastPrice"]) if h["lastPrice"] is not None else "N/A"
        pct = _pnl_pct(h["unrealizedPnl"], cost)
        print(
            f"{h['symbol']:<6}  "
            f"{qty_str:>12}  "
            f"{format_usd(h['avgCost']):>11}  "
            f"{last:>11}  "
            f"{format_usd(h['marketValue']):>11}  "
            f"{format_usd(h['unrealizedPnl']):>11}  "
            f"{pct:>8}"
        )
        total_cost += cost
        total_upnl += h["unrealizedPnl"]

    total_pct = _pnl_pct(total_upnl, total_cost)
    print(
        f"\nRealized: {format_usd(realized_pnl)}  "
        f"Unrealized: {format_usd(total_upnl)} ({total_pct})  "
        f"Total: {format_usd(realized_pnl + total_upnl)}"
    )


def _build_holdings(positions: dict, asset: str, live_prices: dict[str, float | None]) -> tuple[list[dict], float]:
    holdings = []
    realized_pnl = 0.0

    for pos in sorted(positions.values(), key=lambda p: p["symbol"]):
        if pos["asset"] != asset or pos["quantity"] < 1e-9:
            continue
        realized_pnl += pos["realizedPnl"]
        last_price = live_prices.get(pos["symbol"])
        effective = pos["avgCost"] if last_price is None else float(last_price)
        mv = effective * pos["quantity"]
        upnl = mv - pos["avgCost"] * pos["quantity"]
        holdings.append({
            "symbol": pos["symbol"],
            "quantity": pos["quantity"],
            "avgCost": pos["avgCost"],
            "lastPrice": last_price,
            "marketValue": mv,
            "unrealizedPnl": upnl,
        })

    return holdings, realized_pnl


def show_all_portfolio() -> int:
    positions = load_positions()
    active = [p for p in positions.values() if p.get("quantity", 0) > 1e-9]
    if not active:
        print("Portfolio is empty.")
        return 0

    vn_syms = [p["symbol"] for p in active if p["asset"] == "vn"]
    crypto_syms = [p["symbol"] for p in active if p["asset"] == "crypto"]
    has_gold = any(p["asset"] == "gold" for p in active)

    vn_prices: dict[str, float | None] = {}
    crypto_prices: dict[str, float | None] = {}
    gold_prices: dict[str, float | None] = {}

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {}
        if vn_syms:
            futures["vn"] = executor.submit(fetch_live_prices_vn, vn_syms)
        if crypto_syms:
            futures["crypto"] = executor.submit(fetch_live_prices_crypto, crypto_syms)
        if has_gold:
            futures["gold"] = executor.submit(lambda: {"GOLD": fetch_fstock("GC=F")["price"]})

        for key, future in futures.items():
            try:
                result = future.result()
                if key == "vn":
                    vn_prices = result
                elif key == "crypto":
                    crypto_prices = result
                elif key == "gold":
                    gold_prices = result
            except Exception as exc:
                print(f"Warning: {key} prices unavailable: {exc}", file=sys.stderr)

    sections = []
    vn_holdings, vn_realized = _build_holdings(positions, "vn", vn_prices)
    if vn_holdings:
        sections.append(("VN STOCKS (VND)", _print_section_vnd, vn_holdings, vn_realized))

    crypto_holdings, crypto_realized = _build_holdings(positions, "crypto", crypto_prices)
    if crypto_holdings:
        sections.append(("CRYPTO (USD)", _print_section_usd, crypto_holdings, crypto_realized))

    gold_holdings, gold_realized = _build_holdings(positions, "gold", gold_prices)
    if gold_holdings:
        sections.append(("GOLD (USD)", _print_section_usd, gold_holdings, gold_realized))

    if not sections:
        print("Portfolio is empty.")
        return 0

    for i, (title, print_fn, holdings, realized) in enumerate(sections):
        if i > 0:
            print()
        print(f"=== {title} ===")
        print_fn(holdings, realized)

    return 0


def main() -> int:
    args = sys.argv[1:]
    if not args or args[0] in {"help", "--help", "-h"}:
        _usage_stock()
        return 0 if args else 1

    try:
        if args[0] in {"buy", "sell"}:
            if len(args) != 4:
                _usage_stock()
                return 1
            return _record("vn", args[1], args[2], args[3], args[0])

        if args[0] == "remove":
            if len(args) != 3:
                _usage_stock()
                return 1
            return _remove("vn", args[1], args[2])

        if len(args) == 1:
            return show_quote_vn(args[0])
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1

    _usage_stock()
    return 1


def stockvn_main() -> int:
    args = sys.argv[1:]
    if not args or args[0] in {"help", "--help", "-h"}:
        print("Usage:\n  stockvn <symbol>")
        return 0 if args else 1
    try:
        if len(args) == 1:
            return show_quote_vn(args[0])
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print("Usage:\n  stockvn <symbol>")
    return 1


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


def gold_main() -> int:
    args = sys.argv[1:]

    try:
        if not args:
            result = fetch_fstock("GC=F")
            print(f"Gold: {format_usd(result['price'])}/oz")
            return 0

        if args[0] in {"help", "--help", "-h"}:
            _usage_gold()
            return 0

        if args[0] in {"buy", "sell"}:
            if len(args) != 3:
                _usage_gold()
                return 1
            return _record("gold", "GOLD", args[1], args[2], args[0])

        if args[0] == "remove":
            if len(args) != 2:
                _usage_gold()
                return 1
            return _remove("gold", "GOLD", args[1])
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1

    _usage_gold()
    return 1


def crypto_main() -> int:
    args = sys.argv[1:]
    if not args or args[0] in {"help", "--help", "-h"}:
        _usage_crypto()
        return 0 if args else 1

    try:
        if args[0] in {"buy", "sell"}:
            if len(args) != 4:
                _usage_crypto()
                return 1
            return _record("crypto", args[1], args[2], args[3], args[0])

        if args[0] == "remove":
            if len(args) != 3:
                _usage_crypto()
                return 1
            return _remove("crypto", args[1], args[2])

        if len(args) == 1:
            return show_crypto(args[0])
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1

    _usage_crypto()
    return 1


def port_mine_main() -> int:
    args = sys.argv[1:]

    try:
        if not args:
            return show_all_portfolio()

        if args[0] in {"help", "--help", "-h"}:
            _usage_mine()
            return 0

        if args[0] == "clear":
            save_positions({})
            print("Portfolio cleared.")
            return 0

        if args[0] == "remove":
            if len(args) != 3:
                _usage_mine()
                return 1
            asset_map = {"vn": "vn", "crypto": "crypto", "gold": "gold"}
            symbol = args[1].upper()
            qty_str = args[2]
            asset = "gold" if symbol == "GOLD" else ("vn" if symbol.isalpha() and len(symbol) <= 5 else "crypto")
            return _remove(asset, symbol, qty_str)
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1

    _usage_mine()
    return 1


def help_main() -> int:
    _usage_all()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
