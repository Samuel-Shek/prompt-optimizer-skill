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

- Claude / Codex：安装后直接用 `$prompt-optimizer`，然后只要说：
  - `优化提示词`
  - `帮我优化`
  - 后面直接贴你的原始需求 / prompt / system prompt / agent 指令
- OpenClaw：把它接进对应 Agent 工作区后，也只要直接发：
  - `优化提示词`
  - `帮我优化`
  - 然后继续贴原始内容
- 其他平台：运行 `bash scripts/print-prompt.sh`，拿到可直接粘贴的纯正文版本

## 示例

输入：

```text
优化提示词：

我要让 Claude 帮我做一份“把我最近在做的活里哪些 SOP 能沉淀成 Skill” 的分析提示词。

需求大概是这样：
- 它需要先盘点我当前在做的项目、日常任务和重复动作
- 帮我识别哪些事情是高频、可复用、边界清晰、能沉淀成固定流程的
- 不只是列清单，还要判断哪些适合先做，哪些暂时不适合
- 最后最好能给我一个适合后续发 GitHub 的 Skill 方案结构
- 如果有些事情更像“临时任务”而不是 Skill，也要指出来
- 输出不要空，要有分类、有判断依据、有优先级
- 我之后可能会把结果继续交给 OpenClaw 或 Claude 往下做
```

输出风格：

```text
<instructions>
请根据我提供的背景信息，识别我当前正在进行的工作中，哪些 SOP 适合沉淀为可复用的 Skill，并输出一份面向后续 GitHub 发布准备的结构化分析结果。
</instructions>

<context>
我目前同时在处理多个项目、重复任务和临时事项，其中有些工作可能具备“高频、可复用、边界清晰、可形成固定输入输出”的特征，适合进一步抽象为 Skill。

你的任务不是泛泛而谈“什么叫 Skill”，而是根据我提供的真实工作内容做判断、筛选、排序和结构化整理。
</context>

<output_format>
请严格输出以下内容：

1. 候选 Skill 清单
   - Skill 名称
   - 解决的问题
   - 适用触发场景
   - 典型输入
   - 典型输出

2. 优先级排序
   - 高 / 中 / 低
   - 每项排序依据

3. 不适合做成 Skill 的事项
   - 说明为什么更像临时任务、一次性项目或强依赖人工判断

4. GitHub 准备建议
   - 哪些候选项适合优先整理成公开 Skill
   - 每个 Skill 建议包含哪些文件或模块
</output_format>

<constraints>
- 必须基于我提供的真实工作内容判断，不要凭空发散
- 不要只列名称，要给判断依据
- 优先识别高频、重复、可复用、边界稳定的 SOP
- 如果信息不足但可继续，请用 `{{待确认：...}}` 标出关键缺口
</constraints>
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
