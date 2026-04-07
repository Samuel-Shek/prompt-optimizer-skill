# 飞书 / Lark 私聊接入教程

这份文档讲的是：**如何把 Prompt Optimizer 做成一个单独的飞书私聊 Bot。**

目标是：
- 用户只要私聊这个 Bot
- 这个 Bot 就只做提示词优化
- 不进群、不混到别的 agent 里

如果你是新手，最推荐的做法是：

**单独创建一个飞书 Bot 账号，然后把整个账号绑定到 `prompt_optimizer`。**

---

## 1. 你最终会得到什么

做完之后，用户在飞书里直接私聊这个 Bot：

```text
优化提示词：做个全球股票近况的调研
```

或者：

```text
帮我优化：我要让 Claude 帮我写一份产品方案
```

它就会直接回一段终版提示词。

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

- 单独创建一个飞书 Bot
- 只给 `prompt_optimizer` 用
- DM 使用 `pairing`
- 群聊使用 `disabled` 或者根本不配置群路由

这样好处是：
- 逻辑最干净
- 用户最好理解
- 不会把主 agent 和提示词优化器混在一起

---

## 4. 第一步：去飞书开放平台创建应用

去飞书开放平台创建一个机器人应用。

你最终需要拿到：
- `App ID`
- `App Secret`

如果你用的是国际版 Lark，需要记得后面把 `domain` 设成 `lark`。

---

## 5. 第二步：把飞书 Bot 配进 OpenClaw

在 `openclaw.json` 里加入一个专用账号。

示例：

```json
{
  "channels": {
    "feishu": {
      "enabled": true,
      "connectionMode": "websocket",
      "dmPolicy": "pairing",
      "groupPolicy": "disabled",
      "accounts": {
        "prompt_optimizer": {
          "appId": "<YOUR_FEISHU_APP_ID>",
          "appSecret": "<YOUR_FEISHU_APP_SECRET>"
        }
      }
    }
  },
  "bindings": [
    {
      "agentId": "prompt_optimizer",
      "match": {
        "channel": "feishu",
        "accountId": "prompt_optimizer"
      }
    }
  ]
}
```

关键点：
- `connectionMode: "websocket"`：最省事，通常也是默认值
- `dmPolicy: "pairing"`：第一次私聊先配对
- `groupPolicy: "disabled"`：不处理群聊
- `agentId: "prompt_optimizer"`：整个飞书 Bot 都交给提示词优化器

如果你用的是国际版 Lark，可以加上：

```json
{
  "channels": {
    "feishu": {
      "domain": "lark"
    }
  }
}
```

---

## 6. 第三步：重启网关

```bash
openclaw gateway restart
openclaw gateway status
```

---

## 7. 第四步：第一次私聊并批准配对

先去飞书私聊这个 Bot，随便发一句话。

然后在终端执行：

```bash
openclaw pairing list feishu
openclaw pairing approve feishu <CODE>
```

批准后，这个飞书账号就能稳定私聊它了。

---

## 8. 第五步：开始使用

以后用户就直接发：

```text
优化提示词：做个全球股票近况的调研
```

或者：

```text
帮我优化：我要让 Claude 帮我做一份竞品分析，重点看用户定位、价格策略、分发渠道和商业模式
```

也可以用后缀写法：

```text
做个全球股票近况的调研——优化提示词
```

---

## 9. 如果你还想在群里用

新手阶段不建议一开始就搞群聊。

因为群聊会额外涉及：
- `groupPolicy`
- 是否要求 `@mention`
- 群 ID / chat_id
- 误触发控制

如果你只是想让这个 Bot 稳定可用，**先只做私聊版**。

---

## 10. 常见问题

### 为什么推荐单独建一个飞书 Bot？

因为最省脑子：
- 私聊这个 Bot，就是提示词优化器
- 不用再记它是不是还兼任别的 agent

### 为什么推荐 `pairing`？

因为它最稳：
- 第一次手动批准
- 之后这个用户就可以持续私聊

### 什么时候要设置 `domain: "lark"`？

只有你用的是国际版 Lark 才需要。  
如果是国内飞书，默认 `feishu` 就行。

### 什么时候要用 `webhook`？

大多数新手都不用。  
直接用 `websocket` 最简单。

如果你切到 `webhook`，还要额外配置：
- `verificationToken`
- `webhookPath`
- `webhookHost`
- `webhookPort`

所以新手阶段不建议。

---

## 11. 最短流程总结

1. 飞书开放平台创建应用
2. 拿到 `appId` 和 `appSecret`
3. 写进 `openclaw.json`
4. 绑定到 `prompt_optimizer`
5. `openclaw gateway restart`
6. 私聊一次
7. `openclaw pairing approve feishu <CODE>`
