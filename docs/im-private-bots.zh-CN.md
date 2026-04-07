# Telegram / Discord 私聊接入教程

这份文档讲的是：**如何把 Prompt Optimizer 做成一个单独的 Telegram 或 Discord 私聊 Bot。**

目标是：
- 用户只要私聊这个 Bot
- 这个 Bot 就只做提示词优化
- 不进群、不混到别的 agent 里

如果你是新手，推荐你按这个思路做：

**一个平台一个专用 Bot + 只开私聊 + 整个账号绑定到 `prompt_optimizer`**

---

## 1. 你最终会得到什么

做完之后，用户可以直接私聊这个 Bot：

```text
优化提示词：做个全球股票近况的调研
```

或者：

```text
帮我优化：我要让 Claude 帮我写一份产品方案
```

Bot 会直接回一段终版提示词。

---

## 2. 前提

你需要先有：
- 一台已经装好 OpenClaw 的机器
- 这个仓库已经拉到本地
- `prompt_optimizer` 这个 agent 已存在
- `openclaw gateway` 能正常运行

建议先确认：

```bash
openclaw gateway status
```

---

## 3. 总体原则

最推荐的结构是：

- Telegram：建一个专用 Bot
- Discord：建一个专用 Bot
- 每个 Bot 都只给 `prompt_optimizer` 用
- DM 使用 `pairing`
- 群聊使用 `disabled`

这样好处是：
- 逻辑最干净
- 不会误伤主 agent
- 用户体验最简单

---

## 4. Telegram 私聊版

### 步骤 1：去 BotFather 创建 Bot

在 Telegram 搜索 `@BotFather`，然后：

1. 输入 `/newbot`
2. 按提示设置名字和用户名
3. 保存好它给你的 `Bot Token`

---

### 步骤 2：把 Telegram Bot 配进 OpenClaw

在 `openclaw.json` 里加入一个专用账号。

示例：

```json
{
  "channels": {
    "telegram": {
      "accounts": {
        "prompt_optimizer": {
          "botToken": "<YOUR_TELEGRAM_BOT_TOKEN>",
          "dmPolicy": "pairing",
          "groupPolicy": "disabled"
        }
      }
    }
  },
  "bindings": [
    {
      "agentId": "prompt_optimizer",
      "match": {
        "channel": "telegram",
        "accountId": "prompt_optimizer"
      }
    }
  ]
}
```

关键点：
- `dmPolicy: "pairing"`：第一次私聊先配对
- `groupPolicy: "disabled"`：不让它在群里接消息
- `agentId: "prompt_optimizer"`：整个 Bot 都交给提示词优化器

---

### 步骤 3：重启网关

```bash
openclaw gateway restart
openclaw gateway status
```

---

### 步骤 4：第一次私聊并批准配对

先去 Telegram 私聊这个 Bot，点 `/start`，随便发一句话。

然后在终端执行：

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

批准后，这个 Telegram 账号就能稳定私聊它了。

---

### 步骤 5：开始使用

以后用户就直接发：

```text
优化提示词：做个全球股票近况的调研
```

或者：

```text
帮我优化：我要让 Claude 帮我写一份产品方案，重点是用户是谁、为什么现在做、和竞品差异
```

---

## 5. Discord 私聊版

### 步骤 1：创建 Discord Bot

去 Discord Developer Portal：

1. 新建一个 Application
2. 添加 Bot
3. 复制它的 `Bot Token`

---

### 步骤 2：先把 Bot 拉进你自己的私密服务器

虽然目标是私聊，但 Discord 实际使用里，**先有共同服务器通常最稳**。

推荐做法：
- 先建一个自己的私密服务器
- 把这个 Bot 邀进去
- 再从 Discord 给它发私聊

---

### 步骤 3：把 Discord Bot 配进 OpenClaw

在 `openclaw.json` 里加入一个专用账号。

示例：

```json
{
  "channels": {
    "discord": {
      "accounts": {
        "prompt_optimizer": {
          "token": "<YOUR_DISCORD_BOT_TOKEN>",
          "dmPolicy": "pairing",
          "groupPolicy": "disabled"
        }
      }
    }
  },
  "bindings": [
    {
      "agentId": "prompt_optimizer",
      "match": {
        "channel": "discord",
        "accountId": "prompt_optimizer"
      }
    }
  ]
}
```

关键点：
- `dmPolicy: "pairing"`：私聊首次配对
- `groupPolicy: "disabled"`：不处理群聊
- `agentId: "prompt_optimizer"`：整个 Bot 绑定到提示词优化器

---

### 步骤 4：重启网关

```bash
openclaw gateway restart
openclaw gateway status
```

---

### 步骤 5：第一次私聊并批准配对

先去 Discord 私聊这个 Bot。

然后在终端执行：

```bash
openclaw pairing list discord
openclaw pairing approve discord <CODE>
```

---

### 步骤 6：开始使用

```text
优化提示词：做个全球股票近况的调研
```

```text
做个全球股票近况的调研——优化提示词
```

---

## 6. 两个平台怎么选

| 平台 | 推荐度 | 原因 |
|---|---|---|
| Telegram | 更推荐 | 创建和私聊流程更顺，最适合先跑通 |
| Discord | 也可以 | 能做，但通常建议先拉到一个自己的私密服务器里 |

如果你只想先做一个：

**先做 Telegram。**

---

## 7. 常见问题

### 为什么要做成专用 Bot？

因为这样最简单：
- 私聊这个 Bot，就是提示词优化器
- 不需要再记它在别的平台是不是还干别的

### 为什么不用群聊？

因为群聊要多处理：
- mention
- allowlist
- 群权限
- 误触发

而私聊版最适合新手，成本最低。

### 为什么用 `pairing`？

因为它最稳：
- 第一次手动批准
- 之后这个用户就可以继续私聊

---

## 8. 最短流程总结

### Telegram

1. `@BotFather` 创建 Bot
2. 把 `botToken` 写进 `openclaw.json`
3. 绑定到 `prompt_optimizer`
4. `openclaw gateway restart`
5. 私聊一次
6. `openclaw pairing approve telegram <CODE>`

### Discord

1. Developer Portal 创建 Bot
2. 拉进自己的私密服务器
3. 把 `token` 写进 `openclaw.json`
4. 绑定到 `prompt_optimizer`
5. `openclaw gateway restart`
6. 私聊一次
7. `openclaw pairing approve discord <CODE>`
