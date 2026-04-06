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

- Claude / Codex：安装后直接用 `$prompt-optimizer`，然后直接这样发就行：
  - `优化提示词：做个全球股票近况的调研`
  - `帮我优化：做个全球股票近况的调研`
  - `做个全球股票近况的调研——优化提示词`
  - `做个全球股票近况的调研——帮我优化`
  - 或者直接输入 `$prompt-optimizer`，后面直接贴原始内容
- OpenClaw：把它接进对应 Agent 工作区后也是一样，直接发这 4 种 trigger 之一即可；如果是显式进入提示词优化器，也可以直接贴原始内容
- 其他平台：运行 `bash scripts/print-prompt.sh`，拿到可直接粘贴的纯正文版本

推荐主触发就用上面 4 种，不用再加更多固定格式。

但不要把它理解成“只能严格匹配这几个字”。
只要上下文已经明确是在调用提示词优化器，也应该视为有效，例如：

- `调用提示词优化器：做个全球股票近况的调研`
- `调用 Prompt Optimizer：做个全球股票近况的调研`
- `用提示词优化器处理这段内容：{{原始内容}}`

原则是：**优先按用户意图判断，而不是按死板命令匹配。**

## 示例

输入：

```text
优化提示词：做个全球股票近况的调研
```

输出风格：

```text
请帮我完成一份关于全球股票市场近况的结构化调研，面向已经具备基础投资认知、但希望快速把握市场脉络的读者。

调研范围默认包括：
- 美国
- 欧洲
- 中国（A 股 / 港股）
- 日本

请重点分析以下内容：
- 过去 1-3 个月的整体市场表现与主要驱动因素
- 当前影响全球股市的宏观变量，例如通胀、利率、美元、地缘政治、经济预期
- 表现最强和最弱的重点板块，并说明背后逻辑
- 市场当前的主流叙事、分歧点和潜在风险
- 接下来 1-3 个月最值得继续跟踪的观察指标和事件

输出要求：
1. 先给一段 200-300 字的执行摘要
2. 再按地区分别展开，每个地区都包含：
   - 市场表现概览
   - 主要驱动因素
   - 关键板块或主题
3. 单独写一节“共性风险与分歧”
4. 最后给一节“后续观察清单”，按优先级列出 5-8 个最值得跟踪的变量或事件

约束条件：
- 不要泛泛而谈，尽量给出清晰判断
- 如果存在明显不确定性，要标注“确定信息”和“推断判断”
- 如果某些范围仍不够明确，请用 `{{待确认：...}}` 标注，而不是直接停下
- 输出语言为中文，风格专业、清晰、可直接用于后续写报告或做简报
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
