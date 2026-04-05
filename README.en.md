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

- Claude / Codex: install first, call `$prompt-optimizer`, then just say:
  - `optimize prompt`
  - `help me optimize`
  - and paste the raw request / prompt / system prompt / agent instruction directly
- OpenClaw: attach it to the target agent workspace, then do the same:
  - `optimize prompt`
  - `help me optimize`
  - followed by the raw content
- Other platforms: run `bash scripts/print-prompt.sh` to get a clean pasteable prompt body

## Example

Input:

```text
optimize prompt:

I want Claude to analyze the work I’m currently doing and figure out which SOPs are worth turning into reusable Skills.

What I need is roughly:
- identify recurring workflows across my projects and day-to-day tasks
- separate reusable SOPs from one-off tasks
- rank the candidates by reuse potential, clarity of boundaries, and publishability
- suggest which ones are worth packaging for GitHub first
- explain why some items should not become Skills
- keep the output structured and decision-oriented, not generic
```

Expected output style:

```text
<instructions>
Analyze the work I provide and identify which SOPs are strong candidates for reusable Skills.
</instructions>

<context>
I am working across multiple recurring tasks and projects. Some of them may be stable, repeatable, and bounded enough to become Skills, while others may still be too ad hoc.
</context>

<output_format>
Return:
1. candidate Skills
2. priority ranking
3. items that should not become Skills
4. GitHub packaging suggestions
</output_format>

<constraints>
- base judgments on the actual work described
- explain ranking criteria
- distinguish reusable SOPs from one-off work
</constraints>
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
