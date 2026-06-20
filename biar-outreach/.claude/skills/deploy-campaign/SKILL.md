---
name: deploy-campaign
description: Деплоит кампанию через ESP. По умолчанию DRY_RUN — реально не шлёт. Используй последним шагом, только после подтверждения оператора.
---

# Скилл: deploy-campaign

Финальный шаг. На 🟢-старте работает в DRY_RUN — отправки нет, только превью.

## Шаги
1. Убедись, что есть `outputs/contacts.csv` и `outputs/email-sequences.md`.
2. **Спроси подтверждение оператора** перед любым деплоем.
3. Вызови `lib/sender_client.build_campaign(contacts, sequences_md)` → превью.
4. Вызови `lib/sender_client.activate(contacts)`:
   - `DRY_RUN=true` (по умолчанию) → ничего не отправляется, возвращается отчёт.
   - реальная отправка только при `DRY_RUN=false` + настроенном ESP (`4-sending-notes.md`).
5. Сообщи оператору итог и путь к превью.

## Результат
В DRY_RUN: превью `outputs/email-sequences.md` + отчёт «0 отправлено». Реальная рассылка —
осознанно, после настройки ESP, SPF/DKIM и проверки писем.
