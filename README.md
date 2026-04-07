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
- 不主动替你做调研（但如果优化提示词需要了解背景信息，会自行判断是否联网搜索）
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
bash scripts/install-local.sh openclaw --mode skill-only
bash scripts/install-local.sh openclaw --mode host-router
bash scripts/install-local.sh all
```

## OpenClaw 两种接法

| 选项 | 怎么装 | 适合谁 | 优点 | 代价 |
|---|---|---|---|---|
| `skill-only` | `bash scripts/install-local.sh openclaw --mode skill-only` | 只想主动调用 skill、不想碰宿主层的人 | 最简单、最稳、最容易理解；不会额外引入宿主级路由 | 需要显式进入提示词优化器工作区或明确调用 |
| `host-router` | `bash scripts/install-local.sh openclaw --mode host-router` | 已经把 OpenClaw 当主聊天宿主、希望在普通会话里直接短触发的人 | 最顺手；默认只挂到 `main`，不去全局劫持所有 agent；命中后会拦截主 agent，用 `xhigh` specialist 单轮处理，并把结果注回原会话 | 多一层本地插件和宿主配置，排障面更大；它仍然不是持久会话切换 |

选择建议：

- 如果你主要在 Claude / Codex / Skill 目录里用它，或者你就是想“主动调用时才生效”，选 `skill-only`
- 如果你主要在 OpenClaw 的普通聊天面板、飞书、Telegram 里用短 trigger，不想先切工作区，选 `host-router`

使用场景举例：

- `skill-only`：你会明确输入 `$prompt-optimizer`，或打开专门的提示词优化器工作区，再把原始内容贴进去
- `host-router`：你正在普通主 agent 聊天，直接发“优化提示词：做个全球股票近况的调研”，宿主会拦截这轮主 agent 输出，转给提示词优化器 specialist 处理，再把结果写回原会话
- `host-router`：这条 specialist 会在独立的一次性临时 session 中运行，回写后立即结束，不会把后续普通对话持续锁在提示词优化器里
- `host-router`：等待期间会先给一两条很短的状态提示，例如“正在分析原始需求”或“正在重写终版提示词”，避免长时间完全无反馈

注意：
- `skill-only` 不会往你的 OpenClaw 配置里保留宿主路由插件项
- `host-router` 默认只作用于 `main`，如果你确实要挂到别的 agent，再自行改 OpenClaw 配置
- 如果你想要最少配置和最容易排障的方案，优先选 `skill-only`
- `host-router` 现在默认会压掉主 agent 的正文，并把独立临时 specialist session 的结果回写回来；它是“按轮路由”，不是进入一个持久的 prompt_optimizer 会话
- 当前默认给 routed specialist 使用 `xhigh` 思考强度，所以质量优先，代价是等待时间会比 `skill-only` 更长

## 快速调用

- 推荐主触发只保留这 4 种：
  - `优化提示词：做个全球股票近况的调研`
  - `帮我优化：做个全球股票近况的调研`
  - `做个全球股票近况的调研——优化提示词`
  - `做个全球股票近况的调研——帮我优化`

- Claude / Codex：安装后直接用 `$prompt-optimizer`，然后发上面 4 种写法之一；如果已经显式进入这个 skill，也可以直接贴原始内容
- OpenClaw：
  - `skill-only`：进入专用工作区后贴原始内容，或显式调用提示词优化器
  - `host-router`：普通 Agent 会话里发上面 4 种写法，也会被临时切到“提示词优化器”模式
- 其他平台：运行 `bash scripts/print-prompt.sh`，拿到可直接粘贴的纯正文版本

兼容的语义触发也支持，但不建议当主入口到处传播，例如：

- `调用提示词优化器：做个全球股票近况的调研`
- `调用 Prompt Optimizer：做个全球股票近况的调研`

原则是：**对外传播用 4 个主触发，宿主识别时再兼容语义调用。**

## 示例

详细例子见 [docs/examples.zh-CN.md](docs/examples.zh-CN.md)。

稍复杂一点的输入：

```text
帮我优化：盘点我最近在做的事情里，哪些 SOP 适合沉淀成公开 Skill，并输出优先级、理由、依赖、复用场景和 GitHub 发布建议
```

输出风格：

```text
请基于我接下来提供的工作清单、项目片段、零散记录或 SOP 草稿，判断其中哪些内容最适合沉淀成可公开复用的 Skill。

任务目标：
- 找出最值得先做的 Skill 候选项
- 解释为什么值得做
- 给出最小可发布范围，而不是泛泛而谈的大而全方案

分析要求：
1. 先识别每个候选 SOP 的核心任务、重复频率、可标准化程度、是否依赖个人隐性经验
2. 判断它更适合做成：
   - 单用途 Skill
   - Agent 工作流
   - 仅内部 SOP，不适合公开
3. 对适合做成 Skill 的候选项，按优先级输出：
   - Skill 名称建议
   - 适用场景
   - 核心输入
   - 核心输出
   - 必要约束
   - 为什么值得优先做
   - 发布到 GitHub 前还缺什么
4. 对不适合公开的项，明确说明阻碍点，例如：
   - 强依赖私有数据
   - 强依赖个人判断
   - 流程还不稳定
   - 安全边界不清楚

输出格式：
- 先给一段 150-250 字的结论摘要
- 再用表格列出所有候选项的判断结果
- 最后单独给一个“建议先做的前 3 个 Skill”清单

约束条件：
- 不要为了显得完整而强行把所有 SOP 都判成适合做 Skill
- 如果某项信息不足，用 `{{待确认：...}}` 标出缺口
- 优先给可执行的发布建议，而不是抽象方法论
```

## 回归测试

```bash
node scripts/test-trigger-detection.mjs
node scripts/test-host-router-e2e.mjs
```

- `test-trigger-detection.mjs`：验证推荐触发和语义触发是否仍然可识别
- `test-host-router-e2e.mjs`：验证 `host-router` 是否仍然满足“一次 trigger，只优化一轮；回写后立即回到普通对话”

第二个脚本需要本机 OpenClaw Gateway 正在运行，且已安装 `host-router` 模式。

## 隐私说明

- 本仓库不包含你的会话记录、缓存目录、账号凭据或本机截图
- README 不放真实桌面截图或 GIF，避免暴露本机环境细节
- 公开仓库只保留可安全共享的 Skill、脚本和说明文件

## 平台入口

- `SKILL.md`：唯一权威源文件，也是推荐编辑入口
- `AGENTS.md`：`SKILL.md` 的别名，给读取 `AGENTS.md` 的 Agent 系统
- `CLAUDE.md`：`SKILL.md` 的别名，给读取 `CLAUDE.md` 的工作区系统
- `scripts/install-local.sh`：一键安装到 Claude / Codex / OpenClaw
- `integrations/prompt-optimizer-router/`：OpenClaw `host-router` 模式用的本地触发插件源码，安装脚本会通过 `plugins.load.paths` 接入
- `scripts/print-prompt.sh`：导出可直接粘贴给其他 AI 平台的正文版本
- `scripts/test-trigger-detection.mjs`：最小触发回归测试
- `agents/openai.yaml`：界面元数据
- `references/model-adaptation.md`：不同模型的适配参考
- `docs/platforms.zh-CN.md`：各平台接入说明
- `docs/examples.zh-CN.md`：更完整的复杂示例
- `docs/landscape.zh-CN.md`：同类项目对比，以及为什么本项目坚持单一职责

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
├── integrations/
│   └── prompt-optimizer-router/
│       ├── index.js
│       ├── openclaw.plugin.json
│       └── trigger-detection.mjs
├── scripts/
│   ├── install-local.sh
│   ├── print-prompt.sh
│   └── test-trigger-detection.mjs
├── docs/
│   ├── examples.zh-CN.md
│   └── platforms.zh-CN.md
├── agents/
│   └── openai.yaml
└── references/
    └── model-adaptation.md
```
