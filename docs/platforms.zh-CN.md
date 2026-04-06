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
优化提示词：{{粘贴原始内容}}
```

也可以：

```text
帮我优化：{{粘贴原始内容}}
{{原始内容}}——优化提示词
{{原始内容}}——帮我优化
```

如果已经显式进入 `$prompt-optimizer`，也可以直接贴原始内容，不加 trigger。

另外，不要把触发规则理解成只能死板匹配这几种字符串。
如果上下文已经明确是在调用提示词优化器，也应该视为可触发，例如：

```text
调用提示词优化器：{{粘贴原始内容}}
调用 Prompt Optimizer：{{粘贴原始内容}}
用提示词优化器处理这段内容：{{粘贴原始内容}}
```

### OpenClaw

OpenClaw 提供两种模式：

```bash
bash scripts/install-local.sh openclaw --mode skill-only
bash scripts/install-local.sh openclaw --mode host-router
```

#### 模式 A：`skill-only`

- 只安装专用工作区 `~/.openclaw/workspace-prompt-optimizer`
- 不启用宿主级触发插件
- 只有你主动进入提示词优化器工作区，或明确调用它时，才会生效

适合：

- 不想研究 OpenClaw 宿主层和插件层的人
- 希望行为最可预测、排障最简单的人
- 把它当成一个“主动调用 skill”来用的人

#### 模式 B：`host-router`

- 安装专用工作区 `~/.openclaw/workspace-prompt-optimizer`
- 同时通过 `plugins.load.paths` 启用仓库里的本地触发插件
- 普通 Agent 会话里也能识别 trigger，并临时切到提示词优化器逻辑

适合：

- 已经把 OpenClaw 当主聊天入口的人
- 想在普通会话里直接发短 trigger，不想先切工作区的人
- 能接受多一层本地插件和宿主配置的人

推荐：

- 大多数公开用户先从 `skill-only` 开始
- 只有当你已经明确需要“普通会话内短 trigger”体验时，再升级到 `host-router`

推荐主触发：

```text
优化提示词：{{粘贴原始内容}}
帮我优化：{{粘贴原始内容}}
{{原始内容}}——优化提示词
{{原始内容}}——帮我优化
```

语义兼容触发也支持，例如：

```text
调用提示词优化器：{{粘贴原始内容}}
调用 Prompt Optimizer：{{粘贴原始内容}}
```

推荐对外传播时只用 4 个主触发；语义触发留给宿主层自动兼容。

### Codex / 其他 Agent 系统

一条命令：

```bash
bash scripts/install-local.sh codex
```

优先使用 `AGENTS.md`；如果平台本身支持 Skill 目录，也可以直接使用 `SKILL.md`。实际调用时也尽量用最短触发词：

```text
优化提示词：{{粘贴原始内容}}
```

或者：

```text
帮我优化：{{粘贴原始内容}}
{{原始内容}}——优化提示词
{{原始内容}}——帮我优化
```

如果系统支持基于上下文做 Skill 路由，也应该兼容：

```text
调用提示词优化器：{{粘贴原始内容}}
调用 Prompt Optimizer：{{粘贴原始内容}}
```

### ChatGPT / Gemini / DeepSeek / 其他通用平台

如果平台没有原生 Skill 机制，运行：

```bash
bash scripts/print-prompt.sh
```

把输出的纯正文作为系统提示词，或作为你的“提示词优化器”预设指令。

## 验证

如果你改了触发规则或安装脚本，运行：

```bash
node scripts/test-trigger-detection.mjs
```

这会做一轮最小回归，确保推荐触发和语义兼容触发没有被改坏。
