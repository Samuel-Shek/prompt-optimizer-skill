# 提示词优化器

一个单用途的提示词优化 Skill / Agent Prompt 包。

English version: [README.en.md](README.en.md)

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

## 快速接入

```bash
bash scripts/install-local.sh claude
bash scripts/install-local.sh openclaw
bash scripts/install-local.sh all
```

## 快速调用

- Claude / Codex：安装后直接用 `$prompt-optimizer`
- OpenClaw：把它接进对应 Agent 工作区后，直接把原始需求发给这个角色
- 其他平台：运行 `bash scripts/print-prompt.sh`，拿到可直接粘贴的纯正文版本

## 示例

输入：

```text
帮我把这段需求整理成适合 Claude 的终版提示词：我想让它帮我写一个产品方案，重点突出用户是谁、核心功能、上线优先级和风险。
```

输出风格：

```text
请将我接下来提供的需求内容，整理成一段适合 Claude 直接使用的高质量终版提示词。

要求如下：
- 保留原始需求的真实意图，不要替我改题
- 将零散、口语化、不清晰的表达改写为明确、可执行的指令
- 自动补齐必要的任务目标、上下文、输出格式和约束条件
- 如果任务较复杂，优先使用适合 Claude 的分段结构或标签组织提示词
```

## 隐私说明

- 本仓库不包含你的会话记录、缓存目录、账号凭据或本机截图
- README 不放真实桌面截图或 GIF，避免暴露本机环境细节
- 公开仓库只保留可安全共享的 Skill、脚本和说明文件

## 平台入口

- `SKILL.md`：唯一权威源文件，也是推荐编辑入口
- `AGENTS.md`：`SKILL.md` 的别名，给读取 `AGENTS.md` 的 Agent 系统
- `CLAUDE.md`：`SKILL.md` 的别名，给读取 `CLAUDE.md` 的工作区系统
- `scripts/install-local.sh`：一键安装到 Claude / Codex / OpenClaw
- `scripts/print-prompt.sh`：导出可直接粘贴给其他 AI 平台的正文版本
- `agents/openai.yaml`：界面元数据
- `references/model-adaptation.md`：不同模型的适配参考
- `docs/platforms.zh-CN.md`：各平台接入说明

## 维护规则

- 以后只改 `SKILL.md`
- `AGENTS.md` 和 `CLAUDE.md` 不单独维护
- 克隆仓库到本地后，三个入口会自动保持一致

## 目录结构

```text
prompt-optimizer/
├── AGENTS.md
├── CLAUDE.md
├── LICENSE
├── SKILL.md
├── README.md
├── README.en.md
├── scripts/
│   ├── install-local.sh
│   └── print-prompt.sh
├── docs/
│   └── platforms.zh-CN.md
├── agents/
│   └── openai.yaml
└── references/
    └── model-adaptation.md
```
