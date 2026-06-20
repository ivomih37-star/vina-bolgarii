"""Клиент списка импортёров для BIAR (модель «импортёры-first»).

🟢-вариант: читает ручной/ресёрч CSV импортёров (бесплатно, без сети).
Образец — lib/leads_client.py (тот же паттерн чтения CSV).
"""
from __future__ import annotations

import csv
from pathlib import Path
from typing import List, Dict

FIELDS = ["name", "focus", "segment", "categories", "regions", "notes", "source"]


def load_importers(path: str | Path = "importers.csv") -> List[Dict[str, str]]:
    """Прочитать список импортёров из CSV (основной источник)."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Список импортёров не найден: {path}")
    rows: List[Dict[str, str]] = []
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for raw in reader:
            row = {k: (raw.get(k) or "").strip() for k in FIELDS}
            if not row["name"]:
                continue
            rows.append(row)
    return rows


if __name__ == "__main__":
    import sys
    src = sys.argv[1] if len(sys.argv) > 1 else "importers.csv"
    importers = load_importers(src)
    print(f"Загружено импортёров: {len(importers)}")
    for imp in importers:
        print(f"  - {imp['name']} ({imp['focus']}, {imp['segment']})")
