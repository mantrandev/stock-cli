from __future__ import annotations

import json
from urllib.parse import quote
from urllib.request import Request, urlopen


VPS_QUOTE_URL = "https://bgapidatafeed.vps.com.vn/getliststockdata/{symbol}"


def _pick_price(row: dict) -> float | None:
    for key in ("closePrice", "lastPrice", "highPrice", "lowPrice", "r"):
        value = row.get(key)
        if value is None:
            continue
        try:
            price = float(value)
        except (TypeError, ValueError):
            continue
        if price > 0:
            return price
    return None


def _load_quote_payload(symbol: str) -> dict:
    request = Request(
        VPS_QUOTE_URL.format(symbol=quote(symbol)),
        headers={
            "Accept": "application/json",
            "User-Agent": "StockCLI/0.2"
        },
    )
    with urlopen(request, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_quote(symbol: str) -> dict:
    normalized = symbol.strip().upper()
    rows = _load_quote_payload(normalized)

    if not isinstance(rows, list) or not rows:
        raise RuntimeError(f"No price returned for {normalized}.")

    row = rows[0]
    price = _pick_price(row)
    if price is None:
        raise RuntimeError(f"Could not read a usable price for {normalized}.")

    return {
        "symbol": str(row.get("sym", normalized)).upper(),
        "exchange": row.get("boardId"),
        "price": price,
    }
