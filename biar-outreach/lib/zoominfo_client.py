"""ZoomInfo B2B intelligence client для BIAR Outreach.

Обогащает лиды данными о контактах, должностях и компаниях через ZoomInfo API.
Конфигурация находится в ../.zoominfo.config.json
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import List, Dict, Optional

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except Exception:
    pass


class ZoomInfoConfig:
    """Загружает и кэширует конфигурацию ZoomInfo."""

    def __init__(self, config_path: str | Path = ".zoominfo.config.json"):
        self.config_path = Path(config_path)
        self._data: Dict = {}
        if self.config_path.exists():
            with self.config_path.open(encoding="utf-8") as f:
                self._data = json.load(f)

    @property
    def company_name(self) -> str:
        return self._data.get("company", {}).get("name", "КВИС ТРЕЙД")

    @property
    def company_email(self) -> str:
        return self._data.get("company", {}).get("email", "im@kvistrade.com")

    @property
    def target_industries(self) -> List[str]:
        return self._data.get("targetMarket", {}).get("industries", [])

    @property
    def target_job_titles(self) -> List[str]:
        return self._data.get("targetMarket", {}).get("jobTitles", [])

    @property
    def products(self) -> List[Dict]:
        return self._data.get("products", [])

    def get_tier_filter(self, tier: str) -> Dict:
        """Возвращает фильтры для ZoomInfo поиска по тиру."""
        product_ids = [p["id"] for p in self.products if p.get("tier") == tier]
        return {
            "tier": tier,
            "product_ids": product_ids,
            "targetSegments": [seg for p in self.products if p.get("tier") == tier
                              for seg in p.get("targetSegments", [])]
        }


class ZoomInfoClient:
    """Клиент для запросов к ZoomInfo API.

    Реализация зависит от конкретного REST API или SDK ZoomInfo.
    Текущий вариант — заготовка для интеграции.
    """

    def __init__(self, api_key: Optional[str] = None, account_id: Optional[str] = None):
        self.api_key = api_key or os.getenv("ZOOMINFO_API_KEY", "")
        self.account_id = account_id or os.getenv("ZOOMINFO_ACCOUNT_ID", "")
        self.config = ZoomInfoConfig()

        if not self.api_key:
            raise RuntimeError(
                "ZoomInfo API ключ не найден. "
                "Установите ZOOMINFO_API_KEY в .env."
            )

    def search_decision_makers(
        self,
        industry: str,
        job_titles: List[str],
        country: str = "RU",
        limit: int = 100
    ) -> List[Dict]:
        """Ищет decision makers в целевой индустрии.

        TODO: реальная реализация с вызовом ZoomInfo API.
        Сейчас возвращает заготовку для демонстрации структуры.
        """
        if not self.api_key:
            raise RuntimeError(
                f"ZoomInfo API выключен (ключ пуст). "
                f"Поставьте ZOOMINFO_API_KEY в .env."
            )

        # Placeholder для демонстрации структуры результата
        return [
            {
                "id": "contact_123",
                "firstName": "Пример",
                "lastName": "Контакт",
                "email": "contact@example.com",
                "phone": "+7 999 123-45-67",
                "jobTitle": "General Manager",
                "department": "Operations",
                "companyName": "Пример Ресторана ООО",
                "companyIndustry": industry,
                "confidence": 0.85,
                "lastUpdated": "2026-07-09",
            }
        ]

    def enrich_lead(
        self,
        company_name: str,
        city: Optional[str] = None
    ) -> Dict:
        """Обогащает лид данными компании и контактов.

        Args:
            company_name: Название заведения/компании для поиска
            city: Город поиска (опционально, но помогает точности)

        Returns:
            Словарь с данными компании, контактами и confidence score.
        """
        if not self.api_key:
            raise RuntimeError(
                f"ZoomInfo API выключен. Установите ZOOMINFO_API_KEY в .env."
            )

        # TODO: реальный вызов ZoomInfo API
        # Сейчас возвращаем заготовку
        return {
            "company": {
                "name": company_name,
                "city": city or "Unknown",
                "industry": "Hospitality & Food Service",
                "founded": "Unknown",
                "employees": "Unknown",
            },
            "contacts": [],
            "confidence": 0.0,
            "dataQuality": "placeholder"
        }

    def search_by_filter(
        self,
        tier: str,
        city: Optional[str] = None,
        exclude_keywords: Optional[List[str]] = None
    ) -> List[Dict]:
        """Поиск лидов по фильтрам для конкретного тира продукции.

        Args:
            tier: 'A' (премиум красные), 'B' (белые/игристые), 'C' (крепкие)
            city: Город фокуса (опционально)
            exclude_keywords: Слова для исключения из поиска

        Returns:
            Список найденных лидов с enriched данными.
        """
        tier_filter = self.config.get_tier_filter(tier)
        # TODO: реальный поиск через ZoomInfo API
        return []


def load_config() -> ZoomInfoConfig:
    """Утилита для загрузки конфигурации из корня biar-outreach."""
    project_dir = Path(__file__).resolve().parent.parent
    return ZoomInfoConfig(project_dir / ".zoominfo.config.json")


if __name__ == "__main__":
    # Демонстрация загрузки конфигурации
    try:
        config = load_config()
        print(f"Компания: {config.company_name}")
        print(f"Email: {config.company_email}")
        print(f"Целевые индустрии: {config.target_industries}")
        print(f"Целевые должности: {config.target_job_titles}")
        print("\nПродукты:")
        for product in config.products:
            print(f"  - {product['name']} (tier {product['tier']}): {product['description']}")
    except Exception as e:
        print(f"Ошибка загрузки конфигурации: {e}")
