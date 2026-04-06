#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILL_NAME="prompt-optimizer"
OPENCLAW_PLUGIN_ID="prompt-optimizer-router"
OPENCLAW_PLUGIN_PATH="$ROOT_DIR/integrations/prompt-optimizer-router"
OPENCLAW_LEGACY_PLUGIN_PATH="$ROOT_DIR/integrations/openclaw-trigger-router"

CLAUDE_SKILLS_DIR="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
CODEX_SKILLS_DIR="${CODEX_SKILLS_DIR:-$HOME/.codex/skills}"
OPENCLAW_WORKSPACE_DIR="${OPENCLAW_WORKSPACE_DIR:-$HOME/.openclaw/workspace-prompt-optimizer}"
OPENCLAW_CONFIG_FILE="${OPENCLAW_CONFIG_FILE:-$HOME/.openclaw/openclaw.json}"
OPENCLAW_MODE="skill-only"

FORCE=0
TARGET=""

usage() {
  cat <<'EOF'
Usage:
  bash scripts/install-local.sh claude [--force]
  bash scripts/install-local.sh codex [--force]
  bash scripts/install-local.sh openclaw [--mode skill-only|host-router] [--force]
  bash scripts/install-local.sh all [--mode skill-only|host-router] [--force]

Optional env vars:
  CLAUDE_SKILLS_DIR
  CODEX_SKILLS_DIR
  OPENCLAW_WORKSPACE_DIR
  OPENCLAW_CONFIG_FILE

Notes:
  --mode skill-only   Install only the dedicated OpenClaw workspace.
  --mode host-router  Also install and enable the local OpenClaw trigger plugin.
  Default OpenClaw mode: skill-only
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

ensure_openclaw_plugin_config() {
  local enabled="$1"

  if [ ! -f "$OPENCLAW_CONFIG_FILE" ]; then
    echo "[warn] $OPENCLAW_CONFIG_FILE not found. Skipped OpenClaw plugin config update."
    return 0
  fi

  OPENCLAW_CONFIG_FILE="$OPENCLAW_CONFIG_FILE" \
  PROMPT_OPTIMIZER_PLUGIN_ID="$OPENCLAW_PLUGIN_ID" \
  PROMPT_OPTIMIZER_PLUGIN_PATH="$OPENCLAW_PLUGIN_PATH" \
  PROMPT_OPTIMIZER_LEGACY_PLUGIN_PATH="$OPENCLAW_LEGACY_PLUGIN_PATH" \
  PROMPT_OPTIMIZER_SKILL_FILE="$ROOT_DIR/SKILL.md" \
  PROMPT_OPTIMIZER_PLUGIN_ENABLED="$enabled" \
  node <<'NODE'
const fs = require('node:fs');

const configFile = process.env.OPENCLAW_CONFIG_FILE;
const pluginId = process.env.PROMPT_OPTIMIZER_PLUGIN_ID;
const pluginPath = process.env.PROMPT_OPTIMIZER_PLUGIN_PATH;
const legacyPluginPath = process.env.PROMPT_OPTIMIZER_LEGACY_PLUGIN_PATH;
const skillFile = process.env.PROMPT_OPTIMIZER_SKILL_FILE;
const enabled = process.env.PROMPT_OPTIMIZER_PLUGIN_ENABLED === 'true';

const cfg = JSON.parse(fs.readFileSync(configFile, 'utf8'));
cfg.plugins ||= {};
cfg.plugins.enabled = cfg.plugins.enabled !== false;
const allow = Array.isArray(cfg.plugins.allow) ? cfg.plugins.allow : [];
cfg.plugins.allow = enabled
  ? Array.from(new Set([...allow, pluginId]))
  : allow.filter((entry) => entry !== pluginId);
const loadPaths = Array.isArray(cfg.plugins.load?.paths) ? cfg.plugins.load.paths : [];
const sanitizedLoadPaths = loadPaths.filter((entry) => entry !== legacyPluginPath);
cfg.plugins.load = {
  ...(cfg.plugins.load || {}),
  paths: enabled
    ? Array.from(new Set([...sanitizedLoadPaths, pluginPath]))
    : sanitizedLoadPaths.filter((entry) => entry !== pluginPath),
};
cfg.plugins.entries ||= {};

const previousEntry = cfg.plugins.entries[pluginId] && typeof cfg.plugins.entries[pluginId] === 'object'
  ? cfg.plugins.entries[pluginId]
  : {};
const previousConfig = previousEntry.config && typeof previousEntry.config === 'object'
  ? previousEntry.config
  : {};

cfg.plugins.entries[pluginId] = {
  ...previousEntry,
  enabled,
  config: {
    ...previousConfig,
    skillFile,
  },
};

fs.writeFileSync(configFile, `${JSON.stringify(cfg, null, 2)}\n`);
NODE

  if [ "$enabled" = "true" ]; then
    echo "[ok] enabled OpenClaw plugin $OPENCLAW_PLUGIN_ID in $OPENCLAW_CONFIG_FILE"
  else
    echo "[ok] disabled OpenClaw plugin $OPENCLAW_PLUGIN_ID in $OPENCLAW_CONFIG_FILE"
  fi
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
  if [ "$OPENCLAW_MODE" = "host-router" ]; then
    ensure_openclaw_plugin_config true
  else
    ensure_openclaw_plugin_config false
  fi
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    claude|codex|openclaw|all)
      TARGET="$1"
      ;;
    --force)
      FORCE=1
      ;;
    --mode)
      shift
      if [ "$#" -eq 0 ]; then
        echo "[error] --mode requires a value: skill-only or host-router" >&2
        usage
        exit 1
      fi
      case "$1" in
        skill-only|host-router)
          OPENCLAW_MODE="$1"
          ;;
        *)
          echo "[error] Unsupported mode: $1" >&2
          usage
          exit 1
          ;;
      esac
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
echo "- OpenClaw mode: $OPENCLAW_MODE"
