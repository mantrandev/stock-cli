from __future__ import annotations

import json
from urllib.error import HTTPError
from urllib.request import Request, urlopen


YAHOO_CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"


def fetch_fstock(symbol: str) -> dict:
    normalized = symbol.strip().upper()
    request = Request(
        YAHOO_CHART_URL.format(symbol=normalized),
        headers={"Accept": "application/json", "User-Agent": "Mozilla/5.0"},
    )
    try:
        with urlopen(request, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        if exc.code == 404:
            raise RuntimeError(f"Symbol not found: {normalized}") from exc
        raise

    result = data.get("chart", {}).get("result")
    if not result:
        error = data.get("chart", {}).get("error") or {}
        raise RuntimeError(f"No price found for {normalized}: {error.get('description', 'symbol not found')}")

    meta = result[0]["meta"]
    return {
        "symbol": meta.get("symbol", normalized),
        "exchange": meta.get("fullExchangeName", ""),
        "price": float(meta["regularMarketPrice"]),
        "currency": meta.get("currency", "USD"),
    }
