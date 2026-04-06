# 平台接入说明

这份仓库不是只给某一个 AI 平台准备的。

它把同一套“提示词优化器”能力打包成多个常见入口文件，方便不同平台直接读取。

## 单一源规则

`SKILL.md` 是唯一权威源文件。

- `AGENTS.md` 是指向 `SKILL.md` 的别名
- `CLAUDE.md` 是指向 `SKILL.md` 的别名
- 以后只改 `SKILL.md`

如果某个平台不能正确读取符号链接，直接读取 `SKILL.md` 即可。

## 选哪个文件

- Claude Code / 读取 `CLAUDE.md` 的系统：优先用 `CLAUDE.md`，不能识别别名时直接用 `SKILL.md`
- OpenClaw / Codex / 读取 `AGENTS.md` 的系统：优先用 `AGENTS.md`，不能识别别名时直接用 `SKILL.md`
- Skills / Skill Marketplace / 本地技能目录：用 `SKILL.md`
- 其他没有固定 Skill 格式的平台：直接把 `SKILL.md` 或 `AGENTS.md` 内容作为长期系统指令使用

## 行为是否一致

核心行为是一致的：

- 只优化提示词，不执行任务
- 默认直接输出终版提示词
- 简单任务不过度工程化
- 指定模型时自动做格式适配

差别只在入口文件名，方便不同平台按自己的约定加载。

## 建议接法

### Claude Code

一条命令：

```bash
bash scripts/install-local.sh claude
```

之后直接调用 `$prompt-optimizer`，然后只要说：

```text
优化：{{粘贴原始内容}}
```

也可以：

```text
优化提示词：{{粘贴原始内容}}
帮我优化：{{粘贴原始内容}}
{{原始内容}} —— 优化提示词
```

### OpenClaw

一条命令：

```bash
bash scripts/install-local.sh openclaw
```

默认会把接入点放到 `~/.openclaw/workspace-prompt-optimizer`。

之后把这个工作区接到对应 Agent，直接发：

```text
优化：{{粘贴原始内容}}
```

不需要额外铺垫，也不需要先解释“我要让你帮我优化”。

### Codex / 其他 Agent 系统

一条命令：

```bash
bash scripts/install-local.sh codex
```

优先使用 `AGENTS.md`；如果平台本身支持 Skill 目录，也可以直接使用 `SKILL.md`。实际调用时也尽量用最短触发词：

```text
优化：{{粘贴原始内容}}
```

### ChatGPT / Gemini / DeepSeek / 其他通用平台

如果平台没有原生 Skill 机制，运行：

```bash
bash scripts/print-prompt.sh
```

把输出的纯正文作为系统提示词，或作为你的“提示词优化器”预设指令。
