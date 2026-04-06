# 推广文案

仓库地址：

<https://github.com/Samuel-Shek/prompt-optimizer-skill>

## 一句话简介

一个单用途的提示词优化 Skill：把粗糙需求、已有 prompt、system prompt 或 agent 指令，改写成可直接给 Claude、GPT、Gemini、DeepSeek、Codex、OpenClaw 等模型使用的终版提示词。

## X / 短帖版

我把自己常用的「提示词优化器」整理成了一个公开 Skill。

它只做一件事：
把粗糙需求、已有 prompt、system prompt、agent 指令，改写成可直接复制给 Claude / GPT / Gemini / DeepSeek / OpenClaw 使用的终版提示词。

特点：
- 单一职责，不执行任务本身
- 简单任务不过度工程化
- 支持 Claude / GPT / Gemini / DeepSeek / 开源模型的格式适配
- 可直接接入 Claude、Codex、OpenClaw，本地也能一键安装
- 实际调用很短，直接说“优化：xxx”或“xxx —— 优化提示词”就行

Repo：
https://github.com/Samuel-Shek/prompt-optimizer-skill

## 飞书 / Telegram / 群发版

最近把我自己在用的一个「提示词优化器」整理成公开仓库了。

它不是通用聊天机器人，而是一个单用途 Skill：
专门把你手头的粗糙需求、已有提示词、system prompt、agent 指令，改写成可以直接丢给 AI 模型使用的终版提示词。

比较适合这些场景：
- 你已经有一段 prompt，但写得不稳
- 你脑子里有需求，但还没整理成 AI 能执行的指令
- 你在写 Claude / GPTs / Agent 的系统提示词
- 你希望同一份需求能更好地适配 Claude、GPT、Gemini、DeepSeek 等模型

目前已经整理成可公开使用的版本，支持：
- Claude
- Codex
- OpenClaw
- 其他支持直接粘贴 system prompt 的平台

仓库：
https://github.com/Samuel-Shek/prompt-optimizer-skill

本地接入也比较简单：

```bash
bash scripts/install-local.sh claude
bash scripts/install-local.sh openclaw
bash scripts/install-local.sh all
```

如果平台没有原生 Skill 机制，也可以直接运行：

```bash
bash scripts/print-prompt.sh
```

拿到纯正文后直接粘贴使用。

## GitHub 置顶说明版

Prompt Optimizer is a single-purpose skill for rewriting rough requests, existing prompts, system prompts, and agent instructions into polished final prompts for mainstream AI models.

It is designed for people who already know what they want AI to do, but want the instruction itself to become clearer, more stable, and more model-friendly.

Highlights:
- rewrite only, never execute the task itself
- no over-engineering for simple tasks
- adapts structure for Claude, GPT, Gemini, DeepSeek, and open-source models
- supports Claude / Codex / OpenClaw local installation
- can also export a plain prompt body for copy-paste use on other platforms

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
- GitHub 上是公开仓库
- 仓库内容已经做过隐私检查
- 不包含本地缓存、会话记录、凭据或机器截图
- 支持 Claude、Codex、OpenClaw 的本地接入

仓库地址：
https://github.com/Samuel-Shek/prompt-optimizer-skill

## 推荐转发语

- 如果你经常写 prompt，但总觉得不稳，可以试试这个。
- 如果你在折腾 Claude / GPTs / Agent system prompt，这个会比较顺手。
- 如果你不是想换更强模型，而是想先把指令写对，这个工具更对症。
