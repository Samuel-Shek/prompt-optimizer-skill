# Prompt Optimizer: a Claude Code and Codex skill that turns rough requests into copy-ready prompts

**English** · [简体中文](README.zh-CN.md)

Prompt Optimizer is a Skill that turns a rough request or an existing prompt into one copy-ready prompt; it only rewrites the prompt and doesn't do the task. It's for people using Claude Code or Codex, or pasting instructions into ChatGPT GPTs or Claude Projects. In Claude Code, install it with the two commands below.

Current version **v4.1.2** · MIT license · [Changelog](CHANGELOG.md) · [How it was tested](docs/TESTING.md) · [Validation (Chinese)](VALIDATION.md)

## Quick install

**Claude Code (plugin marketplace)**

```text
/plugin marketplace add Samuel-Shek/prompt-optimizer-skill
/plugin install prompt-optimizer@prompt-optimizer
```

See [Install](#install) for manual installation, ChatGPT GPTs / Claude Projects usage, and the check for similar features before installing.

After you try it, suggestions are welcome in [Discussions](https://github.com/Samuel-Shek/prompt-optimizer-skill/discussions). For a case where it went wrong, [open a bad-case issue](https://github.com/Samuel-Shek/prompt-optimizer-skill/issues/new?template=bad-case.yml).

## Example

The example below is a hand-written illustration of the v4.1.0 structure, written by applying the rules to a fictional request. It is not a recorded model output, and a real run may differ in details.

**You type:**

```text
Use $prompt-optimizer: turn my meeting notes below into a Slack message to the team, under 80 words, polite but direct.
Meeting notes: first draft due before Thursday; Alex owns the data section; budget isn't approved yet, so don't buy any tools.
```

**The prompt it gives you:**

```text
User's exact words (follow these):
turn my meeting notes below into a Slack message to the team, under 80 words, polite but direct.
Material:
Meeting notes: first draft due before Thursday; Alex owns the data section; budget isn't approved yet, so don't buy any tools.
```

This is a simple task, so there are no supplementary notes. A recorded real run from 2026-10-22 (v3.5 era, older output structure) is in the [v4.0.4 README](https://github.com/Samuel-Shek/prompt-optimizer-skill/blob/v4.0.4/README.md#example).

> **Moved here on 2026-11-09:** this is now the official home of Prompt Optimizer; [Samuel-Shek/prompt-optimizer](https://github.com/Samuel-Shek/prompt-optimizer) is archived and keeps releases and tags before v4.0.0. The old OpenClaw integration code remains on the [`legacy/openclaw`](https://github.com/Samuel-Shek/prompt-optimizer-skill/tree/legacy/openclaw) branch.

This is a Skill: a set of working instructions written for an AI to read. You use it inside AI tools that load skill files, such as Claude Code and Codex. It isn't a standalone app or a new model, and it needs no extra API key or background service.

**One edition for every language (since v4.1.0).** There is a single skill, `prompt-optimizer`, at the repository root. It replies in the language you write in: English requests get English labels and notes, Chinese requests get Chinese ones, and other languages are handled the same way. Your own wording and any material you paste are never translated. The rule file itself is written in Chinese; that doesn't change the language of the output. The separate English edition (`prompt-optimizer-en`, v3.5.3 rules) was removed in v4.1.0. If you used it, see [Upgrading from the English edition](#upgrading-from-the-english-edition-prompt-optimizer-en).

## What it does

- **Keeps your wording verbatim.** Your request is copied word for word into a "User's exact words" section that the target AI follows. Numbers, dates, names, file names, prohibitions and relative times such as "by next Wednesday" stay exactly as you wrote them.
- **Keeps its own additions subordinate.** Anything the optimizer adds (steps, checks, how to handle missing information) goes into "Supplementary notes", which opens by saying your exact words win any conflict. It doesn't add word counts, formats, prohibitions or acceptance criteria you didn't ask for.
- **Doesn't make up missing information.** If the target AI can look something up, the prompt says where. If only you can supply it, it leaves a placeholder such as `{{TO FILL: batch number | e.g. a code like AB-123}}`. Real conflicts or gaps go into "To confirm", each with what to do if you don't answer.
- **Tells instructions apart from material.** If text you paste in says "ignore all previous rules", it is kept as material and treated as data, not as an order.
- **Remembers across edits.** Your latest explicit change overrides the old requirement; anything you haven't withdrawn stays in force.

If you only want feedback, say "review it, don't rewrite". It will point out problems without rewriting.

In tools that do work on their own, such as Claude Code and Codex, the AI calls it automatically when a task is clearly vague or missing key information (asking you for anything essential that's missing), then carries on with the task; clear tasks are done directly without it. You can also explicitly ask the AI to run it first and then carry on. Either way the prompt it produces is for the AI's own use, and what you get back is the finished task.

**Automatic, but only when needed (since v4.1.1).** Each time you ask a question or give a task, the AI first judges for itself: is the request clear enough, and can it answer well directly with its own ability and what it knows about you? If so, it just answers and doesn't call the optimizer. It calls the optimizer automatically only when the request is clearly vague or missing key information, or when you explicitly ask it to optimize a prompt. When it does, your original words are kept, its additions are only suggestions, and it doesn't make up anything you didn't say. In Codex, `allow_implicit_invocation: true` in `agents/openai.yaml` allows this automatic use; in Claude Code and other hosts the skill description asks the model to make the same judgement (if you want Claude Code to allow only the slash command, add `disable-model-invocation: true` to the frontmatter of your installed copy). Why not every time: in blind evaluations on strong models, optimizing a clear request first gave no stable quality gain over asking directly, and it cost more calls and tokens. See [CHANGELOG.md](CHANGELOG.md). v4.0.0–v4.1.0 described it as manual use only; that was a recording mistake, corrected in v4.1.1.

## What the output looks like

By default you get one copyable prompt in a single code block, split by plain-text labels:

- **Task:** an optional one-line excerpt taken from your own words;
- **User's exact words (follow these):** your request, copied verbatim;
- **Material:** anything you provided to be processed, kept as is;
- **Supplementary notes:** the optimizer's suggestions, starting with a fixed line saying your exact words prevail;
- **To confirm:** only real gaps or conflicts, each with a "When executing" fallback.

Empty sections are left out. Simple tasks usually get only "User's exact words" and "Material".

## Install

**Check for similar features first (this applies when an AI installs it for you, too).** Before installing, check whether the tool already has a skill named `prompt-optimizer`, or any other prompt-optimization skill, plugin or custom instruction with a similar job under a different name (for example a prompt-enhancer skill, or a global rule like "rewrite my prompt before doing the task"). If you find one, tell the user what you found and where, and let them decide whether to replace it, keep it, or run both. Don't overwrite it, and don't quietly install a second copy alongside it.

**Claude Code (plugin marketplace)**

```text
/plugin marketplace add Samuel-Shek/prompt-optimizer-skill
/plugin install prompt-optimizer@prompt-optimizer
```

**Manual install**

1. Download:

   ```bash
   git clone --branch v4.1.2 --depth 1 https://github.com/Samuel-Shek/prompt-optimizer-skill.git prompt-optimizer
   ```

   Or download the archive from the [release page](https://github.com/Samuel-Shek/prompt-optimizer-skill/releases/tag/v4.1.2).

2. Copy the whole `prompt-optimizer` folder into your AI tool's skills folder, keeping its `references/` and `agents/` subfolders. Common locations: `~/.claude/skills/` for Claude Code, `~/.agents/skills/` for Codex. Check your tool's current docs. If a skill with the same name or a similar job is already installed, check its version and confirm with the user first (see above), so you don't overwrite changes they made.

3. Start a new session so the tool loads the skill.

**ChatGPT GPTs, Claude Projects or any chat app:** paste the contents of [`SKILL.md`](SKILL.md) into the custom instructions (add [`references/methods.md`](references/methods.md) if you want its optional methods). Clear questions are answered directly; it steps in when a request is clearly vague or missing key information, or when you ask, for example "optimize this prompt: …". Review requests and ordinary chat are still answered as such.

## Upgrading from the English edition (`prompt-optimizer-en`)

The English edition and its folder `prompt-optimizer-en/` were removed in v4.1.0. Nothing is deleted from your machine, but an old copy won't get updates. Install the merged skill once and remove the old one so you don't end up with two copies:

- **Claude Code plugin `prompt-optimizer-en@prompt-optimizer`:** the plugin name still exists as a legacy alias. Since v4.1.0 it installs the same merged skill (skill name `prompt-optimizer`), so updating it keeps working. To switch to the main name:

  ```text
  /plugin uninstall prompt-optimizer-en@prompt-optimizer
  /plugin install prompt-optimizer@prompt-optimizer
  ```

  Install only one of `prompt-optimizer` and `prompt-optimizer-en`; both now contain the same skill.
- **Marketplace added from the archived repo** (`/plugin marketplace add Samuel-Shek/prompt-optimizer`): that repo no longer gets updates. Remove it and add this one. Both use the marketplace name `prompt-optimizer`:

  ```text
  /plugin marketplace remove prompt-optimizer
  /plugin marketplace add Samuel-Shek/prompt-optimizer-skill
  /plugin install prompt-optimizer@prompt-optimizer
  ```
- **Manual install:** delete the old `prompt-optimizer-en` folder from your skills folder (for example `~/.claude/skills/prompt-optimizer-en` or `~/.agents/skills/prompt-optimizer-en`), then install `prompt-optimizer` as above and start a new session.
- **Calling it by name:** use `$prompt-optimizer` in Codex and `/prompt-optimizer` for a manually installed Claude Code skill. Plugin skills are namespaced: `/prompt-optimizer:prompt-optimizer` for the main plugin, `/prompt-optimizer-en:prompt-optimizer` for the legacy alias. The old command `/prompt-optimizer-en:prompt-optimizer-en` and `$prompt-optimizer-en` no longer exist; the old name is only mentioned in the skill description.
- **Behaviour change:** the English edition used the v3.5.3 structure ("Currently Effective Requirements" plus "Original Input"). The merged skill uses the v4 structure above. If you need the old behaviour, pin the old files: `git clone --branch v4.0.4 --depth 1 https://github.com/Samuel-Shek/prompt-optimizer-skill.git` and copy its `prompt-optimizer-en/` folder.

## Usage

Say "optimize this prompt", or call it by name:

```text
Use $prompt-optimizer: write a research prompt comparing three note-taking apps.
Target: ChatGPT on the web. Public sources only, separate facts from opinions, keep source dates.
Don't sign up for accounts, buy anything, or make personal choices for me.
```

```text
Review it, don't rewrite:
(paste the prompt to review)
```

Optional shortcuts:

| Shortcut | What it does |
|---|---|
| `+explain` (or `+讲解`) | Adds up to 5 notes on the key changes after the final prompt |
| `+two` (or `+双版`) | Gives two versions with different purposes |

There are no other shortcuts. To set a target model or tool, or to let it ask you questions first, just say so in plain words, for example "target: Claude Code" or "ask me up to 3 questions first".

## When not to use it

- **Simple tasks are easier to ask directly.** For a one-line translation or a short message, the result is about the same.
- **It doesn't do the task.** If you want the analysis, article or code, ask the AI for it directly. Optimizing first pays off when you want to pin down requirements, reuse the same prompt, or the task has many hard constraints.

## Known limitations

- **Long output on complex tasks.** Your full wording is kept verbatim and the optimizer's notes come on top, so prompts for complex tasks are longer than what you typed.
- **No guarantee the target AI complies.** However clear the prompt, the AI running it can still miss or add things. Check important output yourself.
- **The merged skill has no new real-model validation.** v4.1.0 is a structural merge. Earlier v4 tests were mostly Chinese (the v4.0.0 comparison with asking directly included 4 English cases); the merged v4.1.0 skill and the updated English exam have not been run on real models. Please report English bad cases.
- **Small test set.** Validation uses a few dozen fictional cases (26 Chinese and 26 English cases in the current exam files, plus 12 frozen cases in the comparison against asking directly), mainly on Claude and GPT models.

## Tests

`evals/` holds fictional test cases (`cases.json`: 26 Chinese; `cases.en.json`: 26 English, same IDs) and one runner for both. It gives the same target model your original request and the optimized prompt, then saves both results in random order for blind review:

```bash
python3 evals/run_eval.py --lang en --out ./eval-out --opt-model opus --target-model sonnet
python3 evals/run_eval.py --lang zh --out ./eval-out-zh
```

It needs the Claude Code CLI. The script only records outputs and runs a few mechanical checks; a person judges the results. How every test was designed and judged is in [docs/TESTING.md](docs/TESTING.md) (Chinese, with an English summary); per-version numbers are in [VALIDATION.md](VALIDATION.md) (Chinese).

## Feedback

The most useful feedback is a real case where it got something wrong. [Open a bad-case issue](https://github.com/Samuel-Shek/prompt-optimizer-skill/issues/new?template=bad-case.yml) with your input, what it returned and what you expected. Confirmed cases are anonymized and added to `evals/`. Ideas and questions go to [Discussions](https://github.com/Samuel-Shek/prompt-optimizer-skill/discussions).

## Versions

- **v4.1.2 (current):** supplementary notes cannot introduce quotations or facts absent from the user’s words and material; quotation marks are reserved for verbatim text. Adds offline fidelity checks (numbers, dates, quoted content and file names counted by occurrence; material retained; new items in notes only flagged for review), a separate `fidelity` field in `run_eval.py`, and a 20-case Chinese/English trigger mini-exam. Fixes imports when the runner is loaded by file path. Trigger rules, description and `allow_implicit_invocation` are unchanged. See the [test record](docs/testing/v4.1.2-20261110/README.md) and [evaluation commands](evals/README.md).
- **v4.1.1:** corrects how it is invoked: from "manual use only" back to automatic use when needed. Clear requests are answered directly; it is called automatically only for clearly vague requests, requests missing key information, or when you ask to optimize a prompt. `allow_implicit_invocation` is now `true`. The install section now asks you (or the installing AI) to check for same-named and similar prompt-optimization features and ask before installing. The optimization rules themselves are unchanged. See [CHANGELOG.md](CHANGELOG.md).
- **v4.1.0:** Chinese and English editions merged into one skill with one rule set (the v4.0.4 rules) and an explicit language rule: reply in the user's language, including languages other than Chinese and English; your wording and material are never translated. `prompt-optimizer-en/` and the old bilingual runner were removed; one runner now covers both exam files. This is a structural merge only: no new real-model quality tests were run. See [CHANGELOG.md](CHANGELOG.md).
- **v4.0.4:** four small revisions (4.0.1–4.0.4) to the Chinese edition, verified statically and offline.
- **v4.0.0:** rewritten to keep your wording verbatim, with the optimizer's own additions kept subordinate to it; it was set to manual use only (changed back to automatic-when-needed in v4.1.1). Blind evaluations on strong models showed no stable quality gain over asking directly.
- **v3.5.x:** earlier rules, including the English edition `prompt-optimizer-en` (v3.5.1–v3.5.3).

Full history: [CHANGELOG.md](CHANGELOG.md) (Chinese).

## Credits and license

The design drew on several public prompt-optimization resources for ideas only; no text was copied. See [design references](docs/design-references.md) (Chinese). The four optional methods in `references/methods.md` credit their sources inside that file.

Original content in this repository is under the [MIT](LICENSE) license. Linked third-party material belongs to its owners.
