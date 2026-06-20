---
name: write-sequence
description: Пишет персональную серию из 3–4 писем на русском под тир точки (Katarzyna/Black Sea Gold/SIS). Используй после find-contacts.
---

# Скилл: write-sequence

Генерирует серию писем под каждую точку из contacts.csv.

## Шаги
1. Возьми `outputs/contacts.csv` (только точки с рабочим email).
2. Для каждой точки выбери винодельню/серию по тиру (см. `../../3-copy-frameworks.md`):
   A → Katarzyna, B → Black Sea Gold, C → SIS.
3. Сгенерируй 3–4 касания. Первую строку-зацепку делегируй субагенту `ru-copywriter`
   (1 персональная строка под точку из её `notes`).
4. **Обязательно** прогони каждое письмо через субагент `legal-auditor` (ФЗ-38/171 +
   спам-слова, см. `../../0-legal-constraints.md`). Не прошло — переписать.
5. Подставь merge-теги `{{name}}`, `{{contact_name}}`, `{{city}}`. Добавь подпись
   КВИС ТРЕЙД и строку отписки.
6. Собери всё в markdown и передай в `lib/sender_client.build_campaign()` —
   он запишет `outputs/email-sequences.md`.

## Результат
`outputs/email-sequences.md` — готовые персональные серии, прошедшие legal-аудит.
