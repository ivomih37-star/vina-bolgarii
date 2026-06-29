---
name: match-producers
description: Строит матрицу соответствия «производитель→импортёр» (Katarzyna/Black Sea Gold/SIS) с fit-баллом и приоритетом. После profile-importers.
---

# Скилл: match-producers

Сопоставляет производителей с импортёрами по их профилю.

## Шаги
1. Возьми оценённых импортёров (из profile-importers) и матрицу из `../../1-importer-criteria.md`.
2. Для каждой пары производитель×импортёр оцени fit:
   - Katarzyna (премиум красные) → импортёры с премиальным still-портфелем.
   - Black Sea Gold (**Бургас-63 (премиальная ракия) + бренди VSOP/XO**, белые) → импортёры, сильные в бренди/крепком.
   - SIS (бренди, ракия) → импортёры-специалисты по крепкому.
3. Запиши `outputs/importers-matrix.csv`:
   `producer,importer,fit,priority,reason` (fit: high/mid/low; priority: P1/P2/P3).
4. Спорные пары — субагенту `fit-matcher`.

## Результат
`outputs/importers-matrix.csv` — кому что презентовать в первую очередь.
