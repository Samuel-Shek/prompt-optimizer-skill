# 提示词优化器

一个单用途的提示词优化 Skill / Agent Prompt 包。

它只做一件事：把用户的原始需求、粗糙提示词、system prompt 或 agent 指令，改写成可直接复制给主流大模型使用的终版提示词。

## 它适合做什么

- 优化一段已有 prompt
- 把口语化需求整理成专业提示词
- 重写 system prompt / agent 指令
- 按 Claude / GPT / Gemini / DeepSeek / 开源模型适配提示词格式

## 它不做什么

- 不直接执行原任务
- 不联网帮你查资料
- 不直接写代码、跑命令、发 GitHub
- 不默认输出多个版本

## 设计原则

- 单一职责
- 默认直接输出终版提示词
- 简单任务不过度工程化
- 信息不足时用占位符标记，而不是停住

## 适用对象

- 想提高 prompt 质量的人
- 想把 agent 指令写得更稳的人
- 想把一段模糊需求改写成可执行 AI 指令的人

## 平台入口

- `SKILL.md`：Skill 的正式定义
- `AGENTS.md`：给读取 `AGENTS.md` 的 Agent 系统
- `CLAUDE.md`：给读取 `CLAUDE.md` 的工作区系统
- `agents/openai.yaml`：界面元数据
- `references/model-adaptation.md`：不同模型的适配参考
- `docs/platforms.zh-CN.md`：各平台接入说明

## 目录结构

```text
prompt-optimizer/
├── AGENTS.md
├── CLAUDE.md
├── SKILL.md
├── README.md
├── docs/
│   └── platforms.zh-CN.md
├── agents/
│   └── openai.yaml
└── references/
    └── model-adaptation.md
```
