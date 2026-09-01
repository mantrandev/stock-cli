from __future__ import annotations

import json
import time
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


DNSE_OHLC_URL = "https://services.entrade.com.vn/chart-api/v2/ohlcs/stock"
PRICE_UNIT = 1000.0
LOOKBACK_DAYS = 30


def _load_quote_payload(symbol: str) -> dict:
    now = int(time.time())
    query = urlencode(
        {
            "symbol": symbol,
            "from": now - LOOKBACK_DAYS * 86400,
            "to": now,
            "resolution": "1D",
        }
    )
    request = Request(
        f"{DNSE_OHLC_URL}?{query}",
        headers={"Accept": "application/json", "User-Agent": "StockCLI/0.4"},
    )
    try:
        with urlopen(request, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        if exc.code == 400:
            raise RuntimeError(f"Symbol not found: {symbol}") from exc
        raise


def fetch_quote(symbol: str) -> dict:
    normalized = symbol.strip().upper()
    payload = _load_quote_payload(normalized)

    closes = payload.get("c")
    if not closes:
        raise RuntimeError(f"No price returned for {normalized}.")

    try:
        price = float(closes[-1]) * PRICE_UNIT
    except (TypeError, ValueError) as exc:
        raise RuntimeError(f"Could not read a usable price for {normalized}.") from exc

    if price <= 0:
        raise RuntimeError(f"Could not read a usable price for {normalized}.")

    return {"symbol": normalized, "price": price}
