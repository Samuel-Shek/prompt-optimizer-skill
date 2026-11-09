# prompt-optimizer

**English** · [简体中文](README.zh-CN.md)

> **Moved here on 2026-11-09.** This repository is now the official home of Prompt Optimizer; [Samuel-Shek/prompt-optimizer](https://github.com/Samuel-Shek/prompt-optimizer) is archived. Releases before v4.0.0 and their tags stay in that archived repository. The old OpenClaw integration code that used to live here is kept on the [`legacy/openclaw`](https://github.com/Samuel-Shek/prompt-optimizer-skill/tree/legacy/openclaw) branch.

Turn a rough request, or a prompt you already have, into one prompt you can paste straight into an AI. It only rewrites the prompt. It doesn't do the task inside it for you.

Current version **v4.0.4** (Chinese edition; the English edition is still v3.5.3) · MIT license · [Changelog](CHANGELOG.md) · [How it was tested](docs/TESTING.md) · [Validation (Chinese)](VALIDATION.md)

This is a Skill: a set of working instructions written for an AI to read. You use it inside AI tools that load skill files, such as Claude Code and Codex. It isn't a standalone app or a new model, and it needs no extra API key or background service.

There are two editions: the English edition in `prompt-optimizer-en/` (skill name `prompt-optimizer-en`) and the Chinese edition at the repository root (skill name `prompt-optimizer`). Both reply in the language you write in. As of v4.0.0 they no longer share the same rules: the Chinese edition has the v4 rules (currently v4.0.4), and the English edition keeps the v3.5.3 rules (not yet translated).

**Manual use only (since v4.0.0).** Both editions set `allow_implicit_invocation: false`, so they run only when you explicitly ask for them. In blind evaluations on strong models, optimizing a request first gave no stable quality gain over asking the model directly, and it cost more calls and tokens. See [CHANGELOG.md](CHANGELOG.md).

## What it does

- **Turns wishes into instructions an AI can follow.** "Make it professional" becomes checkable details such as audience, tone and structure, added only where they actually reduce misunderstanding. Simple tasks don't get a long template.
- **Keeps your hard details exactly as written.** Numbers, dates, names, file names, prohibitions, markers like `[DATA NEEDED]`, and statuses such as "planned" or "to be verified" stay as they are. "Plan to apply for certification" never becomes "certified".
- **Doesn't add conditions you didn't ask for.** It won't invent word counts, formats, filters or acceptance criteria and present them as your rules. When you ask for ideas, its additions are labeled as suggestions.
- **Doesn't make up missing information.** If the target AI can look something up, the prompt says where. If only you can supply it, it leaves a placeholder for you to fill. It asks you questions, at most three, only when a gap would change the result and there's no sensible default.
- **Tells instructions apart from material.** If text you paste in says "ignore all previous rules", it treats that as text to process, not as an order.
- **Remembers across edits.** Your latest explicit change overrides the old requirement; anything you haven't withdrawn stays in force. "Make it shorter" won't quietly drop a prohibition.

If you only want feedback, say "review it, don't rewrite". It will point out problems without rewriting.

In tools that do work on their own, such as Claude Code and Codex, you can also explicitly ask the AI to run it on a complicated request first and then carry on with the task. The AI won't call it on its own (manual use only). In that case the prompt is for the AI's own use, and what you get back is the finished task.

## Example

This is real output from one test run on 2026-10-22, unedited. The meeting is fictional.

**You type:**

```text
Help me optimize this prompt: turn my meeting notes below into a Slack message to the team, under 80 words, polite but direct.
Meeting notes: first draft due before Thursday; Alex owns the data section; budget isn't approved yet, so don't buy any tools.
```

**The prompt it gives you:**

````markdown
# Currently Effective Requirements

## Task
Turn the meeting notes below into a single Slack message for the team.

## Output
- One ready-to-post Slack message, nothing else (no preamble, options, or commentary).
- Under 80 words.
- Tone: polite but direct — courteous, no filler or over-apologizing.
- Plain Slack-friendly text; light formatting (short lines, bullets, bold) is optional as long as the word limit holds.

## Content rules
- Cover all three points from the notes:
  1. First draft is due before Thursday.
  2. Alex owns the data section.
  3. Budget is not yet approved, so no tool purchases.
- Keep facts exactly as stated. Do not add deadlines, owners, approvals, next steps, or meeting details that are not in the notes.
- Keep the budget status as "not yet approved" (pending) — do not imply it was rejected or approved.
- Keep "don't buy any tools" as a clear instruction to the team, not a suggestion.
- "Before Thursday" means the draft is due ahead of Thursday; do not restate it as "on Thursday".

## Meeting notes (source material)
- First draft due before Thursday
- Alex owns the data section
- Budget isn't approved yet, so don't buy any tools

---

# Original Input (for reference)

turn my meeting notes below into a Slack message to the team, under 80 words, polite but direct.
Meeting notes: first draft due before Thursday; Alex owns the data section; budget isn't approved yet, so don't buy any tools.
````

**The same AI (Claude Sonnet) then ran your original request and this prompt:**

| Your original request | The optimized prompt |
|---|---|
| Hi team! 👋 Quick recap from our meeting:<br><br>• **First draft is due before Thursday** — please plan accordingly.<br>• **Alex** will own the **data section**.<br>• **Budget isn't approved yet**, so please hold off on purchasing any tools for now.<br><br>Let me know if you have questions. Thanks for your hard work! | Hi team, quick update:<br><br>• First draft is due **before Thursday**<br>• **Alex** owns the data section<br>• Budget hasn't been approved yet, so please **don't purchase any tools** for now<br><br>Thanks all! |

Both are usable here. The optimized version is shorter and more direct, without the "thanks for your hard work" filler. This is one run of one simple task, and simple tasks often work fine without optimizing.

## Install

**Claude Code (plugin marketplace)**

```text
/plugin marketplace add Samuel-Shek/prompt-optimizer-skill
/plugin install prompt-optimizer-en@prompt-optimizer
```

For the Chinese edition, install `prompt-optimizer@prompt-optimizer` instead.

**Manual install**

1. Download:

   ```bash
   git clone --branch v4.0.4 --depth 1 https://github.com/Samuel-Shek/prompt-optimizer-skill.git
   ```

   Or download the archive from the [release page](https://github.com/Samuel-Shek/prompt-optimizer-skill/releases/tag/v4.0.4).

2. Copy the `prompt-optimizer-en` folder into your AI tool's skills folder, keeping its `references/` and `agents/` subfolders. Common locations: `~/.claude/skills/` for Claude Code, `~/.agents/skills/` for Codex. Check your tool's current docs.

3. Start a new session so the tool loads the skill.

**ChatGPT GPTs, Claude Projects or any chat app:** paste the contents of [`prompt-optimizer-en/SKILL.md`](prompt-optimizer-en/SKILL.md) into the custom instructions. In this setup, every task you send is treated as something to turn into a prompt.

## Usage

Say "optimize this prompt", or call it by name:

```text
Use $prompt-optimizer-en: write a research prompt comparing three note-taking apps.
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
| `+explain` | Adds up to 5 notes on the key changes after the final prompt |
| `+ask` | Lets it ask up to 3 necessary questions first |
| `+two` | Gives two versions with different purposes |
| `@target=model or tool` | Adapts the wording to a model or tool, e.g. `@target=Claude Code` |

### What the output looks like

By default you get one copyable prompt in two parts. First come the "Currently Effective Requirements", which the target AI follows. Then comes your original wording, marked "Original Input (for reference)", so whoever runs it can check the original intent and catch anything missed. That's why the final prompt is usually longer than what you typed. It's deliberate.

## When not to use it

- **Simple tasks are easier to ask directly.** For a one-line translation or a short message, the optimized prompt is much longer than your request and the result is about the same.
- **It doesn't do the task.** If you want the analysis, article or code, ask the AI for it directly. Optimizing first pays off when you want to pin down requirements, reuse the same prompt, or the task has many hard constraints.

## Known limitations

- **Long output.** The optimized prompt is usually five to ten times longer than your request, partly because your original wording is attached for checking.
- **Placeholders.** When information is missing, it leaves slots like `{{TO FILL: ...}}` and tells the AI how to handle them if you leave them empty. Small gaps (a greeting, a signature) are written generically; if a task gives no key information at all (for example a product description with no product details), the AI will stop and ask you rather than invent details.
- **Occasional slips.** In tests a simple task sometimes still got subheadings, and the executing model did not always follow a request for full-width Chinese punctuation in long articles. Skim the "Currently Effective Requirements" and delete anything you don't want.
- **No guarantee the target AI complies.** However clear the prompt, the AI running it can still miss or add things. Check important output yourself.
- **Small test set.** Validation so far uses a few dozen fictional cases (a 16-case baseline per language plus regression cases: 22 English, 26 Chinese in the current exam files, and 12 frozen cases in the comparison against asking directly), mainly on Claude and GPT models. Other models and long-term use haven't been tested systematically.

## Tests

`evals/` holds fictional test cases (`cases.en.json`: 22 English cases for the v3.5.3 English edition; `cases.json`: 26 Chinese cases) and a runner that gives the same target model your original request and the optimized prompt, then saves both results in random order for blind review:

```bash
python3 evals/run_eval_v3.py --lang en --out ./eval-out --opt-model opus --target-model sonnet
```

It needs the Claude Code CLI. The script only records outputs and runs a few mechanical checks; a person judges the results. The Chinese edition uses `evals/run_eval.py`. How every test was designed and judged, including the blind comparison against asking directly, is in [docs/TESTING.md](docs/TESTING.md) (Chinese, with an English summary); per-version numbers are in [VALIDATION.md](VALIDATION.md) (Chinese).

## Feedback

The most useful feedback is a real case where it got something wrong. [Open a bad-case issue](https://github.com/Samuel-Shek/prompt-optimizer-skill/issues/new?template=bad-case.yml) with your input, what it returned and what you expected. Confirmed cases are anonymized and added to `evals/`, so every later version is tested against them. Ideas and questions go to [Discussions](https://github.com/Samuel-Shek/prompt-optimizer-skill/discussions).

## Versions

- **v4.0.4 (current):** first public release of four small revisions (4.0.1–4.0.4) to the Chinese edition: rule conflicts resolved, material containing injected instructions is kept verbatim and treated as data (only injections in the rules being optimized are removed), and one fixed sentence made consistent. These revisions were verified only statically and offline; web checks were single small samples. See [CHANGELOG.md](CHANGELOG.md).
- **v4.0.0:** Chinese edition rewritten to keep your wording verbatim, with the optimizer's own additions kept subordinate to it; the main aim is fidelity, not better results. Manual use only: implicit invocation is off in both editions. Blind evaluations on strong models showed no stable quality gain over asking directly (GPT: 0 clear wins, 35 ties, 0 losses; Gemini: 6 complete pairs, no stable win). The English edition keeps the v3.5.3 rules.
- **v3.5.3:** placeholder examples describe a category instead of looking like real names, and prompts say what to do when a placeholder is left unfilled (deliver, mark the gap, never use the example as real). No notes or lead-in lines outside the prompt; strict JSON with no code fence; simple tasks get short prompts; prompts for Chinese output ask for full-width punctuation.
- **v3.5.2:** keeps banned-word lists and relative times such as "by next Wednesday" exactly as you wrote them. Earlier versions sometimes widened a banned list to word variants or turned relative times into placeholders for a specific date.
- **v3.5.1:** adds the English edition `prompt-optimizer-en`, English test cases and Claude Code plugin install. The rules are unchanged.
- **v3.5.0:** fewer self-invented conditions. It separates your original requirements, equivalent clarifications and its own suggestions, and doesn't add counts, formats, filters or acceptance criteria without a basis.

Full history: [CHANGELOG.md](CHANGELOG.md) (Chinese).

## Credits and license

The design drew on several public prompt-optimization resources for ideas only; no text was copied. See [design references](docs/design-references.md) (Chinese). The four optional methods in `references/methods.md` credit their sources inside that file.

Original content in this repository is under the [MIT](LICENSE) license. Linked third-party material belongs to its owners.
