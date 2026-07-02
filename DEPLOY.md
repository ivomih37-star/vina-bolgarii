# Публикация сайта kvistrade.ru

Пошаговый план развёртывания на **Cloudflare Pages** с доменом
`kvistrade.ru`. Затраты: **0 ₽/мес** сверх уже купленного домена.

## Архитектура

```
[ Посетитель ]
       │  https://kvistrade.ru
       ▼
[ Cloudflare DNS + CDN ]
       │
       ▼
[ Cloudflare Pages ]  ◀── auto-deploy ──  GitHub (ivomih37-star/vina-bolgarii, ветка main)

info@kvistrade.ru  →  [ Cloudflare Email Routing ]  →  kvistrade@gmail.com
```

| Компонент       | Сервис                  | Цена         |
| --------------- | ----------------------- | ------------ |
| Домен           | (уже куплен)            | ~600 ₽/год   |
| Хостинг         | Cloudflare Pages        | бесплатно    |
| DNS             | Cloudflare DNS          | бесплатно    |
| TLS-сертификат  | Cloudflare (Let's Enc.) | бесплатно    |
| Почта (форвард) | Cloudflare Email Routing| бесплатно    |
| CDN / DDoS      | Cloudflare              | бесплатно    |

---

## Этап 0. Что уже готово в репо

- [x] `index.html` собран и закоммичен
- [x] `assets/logo/kvis-trade-gold.png` — прозрачный логотип
- [x] `favicon.ico`, `apple-touch-icon.png`, `assets/logo/favicon-*.png`
- [x] `_headers` — security-заголовки + кеш статики
- [x] `_redirects` — `www.kvistrade.ru` → `kvistrade.ru` (301)
- [x] `robots.txt`, `sitemap.xml`
- [x] OpenGraph / meta description / theme-color в `<head>`

Перед публикацией:
1. Смерджить ветку `claude/determined-wozniak-yglLg` в `main`
   (Cloudflare Pages по умолчанию деплоит из production branch).
2. Удостовериться, что в `site.config.json` верные контакты.

---

## Этап 1. Cloudflare-аккаунт (5 минут)

1. Открыть https://dash.cloudflare.com/sign-up
2. Email + пароль. Без кредитки.
3. Подтвердить email по ссылке из письма.

---

## Этап 2. Добавить домен в Cloudflare (10 минут)

1. В дашборде → **Add a domain**.
2. Ввести `kvistrade.ru` → Continue.
3. Выбрать **Free** план → Continue.
4. Cloudflare просканирует DNS у текущего регистратора (если есть записи)
   и покажет их. На этом этапе можно пропустить — мы донастроим позже.
5. Cloudflare покажет два nameserver-адреса, например:
   ```
   tania.ns.cloudflare.com
   kirk.ns.cloudflare.com
   ```
   **Записать оба — они понадобятся в следующем шаге.**

---

## Этап 3. Сменить nameservers у регистратора (15 мин + до 24 ч ожидания)

Инструкция зависит от регистратора. Большинство пунктов одинаковы:
найти «Управление DNS / NS-серверами», заменить старые NS на два от Cloudflare.

### REG.RU
1. https://lk.reg.ru → «Мои домены и услуги»
2. Кликнуть `kvistrade.ru` → вкладка **DNS-серверы и управление зоной**
3. Кнопка **Изменить**
4. Удалить `ns1.reg.ru`, `ns2.reg.ru` (или какие там стоят)
5. Вписать NS от Cloudflare → Сохранить

### Beget
1. https://cp.beget.com → **Домены и поддомены**
2. Шестерёнка справа от `kvistrade.ru` → **Управление NS**
3. Заменить на NS Cloudflare → Сохранить

### Timeweb
1. https://hosting.timeweb.ru → **Домены**
2. Кликнуть `kvistrade.ru` → **Сменить NS-серверы**
3. Указать Cloudflare NS → Сохранить

### nic.ru
1. https://www.nic.ru → Личный кабинет → **Мои услуги** → **Домены**
2. Открыть `kvistrade.ru` → блок **DNS-серверы** → **Изменить**
3. Указать Cloudflare NS → Сохранить

После сохранения вернуться в Cloudflare и нажать **Done, check nameservers**.

⏱ Распространение DNS: обычно 5–60 минут, иногда до 24 часов.
Cloudflare пришлёт email «Your site is now active», когда заметит NS.

---

## Этап 4. Подключить GitHub-репозиторий к Cloudflare Pages (5 минут)

1. Cloudflare дашборд → слева **Workers & Pages** → **Create application**
2. Вкладка **Pages** → **Connect to Git**
3. Авторизовать Cloudflare в GitHub:
   - Install & Authorize → выбрать аккаунт `ivomih37-star`
   - Разрешить доступ к `vina-bolgarii` (можно сразу к одному репо)
4. Выбрать репозиторий `vina-bolgarii` → **Begin setup**
5. Параметры:
   - **Project name:** `kvistrade` (это даст preview-URL `kvistrade.pages.dev`)
   - **Production branch:** `main`
   - **Framework preset:** None
   - **Build command:** оставить пустым
   - **Build output directory:** `/` (корень)
6. **Save and Deploy**.
7. Через ~30 секунд деплой завершится — откроется страница с URL
   `https://kvistrade.pages.dev`. Открыть, убедиться, что сайт работает.

### Альтернативно: автосборка из шаблона
Если хочется, чтобы при правке `index.template.html` сайт сам пересобирался,
поставить:
- **Build command:** `python3 build.py`
- **Build output directory:** `/` (или `.`)

Cloudflare Pages поддерживает Python 3 из коробки.

---

## Этап 5. Привязать домен к Pages (5 минут + 5 минут на SSL)

1. В проекте Pages → вкладка **Custom domains** → **Set up a custom domain**
2. Ввести `kvistrade.ru` → Continue → Activate domain
3. Cloudflare автоматически создаст нужные DNS-записи в зоне.
4. Подождать ~3–5 минут — статус станет **Active**, TLS-сертификат
   выпустится автоматически.
5. Повторить для `www.kvistrade.ru`:
   - **Set up a custom domain** → `www.kvistrade.ru` → Continue.
   - При желании файл `_redirects` уже делает 301 c `www` на основной домен.

Проверить: открыть https://kvistrade.ru — должен открываться сайт по HTTPS.

---

## Этап 6. Email Routing — `info@kvistrade.ru` → Gmail (10 минут)

1. В дашборде Cloudflare → выбрать домен `kvistrade.ru`
2. Слева **Email** → **Email Routing** → **Get started**
3. Кнопка **Add records and enable** — Cloudflare сам пропишет MX-записи
   и SPF в DNS.
4. Раздел **Routes** → **Custom addresses** → **Create address**:
   - Custom address: `info`
   - Action: **Send to an email**
   - Destination: `kvistrade@gmail.com`
   - **Save**
5. На `kvistrade@gmail.com` придёт письмо с подтверждением — нажать ссылку.
6. (Опционально) добавить **Catch-all** в той же секции:
   - любой адрес `*@kvistrade.ru` будет уходить на `kvistrade@gmail.com`.
7. Тест: отправить с другой почты на `info@kvistrade.ru`. Письмо должно
   прийти в Gmail в течение минуты.

**Важно про отправку:** Cloudflare Email Routing только **получает**.
Чтобы отправлять *из* `info@kvistrade.ru`, надо настроить «Send mail as»
в Gmail. Это отдельный шаг, опишу при необходимости.

---

## Этап 7. Обновить контакты на сайте

После того как `info@kvistrade.ru` заработает, можно показать его на
сайте вместо `kvistrade@gmail.com`. В `site.config.json`:

```json
"email": "info@kvistrade.ru",
```

`git push` — Cloudflare Pages пересоберёт сайт за минуту.

---

## Этап 8. Финальные проверки (10 минут)

- [ ] https://kvistrade.ru — открывается, иконка-узел в табе
- [ ] https://www.kvistrade.ru — редирект на apex
- [ ] HTTPS зелёный, сертификат от Let's Encrypt / Google Trust Services
- [ ] Открыть на iPhone и Android — адаптив работает
- [ ] Age-gate появляется при первом заходе
- [ ] Кнопки «Запросить по почте» открывают `mailto:info@kvistrade.ru`
- [ ] Письмо на `info@kvistrade.ru` приходит в Gmail
- [ ] https://pagespeed.web.dev/ → 95+ на десктопе, 85+ на мобильном

---

## Полезные опции (на потом)

### Аналитика
- **Cloudflare Web Analytics** — бесплатно, без cookie, без баннеров согласия.
  Включить в Cloudflare → раздел Analytics & Logs → Web Analytics.
- **Яндекс.Метрика** — для российской аудитории, бесплатно.

### SEO
- Добавить `<meta name="yandex-verification">` после регистрации в
  Яндекс.Вебмастер, чтобы отслеживать индексацию.
- Аналогично Google Search Console.

### Если когда-нибудь сменим хостинг
DNS у Cloudflare переезжать не надо. Меняется только CNAME на новый хостинг.

---

## Откат

Если что-то пошло не так, домен можно вернуть на старые NS у регистратора
за 5 минут — сайт перестанет открываться через Cloudflare и вернётся к
прежнему состоянию (или ничему, если до этого не работал).
