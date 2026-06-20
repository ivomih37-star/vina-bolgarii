"""Клиент рассылки для BIAR Outreach.

🟢-вариант: по умолчанию DRY_RUN=true — реально ничего не отправляем, только
собираем кампанию и пишем превью в outputs/. Реальный адаптер ESP (Unisender/Sendsay)
включается осознанно через DRY_RUN=false + ESP_API_KEY.
"""
from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except Exception:
    pass

OUTPUTS = Path(__file__).resolve().parent.parent / "outputs"


def build_campaign(contacts: List[Dict[str, str]], sequences_md: str) -> Path:
    """Собрать кампанию и записать превью писем в outputs/email-sequences.md.

    contacts: список точек с тиром и email (из contacts.csv).
    sequences_md: готовый markdown с сериями писем (из write-sequence).
    Возвращает путь к файлу превью. Сети не касается.
    """
    OUTPUTS.mkdir(exist_ok=True)
    preview = OUTPUTS / "email-sequences.md"
    header = (
        f"# Превью кампании BIAR — {datetime.now():%Y-%m-%d %H:%M}\n\n"
        f"Получателей: {len(contacts)}. Режим: "
        f"{'DRY_RUN (отправки нет)' if _dry_run() else 'LIVE'}\n\n---\n\n"
    )
    preview.write_text(header + sequences_md, encoding="utf-8")
    return preview


def activate(contacts: List[Dict[str, str]]) -> Dict[str, object]:
    """«Активировать» кампанию. В DRY_RUN только логирует, реально не шлёт."""
    if _dry_run():
        return {
            "sent": 0,
            "dry_run": True,
            "message": (
                f"DRY_RUN=true — {len(contacts)} писем НЕ отправлено. "
                "Проверьте outputs/email-sequences.md. Для реальной отправки "
                "настройте ESP и поставьте DRY_RUN=false (см. 4-sending-notes.md)."
            ),
        }
    api_key = os.getenv("ESP_API_KEY", "")
    if not api_key:
        raise RuntimeError("DRY_RUN=false, но ESP_API_KEY пуст в .env.")
    # TODO: реальный вызов Unisender/Sendsay API — реализовать при подключении ESP.
    raise NotImplementedError("Реальная отправка подключается при наличии ESP-ключа.")


def _dry_run() -> bool:
    return os.getenv("DRY_RUN", "true").lower() != "false"


if __name__ == "__main__":
    demo = [{"name": "Probka Wine Bar", "email": "", "tier": "A"}]
    path = build_campaign(demo, "## Демо\nПример серии писем.\n")
    print(f"Превью записано: {path}")
    print(activate(demo)["message"])
