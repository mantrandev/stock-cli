from __future__ import annotations

import json
from pathlib import Path


DB_PATH = Path.home() / ".stocklocal"


def load_positions() -> dict:
    if not DB_PATH.exists():
        return {}
    data = json.loads(DB_PATH.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def save_positions(positions: dict) -> None:
    DB_PATH.write_text(json.dumps(positions, indent=2) + "\n", encoding="utf-8")
