"""Клиент источников лидов для BIAR Outreach.

🟢-вариант: основной режим — чтение ручного CSV (бесплатно, без сети).
Платный 2ГИС API присутствует как заготовка за флагом USE_2GIS — по умолчанию выключен.
"""
from __future__ import annotations

import csv
import os
from pathlib import Path
from typing import List, Dict

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except Exception:
    pass  # dotenv опционален; без .env работают значения по умолчанию

FIELDS = [
    "name", "type", "city", "segment",
    "has_wine_list", "contact_name", "email", "phone", "notes",
]


def load_from_csv(path: str | Path) -> List[Dict[str, str]]:
    """Прочитать ручной список точек из CSV. Это основной источник лидов."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Список лидов не найден: {path}")
    rows: List[Dict[str, str]] = []
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for raw in reader:
            row = {k: (raw.get(k) or "").strip() for k in FIELDS}
            if not row["name"]:
                continue
            rows.append(row)
    return rows


def search_2gis(city: str, rubric: str) -> List[Dict[str, str]]:
    """Поиск точек через 2ГИС API. Выключен на старте (USE_2GIS=false).

    Когда подключите платный ключ: положите TWOGIS_API_KEY в .env, поставьте
    USE_2GIS=true. Возвращаемый формат совпадает с load_from_csv (поля FIELDS),
    чтобы остальной пайплайн не менялся.
    """
    if os.getenv("USE_2GIS", "false").lower() != "true":
        raise RuntimeError(
            "2ГИС API выключен (USE_2GIS=false). На старте используйте ручной CSV "
            "через load_from_csv(). Чтобы включить — см. 2-leads-sources.md."
        )
    api_key = os.getenv("TWOGIS_API_KEY", "")
    if not api_key:
        raise RuntimeError("USE_2GIS=true, но TWOGIS_API_KEY пуст в .env.")
    # TODO: реальный вызов https://catalog.api.2gis.com/ — реализовать при подключении.
    raise NotImplementedError("Реальный вызов 2ГИС подключается при наличии ключа.")


if __name__ == "__main__":
    import sys
    src = sys.argv[1] if len(sys.argv) > 1 else "sample-leads.csv"
    leads = load_from_csv(src)
    print(f"Загружено лидов: {len(leads)}")
    for lead in leads:
        print(f"  - {lead['name']} ({lead['type']}, {lead['city']}, {lead['segment']})")
