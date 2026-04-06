# Prompt Optimizer

A single-purpose prompt optimization skill / agent prompt pack.

It does one thing only: rewrite a raw request, rough prompt, system prompt, or agent instruction into a polished final prompt that can be copied into mainstream AI models directly.

## Quick install

```bash
bash scripts/install-local.sh claude
bash scripts/install-local.sh openclaw --mode skill-only
bash scripts/install-local.sh openclaw --mode host-router
bash scripts/install-local.sh all
```

## Two OpenClaw modes

| Option | Install | Best for | Pros | Trade-off |
|---|---|---|---|---|
| `skill-only` | `bash scripts/install-local.sh openclaw --mode skill-only` | people who only want explicit invocation and do not want to touch host-level routing | simplest, safest, easiest to reason about | you need to enter the dedicated workspace or invoke it explicitly |
| `host-router` | `bash scripts/install-local.sh openclaw --mode host-router` | people who already live in OpenClaw chats and want short triggers to work in ordinary agent sessions | fastest UX; short trigger phrases work without switching workspaces first | adds a local plugin and host-level config, so there is more moving surface to maintain |

Recommendation:

- choose `skill-only` if you mainly use Claude / Codex / skill directories, or if you want the optimizer to run only when you explicitly call it
- choose `host-router` if you mainly use OpenClaw chat surfaces and want short wrapper phrases to work in ordinary sessions

## Quick use

- Recommended primary triggers:
  - `optimize prompt: research the current global stock market`
  - `help me optimize: research the current global stock market`
  - `research the current global stock market -- optimize prompt`
  - `research the current global stock market -- help me optimize`

- Claude / Codex: install first, call `$prompt-optimizer`, then use one of the four triggers above. If you are already inside the skill, you can paste the raw content directly.
- OpenClaw:
  - `skill-only`: enter the dedicated workspace and paste the raw content, or invoke the optimizer explicitly
  - `host-router`: ordinary agent chats can recognize the same trigger phrases and temporarily switch into prompt-optimizer mode for that run
- Other platforms: run `bash scripts/print-prompt.sh` to get a clean pasteable prompt body.

Semantic/contextual invocation is supported too, but it should stay a compatibility layer rather than the headline entry point. For example:

- `invoke prompt optimizer: research the current global stock market`
- `call Prompt Optimizer: research the current global stock market`

The rule is: **publish the four primary triggers, but let the host route compatible semantic invocations when the intent is obvious.**

## Example

See [docs/examples.zh-CN.md](docs/examples.zh-CN.md) for fuller Chinese examples.

More demanding input:

```text
help me optimize: review the workflows I have been doing recently, figure out which SOPs are good candidates for public skills, and rank them with reasons, dependencies, reuse scenarios, and GitHub release notes
```

Expected output style:

```text
Please review the work items, partial SOPs, scattered notes, or workflow fragments I provide next and determine which of them are the best candidates to turn into public reusable skills.

Goal:
- identify the strongest skill candidates
- explain why they are worth packaging
- suggest the minimum publishable scope instead of bloated all-in-one plans

Analysis requirements:
1. for each candidate, judge task clarity, repetition frequency, standardizability, and dependence on tacit personal knowledge
2. classify each item as:
   - a single-purpose skill
   - an agent workflow
   - an internal SOP that should stay private
3. for each skill-worthy candidate, provide:
   - suggested skill name
   - suitable use cases
   - core inputs
   - core outputs
   - essential constraints
   - why it deserves priority
   - what is still missing before a GitHub release
4. for items that should not be public, explain the blocker clearly

Output format:
- start with a 150-250 word summary
- then provide a table covering all candidates
- end with a “top 3 skills to build first” list

Constraints:
- do not force every SOP into a skill
- if details are missing, mark them as `{{to confirm: ...}}`
- prefer actionable release advice over abstract framework talk
```

## Trigger regression test

```bash
node scripts/test-trigger-detection.mjs
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
- `integrations/prompt-optimizer-router/`: source for the OpenClaw `host-router` local trigger plugin, wired through `plugins.load.paths`
- `scripts/print-prompt.sh`: print the plain prompt body for direct copy-paste
- `scripts/test-trigger-detection.mjs`: minimal trigger regression test

## Maintenance

- Edit `SKILL.md` only
- `AGENTS.md` and `CLAUDE.md` are aliases to the same source

## License

MIT
