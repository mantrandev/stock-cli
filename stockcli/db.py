from __future__ import annotations

import json
from pathlib import Path


DB_PATH = Path.home() / ".stocklocal"


def ensure_db() -> None:
    if not DB_PATH.exists():
        DB_PATH.write_text(json.dumps({"trades": []}, indent=2) + "\n", encoding="utf-8")


def load_db() -> dict:
    ensure_db()
    payload = json.loads(DB_PATH.read_text(encoding="utf-8"))
    trades = payload.get("trades")
    return {"trades": trades if isinstance(trades, list) else []}


def save_db(db: dict) -> None:
    ensure_db()
    DB_PATH.write_text(json.dumps(db, indent=2) + "\n", encoding="utf-8")


def append_trade(trade: dict) -> None:
    db = load_db()
    db["trades"].append(trade)
    save_db(db)
