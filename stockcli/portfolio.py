from __future__ import annotations

ASSET_TYPES = {"vn", "crypto", "gold"}
ASSET_CURRENCIES = {"vn": "VND", "crypto": "USD", "gold": "USD"}


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


def parse_quantity(value: str | float | int, integer_only: bool = False) -> float:
    if integer_only:
        return float(parse_share_amount(value))
    try:
        qty = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("Quantity must be a positive number.") from exc
    if qty <= 0:
        raise ValueError("Quantity must be positive.")
    return qty


def format_vnd(value: float | int) -> str:
    return f"{round(value):,} VND"


def format_usd(value: float) -> str:
    return f"${value:,.2f}"


def _key(asset: str, symbol: str) -> str:
    return f"{asset}:{symbol}"


def apply_buy(positions: dict, asset: str, symbol: str, qty: float, price: float) -> None:
    symbol = normalize_symbol(symbol)
    key = _key(asset, symbol)
    if key not in positions:
        positions[key] = {
            "asset": asset,
            "symbol": symbol,
            "quantity": 0.0,
            "avgCost": 0.0,
            "currency": ASSET_CURRENCIES[asset],
            "realizedPnl": 0.0,
        }
    pos = positions[key]
    total_cost = pos["quantity"] * pos["avgCost"] + qty * price
    pos["quantity"] += qty
    pos["avgCost"] = total_cost / pos["quantity"]


def apply_sell(positions: dict, asset: str, symbol: str, qty: float, price: float) -> None:
    symbol = normalize_symbol(symbol)
    key = _key(asset, symbol)
    pos = positions.get(key)
    if pos is None or pos["quantity"] < qty - 1e-9:
        raise ValueError(f"Not enough {symbol} to sell.")
    pos["realizedPnl"] += (price - pos["avgCost"]) * qty
    pos["quantity"] -= qty
    if pos["quantity"] < 1e-9:
        pos["quantity"] = 0.0


def apply_remove(positions: dict, asset: str, symbol: str, qty: float) -> None:
    symbol = normalize_symbol(symbol)
    key = _key(asset, symbol)
    pos = positions.get(key)
    if pos is None or pos["quantity"] < qty - 1e-9:
        raise ValueError(f"Not enough {symbol} to remove.")
    pos["quantity"] -= qty
    if pos["quantity"] < 1e-9:
        del positions[key]
