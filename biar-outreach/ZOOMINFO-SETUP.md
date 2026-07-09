# ZoomInfo Plugin — Настройка для КВИС ТРЕЙД

## Обзор

ZoomInfo — B2B платформа для поиска и обогащения контактов decision makers в целевых компаниях.
Конфигурация настроена специально для КВИС ТРЕЙД и интегрируется в пайплайн холодного аутрича.

## Конфигурация (`.zoominfo.config.json`)

### Компания
```json
{
  "company": {
    "name": "КВИС ТРЕЙД",
    "email": "im@kvistrade.com",
    "phone": "+7 916 243-23-96",
    "website": "https://vina-bolgarii.ru"
  }
}
```

### Продукты (3 тира)

| Тир | Продукт | Категория | Целевой сегмент |
|-----|---------|-----------|-----------------|
| **A** | Katarzyna Estate | Премиальные красные вина | Fine-dining, Винотеки, Премиум-рестораны |
| **B** | Black Sea Gold | Белые, игристые, мускаты | Винные бары, Рестораны со средней картой |
| **C** | SIS Industries | Крепкие: бренди, ракия, дистилляты | Бары, Дистрибьюторы, Опт |

### Целевой рынок

- **Страна**: Россия (RU)
- **Язык**: Русский
- **Индустрии**: Рестораны, винотеки, бары, дистрибьюторы, отели
- **Размер компании**: 10–1000 сотрудников
- **Должности**: Buyer, Sommelier, Wine Director, Restaurant Manager, Owner

### Географический фокус

**Приоритетные города**:
- Москва
- Санкт-Петербург
- Екатеринбург
- Сочи
- Казань

## Как использовать

### 1. Получить ZoomInfo API ключ

1. Авторизуйтесь в [ZoomInfo](https://www.zoominfo.com)
2. Перейдите в Settings → API & Integrations
3. Создайте API ключ и скопируйте его
4. (Опционально) Найдите Account ID в профиле

### 2. Сохранить ключ в `.env`

Скопируйте `.env.example` в `.env`:
```bash
cp .env.example .env
```

Заполните ZoomInfo ключи:
```env
ZOOMINFO_API_KEY=your_actual_api_key_here
ZOOMINFO_ACCOUNT_ID=your_account_id_here
```

**ВАЖНО**: `.env` в `.gitignore` — никогда не коммитить реальные ключи в репозиторий.

### 3. Использовать в коде

```python
from lib.zoominfo_client import ZoomInfoClient, load_config

# Загрузить конфигурацию
config = load_config()
print(f"Компания: {config.company_name}")
print(f"Продукты: {[p['name'] for p in config.products]}")

# Инициализировать клиент (использует ZOOMINFO_API_KEY из .env)
client = ZoomInfoClient()

# Найти decision makers для Тира A (премиальные красные вина)
tier_a_leads = client.search_decision_makers(
    industry="Restaurants & Hospitality",
    job_titles=["General Manager", "Sommelier", "Wine Director"]
)

# Обогатить лид компании (найти контакты, email, телефон)
enriched = client.enrich_lead(
    company_name="Пример Ресторана",
    city="Москва"
)

# Поиск по специфическому тиру продукции
tier_leads = client.search_by_filter(
    tier="A",  # премиум красные вина
    city="Москва",
    exclude_keywords=["mass-market", "budget"]
)
```

## Интеграция в пайплайн

### Текущий статус

- ✅ Конфигурация создана и настроена
- ✅ Python клиент подготовлен (заготовка)
- ❌ ZoomInfo API интеграция в статусе TODO (зависит от реального подключения к ZoomInfo)
- ❌ Автоматический поиск лидов еще не включен

### Включить ZoomInfo как источник лидов

В `lib/leads_client.py` добавить функцию:

```python
def search_zoominfo(tier: str = "all", city: str = "Moscow") -> List[Dict[str, str]]:
    """Поиск лидов через ZoomInfo. Требует ZOOMINFO_API_KEY в .env."""
    from lib.zoominfo_client import ZoomInfoClient
    
    client = ZoomInfoClient()
    
    if tier == "all":
        tiers = ["A", "B", "C"]
    else:
        tiers = [tier]
    
    all_leads = []
    for t in tiers:
        leads = client.search_by_filter(tier=t, city=city)
        all_leads.extend(leads)
    
    # Преобразовать в формат FIELDS для совместимости с пайплайном
    return [
        {
            "name": lead["companyName"],
            "type": "restaurant/bar",
            "city": city,
            "segment": "horeca",
            "contact_name": lead.get("firstName", ""),
            "email": lead.get("email", ""),
            "phone": lead.get("phone", ""),
            "notes": f"Найден через ZoomInfo, должность: {lead.get('jobTitle', '')}",
        }
        for lead in all_leads
    ]
```

## Качество данных

### Confidence Score

ZoomInfo возвращает **confidence score** (0.0 — 1.0) для каждого контакта.
В конфигурации установлено минимальное пороговое значение:

```json
"enrichmentSettings": {
  "minConfidenceScore": 0.75
}
```

Это значит, что фильтруются контакты с confidence < 75%.

### Поля обогащения

Включены:
- ✅ Email адреса лиц
- ✅ Номера телефонов
- ✅ Информация о должности
- ✅ Название компании
- ✅ Social media профили компании

Исключены (для оптимизации затрат):
- ❌ Информация о финансировании
- ❌ Используемые технологии

## Примеры поиска

### Найти сомелье в Москве
```python
client = ZoomInfoClient()
decision_makers = client.search_decision_makers(
    industry="Restaurants & Hospitality",
    job_titles=["Sommelier", "Wine Director"],
    country="RU",
    limit=50
)
```

### Обогатить лид по названию ресторана
```python
enriched = client.enrich_lead(
    company_name="Ресторан Черная Икра",
    city="Москва"
)
```

### Найти целевые точки для конкретного тира продукции
```python
# Для премиальных красных вин (Katarzyna Estate)
katarzyna_prospects = client.search_by_filter(
    tier="A",
    city="Москва",
    exclude_keywords=["mass-market", "discount"]
)
```

## Стоимость и лимиты

ZoomInfo работает по системе **credits** (кредитов):
- Каждый поиск стоит определённое количество кредитов
- Каждое обогащение контакта стоит кредиты
- Дневной/месячный лимит зависит от тарифа

**Рекомендация**: При разработке использовать `DRY_RUN=true` в `.env`, чтобы не расходовать реальные кредиты.

## Troubleshooting

### API ключ не найден
```
RuntimeError: ZoomInfo API ключ не найден. Установите ZOOMINFO_API_KEY в .env.
```

**Решение**: 
1. Скопируйте `.env.example` в `.env`
2. Получите ключ из ZoomInfo dashboard
3. Заполните `ZOOMINFO_API_KEY=your_key_here`

### Пустой результат поиска
- Проверьте, что фильтры совпадают с доступными данными ZoomInfo
- Убедитесь, что у вас достаточно кредитов на аккаунте
- Попробуйте расширить географию или критерии поиска

### Низкий confidence score
- Это нормально для новых/малых компаний
- Вы можете снизить `minConfidenceScore` в конфигурации, но это может привести к менее точным контактам

## Дополнительные ресурсы

- [ZoomInfo API Documentation](https://api.zoominfo.com/docs)
- [BIAR Outreach CLAUDE.md](./CLAUDE.md) — общее описание пайплайна
- [Критерии скоринга](./1-scoring-criteria.md)
- [Фреймворки писем](./3-copy-frameworks.md)
