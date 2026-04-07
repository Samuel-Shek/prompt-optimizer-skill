# Prompt Optimizer

A single-purpose skill that does one thing: turn your rough ideas, messy prompts, and chaotic system prompts into polished, ready-to-paste AI instructions.

中文版：[README.md](README.md)

## What it does

- Rewrites a rough request into a structured, actionable prompt
- Cleans up an existing prompt — removes fluff, resolves contradictions, adds missing constraints
- Restructures system prompts and agent instructions into layered, maintainable formats
- Adapts prompt structure for Claude, GPT, Gemini, DeepSeek, and open-source models

## What it doesn't do

- Execute the task itself — it only writes the prompt
- Research on your behalf by default (but if background info is needed to write a better prompt, it may search the web on its own)
- Write code, run commands, or publish to GitHub
- Output multiple versions — you get the single best version, directly

## Design principles

- Single responsibility — prompt optimization only
- Direct output by default — no explanations, no "would you like me to optimize this?"
- Complexity matches the task — a simple email prompt stays simple; a multi-step agent instruction gets the structure it needs
- Missing info gets placeholders, not questions — `{{to fill: variable | example | default}}`

## Quick install

```bash
bash scripts/install-local.sh claude
bash scripts/install-local.sh codex
bash scripts/install-local.sh openclaw --mode skill-only
bash scripts/install-local.sh openclaw --mode host-router
bash scripts/install-local.sh all
```

## Two OpenClaw modes

| Mode | Install | Best for | Pros | Trade-off |
|---|---|---|---|---|
| `skill-only` | `bash scripts/install-local.sh openclaw --mode skill-only` | Explicit invocation only; no host-level routing | Simplest, safest, easiest to reason about | You must enter the dedicated workspace or invoke it explicitly |
| `host-router` | `bash scripts/install-local.sh openclaw --mode host-router` | Short triggers in ordinary chat sessions | Fastest UX; scoped to `main` agent by default; matching turns are intercepted, routed through an `xhigh` specialist, and injected back | Adds a local plugin + host config; more surface to maintain; not a persistent session swap |

**Recommendation:** choose `skill-only` unless you mainly use OpenClaw chat surfaces and want seamless short triggers.

## Quick use

Four recommended triggers:

```
优化提示词：<your raw content>
帮我优化：<your raw content>
<your raw content>——优化提示词
<your raw content>——帮我优化
```

English triggers also work:

```
optimize prompt: <your raw content>
use Prompt Optimizer: <your raw content>
```

- **Claude / Codex:** call `$prompt-optimizer`, then paste your content using any trigger above. If you're already inside the skill, just paste the raw content directly.
- **OpenClaw skill-only:** enter the dedicated workspace, then paste.
- **OpenClaw host-router:** use any trigger in a normal agent chat — the router intercepts the turn, runs a specialist, and injects the result back.
- **Other platforms:** run `bash scripts/print-prompt.sh` to get a clean prompt body you can paste anywhere.

## Examples

**One sentence → full prompt:**

```
optimize prompt: help me write a job application email
```

Outputs a complete prompt with recipient placeholders, structure requirements, tone constraints, and a list of things to avoid — ready to paste into any AI.

**Casual description → professional instruction:**

```
帮我优化：我想让 AI 帮我每周总结工作，就是那种发给老板看的周报，别写得太官方
```

"Don't make it too formal" becomes specific style rules, output structure, and a banned-phrases list.

**Messy system prompt → layered rewrite:**

```
帮我优化下面这个客服 agent 的 system prompt，太乱了——优化提示词
(paste your original prompt)
```

Reorganizes a stream-of-consciousness ruleset into: identity → behavior rules → task workflow → prohibitions → safety boundaries. Removes every sentence that doesn't change AI behavior.

For full before → after examples, see [docs/examples.zh-CN.md](docs/examples.zh-CN.md).

## Regression tests

```bash
node scripts/test-trigger-detection.mjs
node scripts/test-host-router-e2e.mjs
```

- `test-trigger-detection.mjs` — validates supported trigger phrases (no dependencies)
- `test-host-router-e2e.mjs` — validates the full host-router one-shot contract end to end (requires a running local OpenClaw Gateway with `host-router` mode installed)

## Privacy

- This repository contains no chat logs, cache directories, credentials, or local screenshots
- Desktop screenshots and GIFs are intentionally omitted to avoid exposing local environment details
- Only shareable skill files, scripts, and documentation are published

## Entry files

| File | Purpose |
|---|---|
| `SKILL.md` | Single source of truth — edit here |
| `AGENTS.md` | Alias for agent systems that read `AGENTS.md` |
| `CLAUDE.md` | Alias for workspace systems that read `CLAUDE.md` |
| `scripts/install-local.sh` | One-command installer for Claude / Codex / OpenClaw |
| `scripts/print-prompt.sh` | Export plain prompt body for copy-paste |
| `integrations/prompt-optimizer-router/` | OpenClaw host-router plugin source |
| `docs/examples.zh-CN.md` | Full before → after examples |
| `docs/landscape.zh-CN.md` | Comparison with adjacent projects |
| `docs/platforms.zh-CN.md` | Per-platform integration guide |
| `references/model-adaptation.md` | Model-specific adaptation notes |

## Maintenance

- Edit `SKILL.md` only — `AGENTS.md` and `CLAUDE.md` are kept in sync automatically
- After cloning, all three entry files will be identical

## License

MIT
