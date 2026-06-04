from __future__ import annotations

import json
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen


CMC_QUOTES_URL = (
    "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
    "?symbol={symbol}&convert=USD"
)
CONFIG_PATH = Path.home() / ".stockcli" / "config.json"


def _load_api_key() -> str:
    if not CONFIG_PATH.exists():
        raise RuntimeError(
            f"CoinMarketCap API key missing: create {CONFIG_PATH} "
            'with {"cmc_api_key": "<your-key>"}'
        )
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    key = config.get("cmc_api_key")
    if not key:
        raise RuntimeError(f'Set "cmc_api_key" in {CONFIG_PATH}')
    return key


def fetch_crypto(symbol: str) -> dict:
    normalized = symbol.strip().upper()
    request = Request(
        CMC_QUOTES_URL.format(symbol=normalized),
        headers={
            "Accept": "application/json",
            "User-Agent": "StockCLI/0.3",
            "X-CMC_PRO_API_KEY": _load_api_key(),
        },
    )
    try:
        with urlopen(request, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        body = json.loads(exc.read().decode("utf-8"))
        message = body.get("status", {}).get("error_message", str(exc))
        raise RuntimeError(f"No price found for {normalized}: {message}") from exc

    entry = data.get("data", {}).get(normalized)
    if isinstance(entry, list):
        entry = entry[0] if entry else None
    if not entry:
        raise RuntimeError(f"No price found for {normalized}")

    return {
        "symbol": normalized,
        "pair": f"{normalized}/USD",
        "price": float(entry["quote"]["USD"]["price"]),
    }
