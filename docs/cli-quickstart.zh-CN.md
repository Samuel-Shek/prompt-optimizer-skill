# CLI 快速安装与使用

这份文档只讲最短路径：**如何用终端把 Prompt Optimizer 装好，并立刻开始用。**

如果你只想先跑通，不想研究原理，直接照抄下面命令。

---

## 1. 先拉代码

```bash
git clone <repo-url> prompt-optimizer-skill
cd prompt-optimizer-skill
```

---

## 2. 选一个你要装的平台

### Claude Code

```bash
bash scripts/install-local.sh claude
```

装完后：
- CLI 里输入 `/prompt-optimizer`
- 然后直接贴你的原始内容

---

### Codex

```bash
bash scripts/install-local.sh codex
```

装完后：
- **先重启 Codex，或至少新开一个会话**
- 然后最顺手的用法是输入 `$prompt-optimizer`
- 再直接贴你的原始内容

也可以在新会话里直接发：

```text
优化提示词：做个全球股票近况的调研
```

---

### OpenClaw

只想手动调用：

```bash
bash scripts/install-local.sh openclaw --mode skill-only
```

想在普通聊天里用 trigger 自动触发：

```bash
bash scripts/install-local.sh openclaw --mode host-router
```

装完后建议执行：

```bash
openclaw gateway restart
openclaw gateway status
```

---

### 一次全装

```bash
bash scripts/install-local.sh all
```

这会安装：
- Claude
- Codex
- OpenClaw

OpenClaw 默认使用 `skill-only`。  
如果你要自动触发模式，请单独再跑一次：

```bash
bash scripts/install-local.sh openclaw --mode host-router
```

---

## 3. 最快开始用

### 最短 trigger

```text
优化提示词：做个全球股票近况的调研
```

```text
帮我优化：我要让 Claude 帮我写一份产品方案
```

```text
做个全球股票近况的调研——优化提示词
```

```text
做个全球股票近况的调研——帮我优化
```

---

## 4. 如果你的平台不支持 Skill

直接导出纯文本版本：

```bash
bash scripts/print-prompt.sh
```

然后把输出复制到 ChatGPT、Gemini、DeepSeek、Poe 或其他平台里用。

---

## 5. 安装后到底发生了什么

### Claude / Codex

安装脚本会把这几个文件接到本地 skills 目录：
- `SKILL.md`
- `references/`
- `README.md`

### OpenClaw

安装脚本会：
- 建立 `prompt-optimizer` 工作区入口
- 在 `skill-only` 模式下只安装专用工作区
- 在 `host-router` 模式下额外启用本地路由插件

---

## 6. 仓库里最关键的文件

| 文件 | 作用 |
|---|---|
| `SKILL.md` | 主提示词文件，也是唯一权威源 |
| `scripts/install-local.sh` | 一键安装脚本 |
| `scripts/print-prompt.sh` | 导出纯文本 prompt |
| `integrations/prompt-optimizer-router/` | OpenClaw 自动触发模式源码 |
| `docs/im-private-bots.zh-CN.md` | Telegram / Discord 私聊教程 |

---

## 7. 推荐选择

如果你是新手，按这个顺序最省事：

1. Claude：`bash scripts/install-local.sh claude`
2. Codex：`bash scripts/install-local.sh codex`
3. OpenClaw：`bash scripts/install-local.sh openclaw --mode skill-only`
4. 熟了以后再开：`host-router`

原因很简单：
- `skill-only` 更稳
- `host-router` 更方便，但配置更深一层

---

## 8. 快速排错

### Codex 装完没反应

先重启 Codex 或开新会话。  
很多时候不是没装上，而是旧会话没有重新发现新 skill。

### OpenClaw 自动触发没生效

先看：

```bash
openclaw gateway status
```

如果刚改过配置，再执行：

```bash
openclaw gateway restart
```

### 只想确认文件装没装上

```bash
ls -la ~/.claude/skills/prompt-optimizer
ls -la ~/.codex/skills/prompt-optimizer
ls -la ~/.openclaw/workspace-prompt-optimizer
```
