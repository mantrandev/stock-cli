from __future__ import annotations

import json
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen


BINANCE_PRICE_URL = "https://api.binance.com/api/v3/ticker/price?symbol={pair}"
CMC_QUOTES_URL = (
    "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
    "?symbol={symbol}&convert=USD"
)
CONFIG_PATH = Path.home() / ".stockcli" / "config.json"


def _load_api_key() -> str | None:
    if not CONFIG_PATH.exists():
        return None
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    return config.get("cmc_api_key") or None


def _fetch_binance(symbol: str) -> float | None:
    request = Request(
        BINANCE_PRICE_URL.format(pair=f"{symbol}USDT"),
        headers={"Accept": "application/json", "User-Agent": "StockCLI/0.4"},
    )
    try:
        with urlopen(request, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        if exc.code == 400:
            return None
        raise
    return float(data["price"])


def _fetch_cmc(symbol: str, api_key: str) -> float:
    request = Request(
        CMC_QUOTES_URL.format(symbol=symbol),
        headers={
            "Accept": "application/json",
            "User-Agent": "StockCLI/0.4",
            "X-CMC_PRO_API_KEY": api_key,
        },
    )
    try:
        with urlopen(request, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        body = json.loads(exc.read().decode("utf-8"))
        message = body.get("status", {}).get("error_message", str(exc))
        raise RuntimeError(f"No price found for {symbol}: {message}") from exc

    entry = data.get("data", {}).get(symbol)
    if isinstance(entry, list):
        entry = entry[0] if entry else None
    if not entry:
        raise RuntimeError(f"No price found for {symbol}")

    return float(entry["quote"]["USD"]["price"])


def fetch_crypto(symbol: str) -> dict:
    normalized = symbol.strip().upper()

    price = _fetch_binance(normalized)
    if price is not None:
        return {"symbol": normalized, "pair": f"{normalized}/USDT", "price": price}

    api_key = _load_api_key()
    if api_key is None:
        raise RuntimeError(
            f"No Binance USDT pair for {normalized}. To resolve it via "
            f'CoinMarketCap, create {CONFIG_PATH} with {{"cmc_api_key": "<your-key>"}}'
        )

    return {
        "symbol": normalized,
        "pair": f"{normalized}/USD",
        "price": _fetch_cmc(normalized, api_key),
    }
