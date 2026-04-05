# Prompt Optimizer

A single-purpose prompt optimization skill / agent prompt pack.

It does one thing only: rewrite a raw request, rough prompt, system prompt, or agent instruction into a polished final prompt that can be copied into mainstream AI models directly.

## Quick install

```bash
bash scripts/install-local.sh claude
bash scripts/install-local.sh openclaw
bash scripts/install-local.sh all
```

## Quick use

- Claude / Codex: install first, then call `$prompt-optimizer`
- OpenClaw: attach it to the target agent workspace, then send the raw request directly
- Other platforms: run `bash scripts/print-prompt.sh` to get a clean pasteable prompt body

## Example

Input:

```text
Turn this request into a Claude-ready final prompt: I want Claude to help me draft a product plan, focusing on target users, core features, launch priority, and risks.
```

Expected output style:

```text
Please turn the following rough request into a high-quality final prompt for Claude.

Requirements:
- preserve the original intent
- rewrite vague or conversational wording into clear, executable instructions
- add missing task goal, context, output format, and constraints when necessary
- use Claude-friendly structured sections when the task is complex
```

## Privacy

- This repository does not include local chat logs, cache folders, credentials, or machine screenshots
- Real desktop screenshots and GIFs are intentionally omitted to avoid exposing local environment details
- Only shareable skill files, scripts, and documentation are published

## Good for

- Improving an existing prompt
- Turning a rough request into a usable AI instruction
- Rewriting system prompts or agent instructions
- Adapting prompt structure for Claude, GPT, Gemini, DeepSeek, and open-source models

## Not for

- Executing the task itself
- Browsing the web
- Writing code, running commands, or publishing to GitHub
- Returning multiple prompt versions by default

## Entry Files

- `SKILL.md`: single source of truth and recommended edit point
- `AGENTS.md`: alias for agent systems that read `AGENTS.md`
- `CLAUDE.md`: alias for systems that read `CLAUDE.md`
- `scripts/install-local.sh`: one-command local installer for Claude / Codex / OpenClaw
- `scripts/print-prompt.sh`: print the plain prompt body for direct copy-paste

## Maintenance

- Edit `SKILL.md` only
- `AGENTS.md` and `CLAUDE.md` are aliases to the same source

## License

MIT
