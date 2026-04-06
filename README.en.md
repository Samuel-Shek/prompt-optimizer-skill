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

- Claude / Codex: install first, call `$prompt-optimizer`, then use the shortest trigger you want:
  - `optimize: research the current global stock market`
  - `optimize prompt: research the current global stock market`
  - `help me optimize: research the current global stock market`
  - `research the current global stock market -- optimize prompt`
- OpenClaw: same idea. Short trigger first, raw content right after, no setup sentence needed
- Other platforms: run `bash scripts/print-prompt.sh` to get a clean pasteable prompt body

## Example

Input:

```text
optimize: research the current global stock market
```

Expected output style:

```text
Please produce a structured briefing on the current state of the global stock market for a reader who already knows the basics of investing but wants a fast, decision-useful overview.

Default scope:
- United States
- Europe
- China (A-shares / Hong Kong)
- Japan

Focus on:
- overall market performance over the last 1-3 months
- major macro drivers such as inflation, rates, the US dollar, geopolitics, and growth expectations
- strongest and weakest sectors, with explanations
- dominant narratives, disagreement points, and near-term risks
- the most important indicators and events to watch over the next 1-3 months

Output requirements:
1. start with a 200-300 word executive summary
2. then break down each region with:
   - market overview
   - key drivers
   - major sectors or themes
3. add a separate section for shared risks and disagreement points
4. end with a prioritized watchlist of 5-8 indicators or events

Constraints:
- avoid generic commentary; make clear judgments where possible
- label what is confirmed information vs inference
- if anything is still underspecified, mark it as `{{to confirm: ...}}` instead of stopping
- write in Chinese if the original user request is in Chinese
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
