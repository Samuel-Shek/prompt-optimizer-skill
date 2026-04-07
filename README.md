# Prompt Optimizer ｜ 提示词优化器

把你随手写的一句话、一段粗糙需求、一份混杂的 system prompt，改写成可直接复制给任意 AI 使用的终版提示词。

Turn a rough idea, messy prompt, or tangled system prompt into a polished, ready-to-paste AI instruction.

---

## 🇨🇳 中文

### 它是什么

一个单用途 Skill：**只优化提示词，不执行任务本身。**

你发给它的每一条消息都会被当作"原材料"，输出一段结构清晰、约束明确的终版提示词。

适合：
- 优化一段已有 prompt
- 把口语化需求变成专业 AI 指令
- 重写 system prompt / agent 指令
- 按 Claude / GPT / Gemini / DeepSeek / 开源模型适配格式

### 示例

**你输入：**

```
优化提示词：帮我做一份竞品分析
```

**它输出：**

一段包含分析维度、输出结构、约束条件和占位符的完整提示词——拿到就能直接复制给任意 AI 使用。

👉 完整 before → after 示例见 [docs/examples.zh-CN.md](docs/examples.zh-CN.md)

### 三种使用方式

#### 1. 手动模式（Manual Mode）

> 你主动调用，它才工作。最简单、最稳。

| 平台 | 怎么用 |
|---|---|
| **Claude Code** | 运行 `$prompt-optimizer`，然后贴入原始内容 |
| **Codex** | 同上 |
| **OpenClaw** | 进入 `prompt-optimizer` 专用工作区，贴入原始内容 |

安装：

```bash
bash scripts/install-local.sh claude        # Claude Code
bash scripts/install-local.sh codex         # Codex
bash scripts/install-local.sh openclaw --mode skill-only   # OpenClaw
bash scripts/install-local.sh all           # 全部装
```

#### 2. 自动模式（Auto Mode）

> 在普通聊天里发触发词，自动拦截处理。仅限 OpenClaw。

你在任意普通 Agent 会话里发：

```
优化提示词：帮我做一份竞品分析
```

宿主会自动拦截这轮对话，转给提示词优化器处理，把结果写回原会话。下一轮对话自动回到普通模式。

**4 种推荐触发写法：**

```
优化提示词：<你的原始内容>
帮我优化：<你的原始内容>
<你的原始内容>——优化提示词
<你的原始内容>——帮我优化
```

安装：

```bash
bash scripts/install-local.sh openclaw --mode host-router
```

注意：
- 默认只挂到 `main` agent，不会劫持其他 agent
- 使用 `xhigh` 思考强度，质量优先，等待时间较长
- 等待期间会显示 1-2 条简短进度提示

#### 3. 复制粘贴模式（Copy-Paste Mode）

> 导出纯文本 prompt，粘贴到任何 AI 平台。

```bash
bash scripts/print-prompt.sh
```

把输出的纯文本复制到 ChatGPT、Gemini、DeepSeek、Poe 或任何其他平台的 system prompt 里即可使用。

### 手动模式 vs 自动模式怎么选？

| | 手动模式 | 自动模式 |
|---|---|---|
| **适合** | Claude / Codex / 想主动调用才生效 | OpenClaw 聊天面板 / 飞书 / Telegram |
| **触发方式** | 显式进入 skill 或工作区 | 在普通聊天发触发词 |
| **配置复杂度** | 最低 | 多一层插件配置 |
| **推荐** | 大多数人选这个 | 重度 OpenClaw 用户选这个 |

### 回归测试

```bash
node scripts/test-trigger-detection.mjs      # 触发词识别测试
node scripts/test-host-router-e2e.mjs         # 自动模式端到端测试（需本地 OpenClaw Gateway）
```

### 文件说明

| 文件 | 说明 |
|---|---|
| `SKILL.md` | 唯一权威源文件（编辑入口） |
| `AGENTS.md` / `CLAUDE.md` | `SKILL.md` 的别名 |
| `scripts/install-local.sh` | 一键安装 |
| `scripts/print-prompt.sh` | 导出纯文本 prompt |
| `integrations/prompt-optimizer-router/` | 自动模式插件源码 |
| `docs/examples.zh-CN.md` | 完整示例 |
| `docs/landscape.zh-CN.md` | 同类项目对比 |
| `docs/platforms.zh-CN.md` | 各平台接入说明 |
| `references/model-adaptation.md` | 模型适配参考 |

### 维护

只改 `SKILL.md`。`AGENTS.md` 和 `CLAUDE.md` 会自动保持一致。

---

## 🇬🇧 English

### What is it

A single-purpose skill: **it only optimizes prompts — it never executes the task itself.**

Every message you send is treated as raw material. The output is a structured, ready-to-paste final prompt.

Good for:
- Improving an existing prompt
- Turning a rough idea into a professional AI instruction
- Rewriting system prompts and agent instructions
- Adapting prompt format for Claude, GPT, Gemini, DeepSeek, and open-source models

### Example

**You type:**

```
optimize prompt: write a competitive analysis report
```

**It outputs:**

A complete prompt with analysis dimensions, output structure, constraints, and placeholders — ready to paste into any AI.

👉 Full before → after examples: [docs/examples.zh-CN.md](docs/examples.zh-CN.md)

### Three ways to use it

#### 1. Manual Mode

> You invoke it explicitly. Simplest and most stable.

| Platform | How |
|---|---|
| **Claude Code** | Run `$prompt-optimizer`, then paste your content |
| **Codex** | Same as above |
| **OpenClaw** | Enter the `prompt-optimizer` workspace, then paste |

Install:

```bash
bash scripts/install-local.sh claude
bash scripts/install-local.sh codex
bash scripts/install-local.sh openclaw --mode skill-only
bash scripts/install-local.sh all
```

#### 2. Auto Mode

> Use trigger phrases in normal chat — it intercepts automatically. OpenClaw only.

In any ordinary agent chat, type:

```
优化提示词：write a competitive analysis report
帮我优化：write a competitive analysis report
```

The host intercepts the turn, routes it to the optimizer specialist, injects the result back, and resumes normal chat on the next turn.

Install:

```bash
bash scripts/install-local.sh openclaw --mode host-router
```

#### 3. Copy-Paste Mode

> Export the raw prompt text and paste it into any AI platform.

```bash
bash scripts/print-prompt.sh
```

Copy the output into ChatGPT, Gemini, DeepSeek, Poe, or any other platform's system prompt field.

### File reference

| File | Purpose |
|---|---|
| `SKILL.md` | Single source of truth (edit here) |
| `AGENTS.md` / `CLAUDE.md` | Aliases for `SKILL.md` |
| `scripts/install-local.sh` | One-command installer |
| `scripts/print-prompt.sh` | Export plain prompt body |
| `integrations/prompt-optimizer-router/` | Auto Mode plugin source |
| `docs/examples.zh-CN.md` | Full examples |
| `docs/landscape.zh-CN.md` | Comparison with similar projects |
| `references/model-adaptation.md` | Model adaptation notes |

### Privacy

This repo contains no chat logs, credentials, or local screenshots. Only shareable skill files, scripts, and docs are published.

### License

MIT
