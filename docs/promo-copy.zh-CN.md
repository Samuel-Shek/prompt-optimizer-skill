# 推广文案

仓库地址：

`<repo-url>`

## 一句话简介

一个单用途的提示词优化 Skill：把粗糙需求、已有 prompt、system prompt 或 agent 指令，整理成可直接给主流大模型使用的终版提示词。

## 核心卖点

- 单一职责：只优化提示词，不执行任务本身
- 默认直接输出终版提示词，不搞多版本对比
- 简单任务不过度工程化，复杂任务才给复杂结构
- 支持 Claude、GPT、Gemini、DeepSeek、开源模型等常见目标模型的格式适配
- 调用入口很短，主触发只保留 4 个

## 主触发

- `优化提示词：xxx`
- `帮我优化：xxx`
- `xxx——优化提示词`
- `xxx——帮我优化`

## OpenClaw 两种接法

### 1. `skill-only`

适合：
- 只想把它当成一个 Skill，用时主动调用的人
- 不想研究宿主层、插件层的人
- 希望行为最简单、最稳的人

特点：
- 只在你主动进入 Skill 或明确调用时生效
- 更像 Claude / Codex 的常规 Skill 用法
- 更适合公开推广时作为默认推荐

### 2. `host-router`

适合：
- 已经把 OpenClaw 当主聊天宿主的人
- 希望在普通会话里直接发短 trigger 就触发的人

特点：
- 普通 Agent 会话里也能识别短 trigger
- 体验更顺手
- 但多一层宿主配置和本地插件，排障面更大

推荐说法：
- 对大多数用户，先推荐 `skill-only`
- 对重度 OpenClaw 用户，再推荐 `host-router`

## X / 短帖版

我把自己常用的「提示词优化器」整理成了一个公开 Skill。

它只做一件事：
把粗糙需求、已有 prompt、system prompt、agent 指令，改写成可直接复制给 Claude / GPT / Gemini / DeepSeek / OpenClaw 使用的终版提示词。

特点：
- 单一职责，不执行任务本身
- 简单任务不过度工程化
- 支持多模型适配
- 主触发很短：`优化提示词：xxx` / `帮我优化：xxx`
- Claude、Codex、OpenClaw 都能接
- OpenClaw 还支持两种模式：
  - `skill-only`：只在主动调用时生效
  - `host-router`：普通会话里也能直接短触发

Repo：
`<repo-url>`

## 飞书 / Telegram / 群发版

最近把我自己在用的一个「提示词优化器」整理成公开仓库了。

它不是通用聊天机器人，而是一个单用途 Skill：
专门把你手头的粗糙需求、已有提示词、system prompt、agent 指令，改写成可以直接丢给 AI 模型使用的终版提示词。

比较适合这些场景：
- 你已经有一段 prompt，但写得不稳
- 你脑子里有需求，但还没整理成 AI 能执行的指令
- 你在写 Claude / GPTs / Agent 的系统提示词
- 你希望同一份需求更好地适配不同模型

这个公开版现在支持：
- Claude
- Codex
- OpenClaw
- 其他支持直接粘贴 system prompt 的平台

其中 OpenClaw 提供两种接法：
- `skill-only`：只在你主动调用时生效，适合大多数人
- `host-router`：普通会话里直接发“优化提示词：...”也能触发，适合重度 OpenClaw 用户

仓库：
`<repo-url>`

## GitHub 置顶说明版

Prompt Optimizer is a single-purpose skill for rewriting rough requests, existing prompts, system prompts, and agent instructions into polished final prompts for mainstream AI models.

It is designed for people who already know what they want AI to do, but want the instruction itself to become clearer, more stable, and more model-friendly.

Highlights:
- rewrite only, never execute the task itself
- no over-engineering for simple tasks
- adapts structure for Claude, GPT, Gemini, DeepSeek, and open-source models
- short trigger phrases for everyday use
- two OpenClaw modes:
  - `skill-only` for explicit invocation only
  - `host-router` for short-trigger use inside ordinary chats

## 稍长版介绍

我做了一个公开的 Prompt Optimizer Skill。

它解决的问题很具体：
很多时候我们并不是缺“模型能力”，而是缺一段写得足够清楚、足够稳、足够适配目标模型的提示词。

所以这个 Skill 不负责执行任务，它只负责把原始需求整理成终版提示词。

你可以把它拿来做这些事：
- 优化已有 prompt
- 把口语化需求整理成 AI 指令
- 重写 system prompt / agent 指令
- 让同一份需求更适合 Claude、GPT、Gemini、DeepSeek 或开源模型

这次放出来的是可公开、可复用的版本：
- 仓库内容已经做过隐私检查
- 不包含本地缓存、会话记录、凭据或机器截图
- Claude、Codex、OpenClaw 都能接
- OpenClaw 既支持普通 Skill 用法，也支持宿主级短 trigger 用法

如果你不想折腾宿主层，就直接用 `skill-only`。
如果你已经深度使用 OpenClaw，想在普通会话里直接发短 trigger，再用 `host-router`。

仓库地址：
`<repo-url>`

## 推荐转发语

- 如果你经常写 prompt，但总觉得不稳，可以试试这个。
- 如果你在折腾 Claude / GPTs / Agent system prompt，这个会比较顺手。
- 如果你只想把它当成一个 Skill，就用 `skill-only`。
- 如果你是重度 OpenClaw 用户，想在普通会话里直接短触发，就用 `host-router`。
