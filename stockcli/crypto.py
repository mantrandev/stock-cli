from __future__ import annotations

import json
from urllib.error import HTTPError
from urllib.request import Request, urlopen


BINANCE_PRICE_URL = "https://api.binance.com/api/v3/ticker/price?symbol={pair}"


def fetch_crypto(symbol: str) -> dict:
    normalized = symbol.strip().upper()
    pair = f"{normalized}USDT"
    request = Request(
        BINANCE_PRICE_URL.format(pair=pair),
        headers={"Accept": "application/json", "User-Agent": "StockCLI/0.2"},
    )
    try:
        with urlopen(request, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        body = json.loads(exc.read().decode("utf-8"))
        raise RuntimeError(f"No price found for {normalized}: {body.get('msg', str(exc))}") from exc

    return {
        "symbol": normalized,
        "pair": pair,
        "price": float(data["price"]),
    }
