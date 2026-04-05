#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILL_NAME="prompt-optimizer"

CLAUDE_SKILLS_DIR="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
CODEX_SKILLS_DIR="${CODEX_SKILLS_DIR:-$HOME/.codex/skills}"
OPENCLAW_WORKSPACE_DIR="${OPENCLAW_WORKSPACE_DIR:-$HOME/.openclaw/workspace-prompt-optimizer}"

FORCE=0
TARGET=""

usage() {
  cat <<'EOF'
Usage:
  bash scripts/install-local.sh claude [--force]
  bash scripts/install-local.sh codex [--force]
  bash scripts/install-local.sh openclaw [--force]
  bash scripts/install-local.sh all [--force]

Optional env vars:
  CLAUDE_SKILLS_DIR
  CODEX_SKILLS_DIR
  OPENCLAW_WORKSPACE_DIR
EOF
}

ensure_link() {
  local source="$1"
  local dest="$2"

  mkdir -p "$(dirname "$dest")"

  if [ -L "$dest" ]; then
    local current
    current="$(readlink "$dest")"
    if [ "$current" = "$source" ]; then
      echo "[skip] $dest"
      return 0
    fi
    rm -f "$dest"
  elif [ -e "$dest" ]; then
    if [ "$FORCE" -ne 1 ]; then
      echo "[error] $dest already exists. Re-run with --force to replace it." >&2
      exit 1
    fi
    rm -rf "$dest"
  fi

  ln -s "$source" "$dest"
  echo "[ok] $dest -> $source"
}

install_claude() {
  local base="$CLAUDE_SKILLS_DIR/$SKILL_NAME"
  mkdir -p "$base"
  ensure_link "$ROOT_DIR/SKILL.md" "$base/SKILL.md"
  ensure_link "$ROOT_DIR/references" "$base/references"
  ensure_link "$ROOT_DIR/README.md" "$base/README.md"
}

install_codex() {
  local base="$CODEX_SKILLS_DIR/$SKILL_NAME"
  mkdir -p "$base"
  ensure_link "$ROOT_DIR/SKILL.md" "$base/SKILL.md"
  ensure_link "$ROOT_DIR/references" "$base/references"
  ensure_link "$ROOT_DIR/README.md" "$base/README.md"
}

install_openclaw() {
  mkdir -p "$OPENCLAW_WORKSPACE_DIR"
  ensure_link "$ROOT_DIR/AGENTS.md" "$OPENCLAW_WORKSPACE_DIR/AGENTS.md"
  ensure_link "$ROOT_DIR/AGENTS.md" "$OPENCLAW_WORKSPACE_DIR/AGENTS.zh-CN.md"
  ensure_link "$ROOT_DIR/references" "$OPENCLAW_WORKSPACE_DIR/references"
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    claude|codex|openclaw|all)
      TARGET="$1"
      ;;
    --force)
      FORCE=1
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "[error] Unknown argument: $1" >&2
      usage
      exit 1
      ;;
  esac
  shift
done

if [ -z "$TARGET" ]; then
  usage
  exit 1
fi

case "$TARGET" in
  claude)
    install_claude
    ;;
  codex)
    install_codex
    ;;
  openclaw)
    install_openclaw
    ;;
  all)
    install_claude
    install_codex
    install_openclaw
    ;;
esac

echo
echo "Done."
echo "- Claude: $CLAUDE_SKILLS_DIR/$SKILL_NAME"
echo "- Codex: $CODEX_SKILLS_DIR/$SKILL_NAME"
echo "- OpenClaw workspace: $OPENCLAW_WORKSPACE_DIR"
