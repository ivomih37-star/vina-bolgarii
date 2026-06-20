#!/usr/bin/env bash
# PostToolUse hook — детерминированно логирует каждый вызов инструмента
# в outputs/pipeline-log. Срабатывает всегда, независимо от модели.
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LOG="$DIR/outputs/pipeline-log"
mkdir -p "$DIR/outputs"

# Claude Code передаёт JSON события в stdin; имя инструмента вытащим грубо без jq.
INPUT="$(cat || true)"
TOOL="$(printf '%s' "$INPUT" | grep -o '"tool_name"[^,]*' | head -n1 | cut -d'"' -f4 || true)"
[ -z "$TOOL" ] && TOOL="unknown"

printf '%s\t%s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$TOOL" >> "$LOG"
