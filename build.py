#!/usr/bin/env python3
"""
build.py — сборка index.html из шаблона index.template.html и данных site.config.json.

Что делает:
  * подставляет реальные контакты (почта, телефон) и название бренда;
  * если в конфиге указан путь к фото (hero_photo / gastro_photo), заменяет
    нарисованную кодом бутылку/бокал на тег <img> с этим фото;
  * если путь пустой — сохраняет исходную CSS-графику.

Запуск:
  python build.py
  python build.py --config site.config.json --template index.template.html --out index.html

Зависимости: только стандартная библиотека Python 3 (ничего ставить не нужно).
"""
import argparse
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def load_config(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def img_tag(css_class: str, src: str, alt: str) -> str:
    """Тег картинки с экранированными значениями из конфига."""
    return (
        f'<img class="{css_class}" src="{html.escape(src, quote=True)}" '
        f'alt="{html.escape(alt, quote=True)}">'
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

    # Текстовые подстановки. Телефон и почта экранируются, бренд — нет
    # (это намеренно: brand_html может содержать разметку, например <span>).
    replacements = {
        "{{BRAND_TITLE}}": html.escape(cfg.get("brand_title", "Вина Болгарии")),
        "{{BRAND_HTML}}": cfg.get("brand_html", "Вина <span>Болгарии</span>"),
        "{{EMAIL}}": html.escape(cfg.get("email", ""), quote=True),
        "{{PHONE_DISPLAY}}": html.escape(cfg.get("phone_display", "")),
        "{{PHONE_TEL}}": html.escape(cfg.get("phone_tel", ""), quote=True),
    }
    for key, value in replacements.items():
        template = template.replace(key, value)

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

    print(f"Готово: собран {out_path.name}")
    for w in warnings:
        print(f"  ⚠ {w}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
