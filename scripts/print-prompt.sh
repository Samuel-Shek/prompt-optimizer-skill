#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

awk '
  BEGIN { dash_count = 0 }
  /^---$/ {
    dash_count++
    next
  }
  dash_count >= 2 { print }
' "$ROOT_DIR/SKILL.md"
