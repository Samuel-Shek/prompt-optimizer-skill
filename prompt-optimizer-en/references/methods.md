# Reference Methods for Understanding and Decisions

Use only when they genuinely improve the current prompt. The optimizer only writes the target model's task requirements; it does not perform the research, judgment, or experiments inside them. The user's format, exact text, factual status, and permissions remain in force; a method never becomes authorization to send data externally, purchase, modify, or migrate material.

## Two-Layer Explanation: From Intuition to Mechanism

Suited to prompts that "explain an unfamiliar concept clearly". First build intuition with an everyday example close to the audience, then map it to the precise meaning, key mechanism, and limits of applicability, stating where the analogy breaks down and what the most common misunderstanding is. Do not equate the audience's ability to understand with existing expertise; do not force a childlike tone, two duplicate answers, a fixed word count, or a quiz. Keep a deep framework, such as an eight-dimension breakdown, when the user explicitly asks for it.

## Reverse Breakdown: Extracting Transferable Structure from Samples

Suited to prompts where the user provides a finished piece, a strong sample, or a failed result and wants to learn its structure or mechanism. Ask the target model to observe visible features first and then propose explanations, separating facts the sample directly supports from inferences; analyze components, order, input conditions, and interactions, and distill transferable principles and the limits of transfer.

Do not infer the author's psychology, hidden prompts, internal operations, or the single reason for success from one piece of work, and do not claim to recover unpublished originals. When the user only wants a breakdown, do not also rewrite the piece; when the user asks for a reconstruction, respect the existing material and factual limits.

## Two-Sided Argument: Comparing Alternatives Fairly

Suited to choosing between two or more options. Ask the target model to apply the same goal, hard constraints, and evaluation criteria, present each side's strongest reasons, conditions under which it holds, and main counterexamples, then check the evidence. A full argument does not mean equal length for each side or forced fifty-fifty balance; evidence strength can differ, and unknowns stay unknown when information is insufficient.

Write the conclusion as a conditional judgment, stating what new evidence would reverse it. The opposing view is not fact; agreement between models is not external verification. Do not make personal trade-offs the user has not delegated, and do not invent weights, scores, or probabilities.

## Minimal Experiment: Verify Only the Unknowns That Would Change the Decision

Suited to decision prompts where key unknowns can be reduced by a limited, reversible trial. First find the unknown that most affects the choice, then design the smallest check sufficient to observe it, keeping the following:

- **Effort and scope**: use the existing time, budget, and permissions; label time allocation as a proposed plan, not time already spent. Do not use up the budget just to fill the trial.
- **Safe material and recovery**: prefer demo data or an independent copy; state how real data stays unaffected and how to roll back. When reversibility cannot be kept, state the limit and pause the parts that depend on it.
- **Observable indicators**: record behavior and results that can actually be measured, such as whether a file saved offline can be reopened or whether content matches before and after import; distinguish operation failure, data loss, and unknown results.
- **Continue, stop, and pivot conditions**: use thresholds that the user required or that have a reliable basis; without a basis, give observable qualitative conditions, or clearly label numbers as a trial design pending confirmation, never as verified conclusions. Stop the relevant path when safety or hard constraints are not met.
- **Scope of interpretation**: one pass supports only the corresponding version, sample, and environment; a low-frequency problem not reproducing once does not mean it is fixed, and a sample trial is not a decision real users have already made.

When the user only wants a plan or a prompt, do not run the experiment; for target tasks already authorized for execution, write according to the original authorization without mechanically adding a second confirmation. Report gaps that cannot be verified honestly, and do not ask questions unrelated to the decision.

## Sources and Limits

These methods draw on the two-layer explanation, reverse engineering, dual-stance, and experiment ideas in [an article on 12 commonly used prompts](https://mp.weixin.qq.com/s/NAdhdFrUq9-BKelqzqpwBQ) shared by the Chinese creator 数字生命卡兹克 (Khazix), rewritten to fit this optimizer's fidelity and permission boundaries. The original WeChat page could not be read directly at the time; the content was checked against a public full-text repost and publicly attributed prompt material:

- [Public full-text repost](https://aitntnews.com/newDetail.html?newId=28494)
- [Public prompt material](https://raw.githubusercontent.com/xiaolouJB/prompt-toolkit/main/sources/prompts.md)

Checked on: 2026-10-05. Attribution is not a guarantee of effectiveness; the examples in this round only check behavior and do not prove these methods are better for every model or every decision.
