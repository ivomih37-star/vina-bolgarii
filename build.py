#!/usr/bin/env python3
"""
build.py — сборка index.html и legal-страниц из шаблонов и site.config.json.

Что делает:
  * подставляет реальные контакты (почта, телефон) и название бренда;
  * генерирует JSON-LD Schema.org Organization/WebSite для повышения
    доверия поисковиков и AI;
  * собирает блок юридических реквизитов в подвал из конфига;
  * собирает иконки соцсетей (показываются только те, что заполнены);
  * подставляет meta-теги верификации Yandex.Webmaster / Google Search Console;
  * если в конфиге указан путь к фото (hero_photo / gastro_photo), заменяет
    нарисованную кодом бутылку/бокал на тег <img> с этим фото;
  * собирает legal-страницы (privacy/terms/cookie/about) из legal-templates/.

Запуск:
  python build.py
  python build.py --config site.config.json --template index.template.html --out index.html

Зависимости: только стандартная библиотека Python 3 (ничего ставить не нужно).
"""
import argparse
import datetime
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SITE_URL = "https://kvistraide.com"
LEGAL_TEMPLATES_DIR = ROOT / "legal-templates"
LEGAL_OUTPUT_FILES = ("privacy.html", "terms.html", "cookie.html", "about.html")


def load_config(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def img_tag(css_class: str, src: str, alt: str) -> str:
    """Тег картинки с экранированными значениями из конфига."""
    return (
        f'<img class="{css_class}" src="{html.escape(src, quote=True)}" '
        f'alt="{html.escape(alt, quote=True)}">'
    )


DOWNLOAD_ICON = (
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
    '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>'
    '<polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>'
    '</svg>'
)
MAIL_ICON = (
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
    '<rect x="3" y="5" width="18" height="14" rx="2"/>'
    '<polyline points="3 7 12 13 21 7"/>'
    '</svg>'
)

# SVG-иконки соцсетей (контурные, единый стиль с остальной графикой сайта).
SOCIAL_ICONS = {
    "vk": (
        '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">'
        '<path d="M13.16 16.49h-1.45c-.55 0-.72-.44-1.71-1.43-.86-.84-1.24-.95-1.45-.95-.3 0-.39.08-.39.5v1.32c0 .35-.11.56-1.04.56-1.53 0-3.22-.93-4.42-2.65C.74 11.4.24 9.5.24 9.12c0-.21.08-.41.5-.41h1.45c.37 0 .51.17.66.57.71 2.06 1.91 3.86 2.4 3.86.18 0 .27-.08.27-.55v-2.14c-.06-.98-.58-1.07-.58-1.42 0-.17.14-.34.36-.34h2.28c.31 0 .42.17.42.54v2.88c0 .31.14.42.22.42.18 0 .33-.11.66-.45 1.03-1.16 1.77-2.94 1.77-2.94.09-.21.26-.4.63-.4h1.45c.44 0 .53.22.44.54-.18.85-1.96 3.36-1.96 3.36-.15.25-.21.36 0 .64.15.21.65.64 1 1.05.62.71 1.1 1.31 1.23 1.72.13.42-.08.63-.51.63z"/>'
        '</svg>'
    ),
    "telegram": (
        '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">'
        '<path d="M21.94 4.4 18.83 19.7c-.23 1.04-.85 1.29-1.71.8L12.4 17l-2.27 2.18c-.25.25-.46.46-.95.46l.34-4.85 8.81-7.95c.38-.34-.08-.53-.59-.19L6.87 13.5l-4.69-1.47c-1.02-.32-1.04-1.02.21-1.5L20.62 3c.85-.32 1.6.19 1.32 1.4z"/>'
        '</svg>'
    ),
    "linkedin": (
        '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">'
        '<path d="M20.45 20.45h-3.55v-5.57c0-1.33-.02-3.04-1.85-3.04-1.85 0-2.14 1.45-2.14 2.95v5.66H9.36V9h3.4v1.56h.05c.47-.9 1.63-1.85 3.36-1.85 3.59 0 4.26 2.36 4.26 5.43v6.31zM5.34 7.43a2.07 2.07 0 1 1 0-4.14 2.07 2.07 0 0 1 0 4.14zm-1.78 13.02h3.55V9H3.56v11.45z"/>'
        '</svg>'
    ),
}


def catalog_button(url: str, producer_label: str, email: str) -> str:
    """
    Кнопка для каталога: скачивание PDF, либо письмо-запрос с темой,
    если файл ещё не загружен.
    """
    if url.strip():
        return (
            f'<a class="cat-btn" href="{html.escape(url, quote=True)}" '
            f'target="_blank" rel="noopener" download>'
            f'{DOWNLOAD_ICON}Скачать каталог PDF</a>'
        )
    subject = f"Запрос каталога: {producer_label}"
    mailto = (
        f"mailto:{html.escape(email, quote=True)}"
        f"?subject={html.escape(subject, quote=True)}"
    )
    return (
        f'<a class="cat-btn outline" href="{mailto}">'
        f'{MAIL_ICON}Запросить по почте</a>'
    )


def replace_visual(template: str, marker: str, css_class: str,
                   photo: str, alt: str, warnings: list) -> str:
    """
    Заменяет блок между <!--MARKER--> и <!--/MARKER-->:
      * на <img>, если задан путь к фото;
      * иначе оставляет исходную графику (просто убирает маркеры-комментарии).
    """
    pattern = re.compile(
        rf"<!--{marker}-->(.*?)<!--/{marker}-->", re.DOTALL
    )
    match = pattern.search(template)
    if not match:
        raise SystemExit(f"Ошибка: в шаблоне не найден маркер {marker}.")

    if photo.strip():
        if not (ROOT / photo).exists():
            warnings.append(
                f"фото '{photo}' не найдено на диске — путь оставлен в HTML, "
                f"проверьте, что файл лежит рядом с index.html"
            )
        replacement = img_tag(css_class, photo, alt)
    else:
        # Фото не задано — сохраняем нарисованную графику без маркеров.
        replacement = match.group(1).strip()

    return template[:match.start()] + replacement + template[match.end():]


def build_json_ld(cfg: dict) -> str:
    """JSON-LD Schema.org Organization + WebSite — основной trust-сигнал
    для Google AI Overview, Яндекс Нейро и Knowledge Graph."""
    legal_country = cfg.get("legal_country", "BG").strip() or "BG"
    address_dict = {"@type": "PostalAddress", "addressCountry": legal_country}
    if cfg.get("legal_address"):
        address_dict["streetAddress"] = cfg["legal_address"]

    org = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "@id": f"{SITE_URL}/#org",
        "name": cfg.get("brand_title", "КВИС ТРЕЙД"),
        "legalName": cfg.get("legal_name", "«КВИС ТРЕЙД» ЕООД"),
        "url": SITE_URL,
        "logo": f"{SITE_URL}/assets/logo/favicon-512.png",
        "email": cfg.get("email", ""),
        "telephone": cfg.get("phone_display", ""),
        "address": address_dict,
        "foundingLocation": {
            "@type": "Country",
            "name": "Болгария" if legal_country == "BG" else legal_country,
        },
        "areaServed": {"@type": "Country", "name": "Россия"},
        "description": (
            "Эксклюзивное представительство болгарских винодельческих "
            "домов на российском рынке: Katarzyna Estate, Black Sea Gold, "
            "SIS Industries. Премиум-вина и крепкие напитки напрямую "
            "от производителя."
        ),
        "sameAs": [
            url for url in (
                "https://katarzyna.bg",
                "https://blackseagold.com",
                "https://sis.bg",
                cfg.get("social_vk", ""),
                cfg.get("social_telegram", ""),
                cfg.get("social_linkedin", ""),
            ) if url.strip()
        ],
    }
    if cfg.get("eik"):
        org["taxID"] = cfg["eik"]
        org["identifier"] = {
            "@type": "PropertyValue",
            "propertyID": "EIK",
            "value": cfg["eik"],
        }
    if cfg.get("vat"):
        org["vatID"] = cfg["vat"]
    if cfg.get("founded_year"):
        org["foundingDate"] = cfg["founded_year"]

    website = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "@id": f"{SITE_URL}/#website",
        "url": SITE_URL,
        "name": cfg.get("brand_title", "КВИС ТРЕЙД"),
        "publisher": {"@id": f"{SITE_URL}/#org"},
        "inLanguage": "ru-RU",
    }

    payload = json.dumps([org, website], ensure_ascii=False, indent=2)
    return f'<script type="application/ld+json">\n{payload}\n</script>'


def build_legal_block(cfg: dict) -> str:
    """HTML-блок юридических реквизитов для подвала.
    Если поле пустое — соответствующая строка не показывается."""
    rows = []
    legal_name = cfg.get("legal_name", "").strip()
    if legal_name:
        rows.append(html.escape(legal_name))
    if cfg.get("eik", "").strip():
        rows.append("ЕИК: " + html.escape(cfg["eik"]))
    if cfg.get("vat", "").strip():
        rows.append("ДДС: " + html.escape(cfg["vat"]))
    if cfg.get("legal_address", "").strip():
        rows.append(html.escape(cfg["legal_address"]))
    if not rows:
        return ""
    return '<div class="footer-legal">' + " · ".join(rows) + "</div>"


def build_social_block(cfg: dict) -> str:
    """Иконки соцсетей. Скрытые иконки не выводятся вообще."""
    items = []
    for key in ("vk", "telegram", "linkedin"):
        url = cfg.get(f"social_{key}", "").strip()
        if not url:
            continue
        label = {"vk": "ВКонтакте", "telegram": "Telegram", "linkedin": "LinkedIn"}[key]
        items.append(
            f'<a class="social-link" href="{html.escape(url, quote=True)}" '
            f'target="_blank" rel="noopener" aria-label="{label}">'
            f"{SOCIAL_ICONS[key]}</a>"
        )
    if not items:
        return ""
    return '<div class="footer-social">' + "".join(items) + "</div>"


def build_verification_block(cfg: dict) -> str:
    """Meta-теги верификации Yandex.Webmaster + Google Search Console."""
    tags = []
    yandex = cfg.get("yandex_verification", "").strip()
    google = cfg.get("google_verification", "").strip()
    if yandex:
        tags.append(
            f'<meta name="yandex-verification" '
            f'content="{html.escape(yandex, quote=True)}">'
        )
    if google:
        tags.append(
            f'<meta name="google-site-verification" '
            f'content="{html.escape(google, quote=True)}">'
        )
    return "\n".join(tags)


def apply_replacements(template: str, cfg: dict, current_year: str,
                       json_ld: str, legal_block: str, social_block: str,
                       verification_block: str) -> str:
    """Обычные текстовые подстановки (общие для index и legal-страниц)."""
    replacements = {
        "{{BRAND_TITLE}}": html.escape(cfg.get("brand_title", "Вина Болгарии")),
        "{{BRAND_HTML}}": cfg.get("brand_html", "Вина <span>Болгарии</span>"),
        "{{EMAIL}}": html.escape(cfg.get("email", ""), quote=True),
        "{{PHONE_DISPLAY}}": html.escape(cfg.get("phone_display", "")),
        "{{PHONE_TEL}}": html.escape(cfg.get("phone_tel", ""), quote=True),
        "{{LEGAL_NAME}}": html.escape(cfg.get("legal_name", "«КВИС ТРЕЙД» ЕООД")),
        "{{CURRENT_YEAR}}": current_year,
        "{{SITE_URL}}": SITE_URL,
        "{{JSON_LD}}": json_ld,
        "{{FOOTER_LEGAL}}": legal_block,
        "{{FOOTER_SOCIAL}}": social_block,
        "{{VERIFICATION_META}}": verification_block,
    }
    for key, value in replacements.items():
        template = template.replace(key, value)
    return template


def build_legal_pages(cfg: dict, current_year: str, json_ld: str,
                      legal_block: str, social_block: str,
                      verification_block: str, warnings: list) -> None:
    """Сборка privacy/terms/cookie/about из legal-templates/."""
    if not LEGAL_TEMPLATES_DIR.exists():
        warnings.append(
            f"папка legal-templates/ не найдена — пропускаю сборку "
            f"{', '.join(LEGAL_OUTPUT_FILES)}"
        )
        return
    for filename in LEGAL_OUTPUT_FILES:
        src = LEGAL_TEMPLATES_DIR / filename
        if not src.exists():
            warnings.append(f"шаблон {filename} не найден в legal-templates/")
            continue
        text = src.read_text(encoding="utf-8")
        text = apply_replacements(
            text, cfg, current_year, json_ld, legal_block,
            social_block, verification_block,
        )
        (ROOT / filename).write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Сборка сайта «Вина Болгарии».")
    parser.add_argument("--config", default="site.config.json")
    parser.add_argument("--template", default="index.template.html")
    parser.add_argument("--out", default="index.html")
    args = parser.parse_args()

    config_path = ROOT / args.config
    template_path = ROOT / args.template
    out_path = ROOT / args.out

    for p in (config_path, template_path):
        if not p.exists():
            raise SystemExit(f"Ошибка: не найден файл {p.name}.")

    cfg = load_config(config_path)
    template = template_path.read_text(encoding="utf-8")
    warnings: list = []
    current_year = str(datetime.datetime.now().year)
    json_ld = build_json_ld(cfg)
    legal_block = build_legal_block(cfg)
    social_block = build_social_block(cfg)
    verification_block = build_verification_block(cfg)

    template = apply_replacements(
        template, cfg, current_year, json_ld, legal_block,
        social_block, verification_block,
    )

    # Кнопки каталогов: PDF-ссылка или mailto-фолбэк.
    email = cfg.get("email", "")
    catalogs = (
        ("{{CATALOG_KATARZYNA}}", cfg.get("katarzyna_catalog_url", ""), "Katarzyna Estate"),
        ("{{CATALOG_BLACKSEA}}",  cfg.get("blacksea_catalog_url", ""),  "Black Sea Gold"),
        ("{{CATALOG_SIS}}",       cfg.get("sis_catalog_url", ""),       "SIS Industries"),
    )
    for placeholder, url, label in catalogs:
        if url.strip() and not (ROOT / url).exists() and not url.startswith(("http://", "https://")):
            warnings.append(
                f"каталог '{url}' ({label}) не найден на диске — путь оставлен в HTML"
            )
        template = template.replace(placeholder, catalog_button(url, label, email))

    # Визуальные блоки: фото или CSS-графика.
    template = replace_visual(
        template, "HERO_VISUAL", "hero-photo",
        cfg.get("hero_photo", ""), cfg.get("hero_photo_alt", ""), warnings,
    )
    template = replace_visual(
        template, "GASTRO_VISUAL", "gastro-photo",
        cfg.get("gastro_photo", ""), cfg.get("gastro_photo_alt", ""), warnings,
    )

    # Проверка, что не осталось незаполненных плейсхолдеров.
    leftovers = re.findall(r"\{\{[A-Z_]+\}\}", template)
    if leftovers:
        warnings.append(
            "в HTML остались незаполненные плейсхолдеры: "
            + ", ".join(sorted(set(leftovers)))
        )

    out_path.write_text(template, encoding="utf-8")

    # Legal-страницы (privacy / terms / cookie / about).
    build_legal_pages(
        cfg, current_year, json_ld, legal_block,
        social_block, verification_block, warnings,
    )

    print(f"Готово: собран {out_path.name}")
    for filename in LEGAL_OUTPUT_FILES:
        if (ROOT / filename).exists():
            print(f"  + {filename}")
    for w in warnings:
        print(f"  ⚠ {w}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
