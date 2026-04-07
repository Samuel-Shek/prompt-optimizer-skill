# 快速开始

如果你是第一次接触这个 Skill，不想一上来就研究全部细节，先看这页。

这页只做一件事：**帮你最快选对安装方式和接入路径。**

---

## 1. 先判断你属于哪种情况

| 你的情况 | 最推荐路径 |
|---|---|
| 我只想最快在本机终端里装好并开始用 | [CLI 快速安装与使用](cli-quickstart.zh-CN.md) |
| 我想在飞书里私聊一个专用“提示词优化器”机器人 | [飞书 / Lark 私聊接入教程](feishu-private-bot.zh-CN.md) |
| 我想在 Telegram 或 Discord 里私聊一个专用机器人 | [Telegram / Discord 私聊接入教程](im-private-bots.zh-CN.md) |
| 我只想先在 Claude / Codex / OpenClaw 本机里手动调用 | [CLI 快速安装与使用](cli-quickstart.zh-CN.md) |
| 我以后想在 OpenClaw 普通聊天里自动触发 | 先看 [CLI 快速安装与使用](cli-quickstart.zh-CN.md)，再开 `host-router` |

---

## 2. 新手最推荐的顺序

如果你完全是第一次用，建议按这个顺序：

1. 先走 [CLI 快速安装与使用](cli-quickstart.zh-CN.md)
2. 先在本机手动调用跑通
3. 再决定要不要接飞书 / Telegram / Discord
4. 最后再决定要不要开 OpenClaw 的 `host-router`

原因很简单：
- 手动模式最稳
- 私聊 Bot 第二稳
- 自动路由最方便，但配置也最深

---

## 3. 三种典型路径

### 路径 A：只想先在本机用

适合：
- Claude Code
- Codex
- OpenClaw 工作区

直接看：
- [CLI 快速安装与使用](cli-quickstart.zh-CN.md)

---

### 路径 B：想做一个飞书专用 Bot

适合：
- 想在手机上直接私聊
- 不想把提示词优化器和别的 agent 混在一起

直接看：
- [飞书 / Lark 私聊接入教程](feishu-private-bot.zh-CN.md)

---

### 路径 C：想做 Telegram / Discord 专用 Bot

适合：
- 想在 TG / DC 私聊里用
- 想一个平台一个专用 Bot

直接看：
- [Telegram / Discord 私聊接入教程](im-private-bots.zh-CN.md)

---

## 4. 你现在最该怎么选

### 最省事

先选：
- [CLI 快速安装与使用](cli-quickstart.zh-CN.md)

### 最适合飞书用户

先选：
- [飞书 / Lark 私聊接入教程](feishu-private-bot.zh-CN.md)

### 最适合想上手机私聊的人

先选：
- [Telegram / Discord 私聊接入教程](im-private-bots.zh-CN.md)

---

## 5. 一个原则

如果你只是想“先能用”，不要一上来就追求最复杂的自动化。

推荐顺序一直都是：

1. 手动模式
2. 私聊专用 Bot
3. 自动触发 / host-router

这样最不容易踩坑。

---

## 6. 相关文档

- [CLI 快速安装与使用](cli-quickstart.zh-CN.md)
- [飞书 / Lark 私聊接入教程](feishu-private-bot.zh-CN.md)
- [Telegram / Discord 私聊接入教程](im-private-bots.zh-CN.md)
- [各平台接入说明](platforms.zh-CN.md)
- [完整示例](examples.zh-CN.md)
