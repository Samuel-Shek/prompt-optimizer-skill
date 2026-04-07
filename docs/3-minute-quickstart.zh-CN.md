# 3 分钟上手

如果你只想 **3 分钟内先跑通一次**，看这页就够了。

---

## 1. 拉代码

```bash
git clone <repo-url> prompt-optimizer-skill
cd prompt-optimizer-skill
```

---

## 2. 选一个你正在用的平台

### Claude Code

```bash
bash scripts/install-local.sh claude
```

然后直接：

```text
/prompt-optimizer
```

再贴你的原始内容。

---

### Codex

```bash
bash scripts/install-local.sh codex
```

然后：
1. 重启 Codex，或至少新开一个会话
2. 输入：

```text
$prompt-optimizer
```

再贴你的原始内容。

如果你不想显式调，也可以直接发：

```text
优化提示词：做个全球股票近况的调研
```

---

### OpenClaw

只想先稳定跑通：

```bash
bash scripts/install-local.sh openclaw --mode skill-only
openclaw gateway restart
```

然后进 `prompt-optimizer` 工作区，直接贴内容。

如果你想在普通聊天里直接触发：

```bash
bash scripts/install-local.sh openclaw --mode host-router
openclaw gateway restart
```

然后直接发：

```text
优化提示词：做个全球股票近况的调研
```

---

## 3. 四种最短触发写法

```text
优化提示词：做个全球股票近况的调研
帮我优化：做个全球股票近况的调研
做个全球股票近况的调研——优化提示词
做个全球股票近况的调研——帮我优化
```

---

## 4. 只想确认有没有装上

```bash
ls -la ~/.claude/skills/prompt-optimizer
ls -la ~/.codex/skills/prompt-optimizer
ls -la ~/.openclaw/workspace-prompt-optimizer
```

---

## 5. 如果你想接手机私聊

直接跳这两页：

- [飞书 / Lark 私聊接入教程](feishu-private-bot.zh-CN.md)
- [Telegram / Discord 私聊接入教程](im-private-bots.zh-CN.md)

---

## 6. 如果你想看完整版

看这里：

- [快速开始总导航](get-started.zh-CN.md)
- [CLI 快速安装与使用](cli-quickstart.zh-CN.md)
