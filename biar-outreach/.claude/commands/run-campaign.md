---
description: Полный прогон аутрич-пайплайна BIAR от списка лидов до превью писем (DRY_RUN).
argument-hint: "[путь к csv лидов, по умолчанию sample-leads.csv]"
---

# Команда: run-campaign

Прогони весь пайплайн BIAR Outreach по шагам. Источник лидов: `$1` (если пусто —
`sample-leads.csv`). Отправки нет — работаем в DRY_RUN.

## Шаги
1. **Загрузка лидов** — `load_from_csv($1)` (по умолчанию `sample-leads.csv`).
   Покажи оператору, сколько точек загружено.
2. **Скоринг** — скилл `score-icp` → `outputs/horeca-scored.csv` (тиры A/B/C).
3. **Контакты** — скилл `find-contacts` → `outputs/contacts.csv`. Точки без email
   помечаются `needs_contact` и в отправку не идут.
4. **Письма** — скилл `write-sequence`: серии под тир, персонализация `ru-copywriter`,
   обязательный аудит `legal-auditor` → `outputs/email-sequences.md`.
5. **Деплой** — скилл `deploy-campaign`: **спроси подтверждение**, затем `build_campaign`
   + `activate` в DRY_RUN. Реальной рассылки нет.

## Итог оператору
Сводка: сколько точек по тирам, сколько готовых писем, путь к превью
`outputs/email-sequences.md`. Напомни: для реальной отправки нужны ESP + `DRY_RUN=false`.
