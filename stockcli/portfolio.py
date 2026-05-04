from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4


def normalize_symbol(symbol: str) -> str:
    if not isinstance(symbol, str) or not symbol.strip():
        raise ValueError("Symbol is required.")
    return symbol.strip().upper()


def parse_share_amount(value: str | int) -> int:
    try:
        amount = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("Amount must be a positive integer.") from exc

    if amount <= 0 or str(amount) != str(value).strip():
        raise ValueError("Amount must be a positive integer.")
    return amount


def format_vnd(value: float | int) -> str:
    return f"{round(value):,} VND"


def create_trade(
    trade_type: str,
    symbol: str,
    shares: int,
    price: float,
    executed_at: str | None = None,
) -> dict:
    if trade_type not in {"buy", "sell"}:
        raise ValueError("Trade type must be buy or sell.")
    if price <= 0:
        raise ValueError("Price must be positive.")

    return {
        "id": uuid4().hex,
        "type": trade_type,
        "symbol": normalize_symbol(symbol),
        "shares": parse_share_amount(shares),
        "price": float(price),
        "executedAt": executed_at or datetime.now(timezone.utc).isoformat(),
    }


@dataclass
class Position:
    symbol: str
    shares: int = 0
    cost: float = 0.0


def summarize_portfolio(trades: list[dict], live_prices: dict[str, float | None] | None = None) -> dict:
    live_prices = live_prices or {}
    positions: dict[str, Position] = {}
    realized_pnl = 0.0

    for trade in trades:
        symbol = normalize_symbol(trade["symbol"])
        position = positions.setdefault(symbol, Position(symbol=symbol))
        shares = parse_share_amount(trade["shares"])
        price = float(trade["price"])

        if trade["type"] == "buy":
            position.shares += shares
            position.cost += shares * price
        elif trade["type"] == "sell":
            if position.shares < shares:
                raise ValueError(f"Not enough shares to sell {symbol}.")
            average_cost = position.cost / position.shares
            realized_pnl += (price - average_cost) * shares
            position.shares -= shares
            position.cost -= average_cost * shares
            if position.shares == 0:
                position.cost = 0.0
        else:
            raise ValueError(f"Unsupported trade type: {trade['type']}")

    holdings = []
    unrealized_pnl = 0.0
    market_value = 0.0

    for position in sorted(positions.values(), key=lambda item: item.symbol):
        if position.shares == 0:
            continue

        average_cost = position.cost / position.shares
        last_price = live_prices.get(position.symbol)
        effective_price = average_cost if last_price is None else float(last_price)
        holding_market_value = effective_price * position.shares
        holding_unrealized_pnl = holding_market_value - position.cost

        market_value += holding_market_value
        unrealized_pnl += holding_unrealized_pnl
        holdings.append(
            {
                "symbol": position.symbol,
                "shares": position.shares,
                "averageCost": average_cost,
                "lastPrice": last_price,
                "marketValue": holding_market_value,
                "unrealizedPnl": holding_unrealized_pnl,
            }
        )

    return {
        "holdings": holdings,
        "marketValue": market_value,
        "realizedPnl": realized_pnl,
        "unrealizedPnl": unrealized_pnl,
        "totalPnl": realized_pnl + unrealized_pnl,
    }
