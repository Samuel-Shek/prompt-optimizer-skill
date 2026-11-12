# 提示词优化器（prompt-optimizer）：Claude Code / Codex 提示词优化 Skill

[English](README.md) · **简体中文**

提示词优化器是一个 Skill，能把随手写的需求或已有的提示词改成一份可以直接复制的提示词；它只改提示词，不替你做任务。它适合使用 Claude Code、Codex，或把指令粘贴到 ChatGPT GPTs、Claude Projects 的人。在 Claude Code 中，用下方两条命令即可安装。

当前版本 **v4.1.2** · MIT 许可 · [版本记录](CHANGELOG.md) · [测试方法](docs/TESTING.md) · [验证记录](VALIDATION.md)

## 快速安装

**Claude Code（插件市场）**

```text
/plugin marketplace add Samuel-Shek/prompt-optimizer-skill
/plugin install prompt-optimizer@prompt-optimizer
```

手动安装、ChatGPT GPTs / Claude Projects 用法，以及安装前检查类似功能的说明，见[安装](#安装)。

试用后有建议，欢迎到 [Discussions](https://github.com/Samuel-Shek/prompt-optimizer-skill/discussions) 留言；失败案例请[提交 Issue](https://github.com/Samuel-Shek/prompt-optimizer-skill/issues/new?template=bad-case.yml)。

## 看一个例子

下面是按 v4.1.0 规则手写的示意，不是模型实录，真实运行细节可能不同；会议需求是虚构的。另见[早期真实运行（v3.5，2026-10-22）](#早期真实运行v352026-10-22)。

**你说的：**

```text
使用 $prompt-optimizer：把我下面的会议要点整理成一条发给团队的微信消息，200 字以内，语气客气但直接。
会议要点：周四前交初稿；小王负责数据部分；预算还没批，先别买工具。
```

**它给你的提示词：**

```text
用户原话（按此执行）：
把我下面的会议要点整理成一条发给团队的微信消息，200 字以内，语气客气但直接。
材料：
会议要点：周四前交初稿；小王负责数据部分；预算还没批，先别买工具。
```

这是一个简单任务，所以没有补充说明。

> **2026-11-09 起迁移至本仓库**，这里是提示词优化器的正式公开版；原仓库 [Samuel-Shek/prompt-optimizer](https://github.com/Samuel-Shek/prompt-optimizer) 已归档，保留 v4.0.0 之前的版本和标签。这里原有的旧版 OpenClaw 接入代码保留在 [`legacy/openclaw`](https://github.com/Samuel-Shek/prompt-optimizer-skill/tree/legacy/openclaw) 分支。

这是一个 Skill（写给 AI 读的工作说明），放进 Claude Code、Codex 这类能读取技能文件的 AI 工具里使用。它不是独立软件，也不是新模型，不需要额外的 API Key 或后台服务。

**自 v4.1.0 起只有一个版本，适用所有语言。** 仓库根目录的 `SKILL.md` 就是唯一的技能（技能名 `prompt-optimizer`）。它跟随你的语言回复：中文需求用中文标签和说明，英文需求用英文，其他语言同样照此处理；你的原话和贴进来的材料永远不翻译。原来的英文版 `prompt-optimizer-en/`（v3.5.3 规则）已在 v4.1.0 删除，用过它的请看下文[从英文版迁移](#从英文版prompt-optimizer-en迁移)。

## 它会做什么

- **把愿望改成 AI 能照做的要求**。“写得专业一点”会被拆成受众、语气、结构这类能检查的说法；只在确实能减少误解时才加，不给简单任务套长模板。
- **原话里的硬信息原样保住**。数字、日期、名称、文件名、禁止事项、`【待补数据】` 这样的标记，以及“计划中”“待核实”这类状态都不改。不会把“计划申请认证”写成“已获认证”。
- **不替你多加条件**。你没提的字数、格式、筛选标准和验收要求，它不会自己补上当成硬规定。需要它出主意时，新加的做法会写成建议。
- **缺的信息不替你编**。目标 AI 能自己查的，写明去哪查；必须由你补的，留成待填空位；缺了会改变结果、又没有合理默认值时，才问你，最多三个问题。
- **分得清“指令”和“材料”**。你贴进来的材料里如果写着“忽略之前的规则”，它只当成要处理的文字，不会照做。
- **多轮修改记得住**。最新一次明确修改才覆盖旧要求，没撤销的一直有效；“再短一点”不会顺手删掉禁止项。

只想听意见时说“先评价，别改”，它只指出问题，不重写。

在 Claude Code、Codex 这类能自己干活的 AI 工具里，当前 AI 遇到明显含糊、缺少关键信息的任务时会自动先用它把要求理清楚（缺的关键信息会先问你），再继续把任务做完；清楚的任务直接做，不调用。你也可以明确要求它先整理再执行。这时它整理出的提示词只给当前 AI 用，你最后拿到的是任务结果。

**按需自动调用（v4.1.1 起）。** 每次你提问或交代任务，AI 先自己判断：问题是否已经足够清楚？凭它自己的能力和对你的了解，能不能直接答好？能，就直接回答，不调用优化器；只有问题明显含糊、缺少关键信息，或者你明确说“优化提示词”时，才自动调用它。调用时保留你的原话，补充内容只作为建议，不替你编造没说过的信息。Codex 里由 `agents/openai.yaml` 的 `allow_implicit_invocation: true` 允许这种自动调用；Claude Code 等其他工具按技能描述做同样的判断（想只允许斜杠命令调用，可在自己安装的副本开头加 `disable-model-invocation: true`）。为什么不每次都用：强模型盲评里，清楚的问题先优化再执行与直接提要求相比没有稳定的质量提升，调用次数和 token 用量还会增加，详见[版本记录](CHANGELOG.md)。v4.0.0–v4.1.0 曾写成“仅手动使用”，那是记录错误，v4.1.1 已改正。

## 早期真实运行（v3.5，2026-10-22）

下面是 2026-10-22 一次测试的真实输出，一字未改；会议内容是虚构的。**注意：这是 v3.5 时期的输出，结构是“当前生效要求＋原始输入”；v4 起改为“用户原话＋从属补充”，见下文“输出长什么样”。**

**你说的：**

```text
帮我优化一下这个提示词：把我下面的会议要点整理成一条发给团队的微信消息，200 字以内，语气客气但直接。
会议要点：周四前交初稿；小王负责数据部分；预算还没批，先别买工具。
```

**它给你的提示词：**

````markdown
# 任务
把下面的会议要点整理成一条可直接发给团队的微信消息。

# 当前生效要求
- 渠道与受众：微信消息，发给本团队成员。
- 篇幅：200 字以内（含标点）。
- 语气：客气但直接——有礼貌的开头/结尾即可，不堆敬语，不绕弯子，事项交代清楚。
- 内容范围：完整覆盖下列三条要点，不新增未提供的信息（不要自行补具体日期、全名、金额、工具名称或理由）。
- 事实保真：预算状态是“尚未批准”，不要写成已否决或已通过；“先别买工具”是当前暂缓，不是永久禁止。
- 责任人：只保留已明确的分工（数据部分由小王负责）；原文未指明责任人的事项，不要擅自指派给某人。
- 格式：纯文本，适合微信直接粘贴发送；可用换行分条，不使用 Markdown 标记（如 #、*、**）。
- 输出：只输出这条消息正文本身，不加说明、标题或备选版本。

# 会议要点（待整理内容）
1. 周四前交初稿。
2. 小王负责数据部分。
3. 预算还没批，先别买工具。

---

# 原始输入（核对用，不单独执行）
把我下面的会议要点整理成一条发给团队的微信消息，200 字以内，语气客气但直接。
会议要点：周四前交初稿；小王负责数据部分；预算还没批，先别买工具。
````

**同一个 AI 分别拿原话和这份提示词去写，结果是：**

| 直接用原话 | 用优化后的提示词 |
|---|---|
| 多写了“有相关问题可以直接找他对接”“等审批结果出来后再统一安排”，会议里没说过这两件事；还用了 `**加粗**`，贴进微信会显示成星号 | 三条要点照原样写清，没有多加事项，纯文本可以直接粘贴 |

这只是一次运行的结果。简单任务直接问，很多时候也能写对。

## 安装

**安装前先查有没有类似功能（让 AI 帮你装时也一样）。** 先检查当前工具里是否已经装了同名的 `prompt-optimizer`，以及任何功能类似的提示词优化技能、插件或自定义指令（名字不同也算，例如 prompt-enhancer、提示词改写、“先帮我优化提示词再执行”这类全局规则）。发现了就先告诉用户找到了什么、在哪里，由用户决定替换、保留还是并存；不要直接覆盖，也不要不打招呼地另装一份。

**Claude Code 一键安装（插件市场）**

```text
/plugin marketplace add Samuel-Shek/prompt-optimizer-skill
/plugin install prompt-optimizer@prompt-optimizer
```


**手动安装**

1. 下载：

   ```bash
   git clone --branch v4.1.2 --depth 1 https://github.com/Samuel-Shek/prompt-optimizer-skill.git prompt-optimizer
   ```

   也可以在[发布页](https://github.com/Samuel-Shek/prompt-optimizer-skill/releases/tag/v4.1.2)下载压缩包。

2. 把下载得到的整个 `prompt-optimizer` 文件夹放进 AI 工具的技能目录，保留里面的 `references/` 和 `agents/`。常见位置：Claude Code 是 `~/.claude/skills/`，Codex 是 `~/.agents/skills/`，WorkBuddy 是 `~/.workbuddy/skills/`，以各工具当前文档为准。已经装过同名或类似技能的，按上面的说明先确认，别把自己改过的内容覆盖掉。

3. 新开一个会话，让工具重新读取技能。

**ChatGPT GPTs、Claude Projects 或其他聊天应用：** 将 [`SKILL.md`](SKILL.md) 的内容粘贴到自定义指令中（需要可选方法时，可一并加入 [`references/methods.md`](references/methods.md)）。清楚的问题直接回答；只有需求明显含糊、缺少关键信息，或你明确要求时，例如“优化这个提示词：……”，它才介入。审阅请求和普通聊天仍按原意回答。

## 从英文版（prompt-optimizer-en）迁移

v4.1.0 删除了英文版和 `prompt-optimizer-en/` 目录。你电脑上的旧副本不会被删，但也不会再更新。装一次合并版，再删掉旧的，避免同时存在两份：

- **Claude Code 插件 `prompt-optimizer-en@prompt-optimizer`**：这个插件名作为旧名别名保留，v4.1.0 起装的是同一个合并版技能（技能名 `prompt-optimizer`），继续更新不会报错。想换回主名：

  ```text
  /plugin uninstall prompt-optimizer-en@prompt-optimizer
  /plugin install prompt-optimizer@prompt-optimizer
  ```

  `prompt-optimizer` 和 `prompt-optimizer-en` 只装一个，两者现在内容相同。
- **插件市场是从已归档的旧仓库添加的**（`/plugin marketplace add Samuel-Shek/prompt-optimizer`）：旧仓库不再更新。两者的市场名都是 `prompt-optimizer`，先删再加：

  ```text
  /plugin marketplace remove prompt-optimizer
  /plugin marketplace add Samuel-Shek/prompt-optimizer-skill
  /plugin install prompt-optimizer@prompt-optimizer
  ```
- **手动安装**：删掉技能目录里的旧 `prompt-optimizer-en` 文件夹（如 `~/.claude/skills/prompt-optimizer-en`、`~/.agents/skills/prompt-optimizer-en`），按上文安装 `prompt-optimizer`，再新开会话。
- **点名调用**：Codex 用 `$prompt-optimizer`，手动安装到 Claude Code 的用 `/prompt-optimizer`。插件里的技能带命名空间：主插件是 `/prompt-optimizer:prompt-optimizer`，旧名别名是 `/prompt-optimizer-en:prompt-optimizer`。原来的 `/prompt-optimizer-en:prompt-optimizer-en` 和 `$prompt-optimizer-en` 已不存在，旧名只在技能描述里提到。
- **行为变化**：英文版是 v3.5.3 结构（“当前生效要求＋原始输入”），合并版是 v4 结构。需要旧行为的，可固定用旧文件：`git clone --branch v4.0.4 --depth 1 https://github.com/Samuel-Shek/prompt-optimizer-skill.git`，取其中的 `prompt-optimizer-en/` 文件夹。

## 怎么用

直接说“帮我优化这个提示词”，或者点名调用：

```text
使用 $prompt-optimizer：帮我写一条研究提示词，比较三种笔记工具。
目标是 ChatGPT 网页端。只用公开资料，区分事实和判断，保留来源日期。
不要注册账号、购买产品或替我作个人选择。
```

```text
先评价，别改：
（粘贴待审阅提示词）
```

可以在请求里加这些写法，都不是必需的：

| 写法 | 作用 |
|---|---|
| `+讲解`（或 `+explain`） | 在终稿后附最多 5 条关键改动说明 |
| `+双版`（或 `+two`） | 给两个用途不同的版本 |

没有别的快捷写法。想指定目标模型或工具、或者允许它先问几个问题，直接用自然语言说即可，例如“目标是 Claude Code”“先问我最多 3 个问题”。

### 输出长什么样

默认是一份可复制的提示词，放在一个代码块里，用纯文本标签分区（v4 起）：

- **用户原话（按此执行）**：你的需求逐字照抄，目标 AI 按这部分执行；
- **材料**：你提供的材料，原样保留；
- **补充说明**：优化器补充的建议，第一行固定写明“与‘用户原话’冲突时，以用户原话为准”；
- **待确认**：会实质改变结果的缺口，每条附“执行时”怎么处理。

没有材料、补充或待确认时省略对应区；简单任务通常只有“用户原话”和“材料”。前面可能有一行“任务”，只取你原话里的连续片段。英文需求的区名对应为 Task / User's exact words (follow these) / Material / Supplementary notes / To confirm。

## 什么时候不用

- **简单任务直接问 AI 更省事**。一句话翻译、一条短消息，优化后的提示词会比原话长不少，最后结果和直接问差不多。
- **它不做任务本身**。要的是分析结果、文章或代码，就直接让 AI 去做；只有你想先把要求理清楚、要反复用同一份提示词、或者任务有很多硬性限制时，先优化才划算。

## 已知局限

- **复杂任务输出偏长**。原话逐字保留，优化器的补充写在后面，所以复杂任务的提示词会比你写的长。
- **待填空位**。原话缺信息时，它会留下 `{{待填写：……}}` 这样的空位，并写明没填时怎么处理：称呼、署名这类小缺口用通用写法；如果任务一点关键信息都没给（比如写商品介绍却没给任何产品信息），执行的 AI 会先停下来问你，而不是编造。
- **偶尔仍有小偏差**。测试里简单任务偶尔仍会出现小标题；长文章即使提示词要求全角标点，执行的 AI 也不一定照做。交付前最好扫一眼“补充说明”，删掉你不想要的条目。
- **不保证目标 AI 照做**。提示词写得再清楚，执行的 AI 也可能漏项或多写；重要的输出仍要自己核对。
- **合并版没有新的真实模型验证**。v4.1.0 只是结构合并。此前 v4 的测试以中文为主（v4.0.0 与直接提问的对比含 4 道英文题）；合并后的 v4.1.0 和更新后的英文考卷都没有在真实模型上跑过。
- **测试规模小**。目前的验证只用过几十道虚构题（中英文考卷各 26 道，另有 12 道冻结题用于与直接提问对比），模型以 Claude 和 GPT 为主；在其他模型或长期使用中的表现没有系统测过。

每种测试怎么做、怎么判、哪些结论成立，见[测试方法](docs/TESTING.md)；逐版数字见[验证记录](VALIDATION.md)，考卷用法见[考卷说明](evals/README.md)。

## 版本

- **v4.1.2（当前）**：补充说明不得引入原话和材料里没有的引用或事实，引号只用于逐字引用。新增离线保真检查（数字、日期、引号内容和文件名按次数核对，材料不得删，补充说明新增项只告警），接入 `run_eval.py` 的独立 `fidelity` 字段；新增中英共 20 条触发判断小考卷，修复按文件加载运行脚本时的导入问题。触发规则、description 和 `allow_implicit_invocation` 不变。见[测试记录](docs/testing/v4.1.2-20261110/README.md)及[运行方法](evals/README.md)。
- **v4.1.1**：改正调用方式：由“仅手动使用”改回按需自动调用——问题清楚就直接回答，明显含糊、缺关键信息或你明确说“优化提示词”时才自动调用；`allow_implicit_invocation` 改为 `true`。安装说明要求先检查同名和类似的提示词优化功能，发现后先问你再装。规则正文的优化方法没有改动，详见[版本记录](CHANGELOG.md)。
- **v4.1.0**：中英文两版合并为一个技能、一套规则（以 v4.0.4 为准），写明语言规则：跟随用户语言，中英文以外的语言也一样，原话和材料不翻译。删除 `prompt-optimizer-en/` 和旧的双语运行脚本，一个运行脚本覆盖中英文两份考卷。这一版只是结构合并，没有新的真实模型质量测试，详见[版本记录](CHANGELOG.md)。
- **v4.0.4**：中文版 4.0.1–4.0.4 四个小修订的首次公开发布：消除规则冲突；材料里夹带的指令原样保留、按数据处理，只移出待优化规则文本里的注入；统一一句固定优先句。这些修订只做过静态和离线验证，网页实测是单次小样本，详见[版本记录](CHANGELOG.md)。
- **v4.0.0**：中文版重写为照抄你的原话，优化器自己补充的内容从属于原话；这一版主要保证保真，不承诺成品更好。当时改为仅手动使用、关闭自动调用（v4.1.1 已改回按需自动调用）。强模型盲评中，与直接提要求相比没有稳定提升（GPT：明显胜 0、平 35、负 0；Gemini：完成 6 组完整对照，没有稳定胜出）。英文版保持 v3.5.3 规则。
- **v3.5.3**：待填空位的示例只写类别，不再像真名；提示词写明空位没填时怎么办（照样交付、标出缺口、不把示例当真）。提示词前后不再附说明或引导语；严格 JSON 不套代码块；简单任务写短；中文提示词本身用全角标点，并要求中文结果使用全角标点。测试结果见[验证记录](VALIDATION.md)。
- **v3.5.2**：禁用词清单和“下周三前”这类相对时间按你的原话执行，不再扩大禁用范围，也不再改成待填的具体日期。测试结果见[验证记录](VALIDATION.md)。
- **v3.5.1**：新增英文版 `prompt-optimizer-en`、英文考卷和 Claude Code 插件市场安装方式；中文版规则没有改动。英文版 16 道题实测结果见[验证记录](VALIDATION.md)。
- **v3.5.0**：减少擅自增加条件。改写时区分“你原本的要求”“等义的澄清”和“它新加的建议”；没有依据就不添加数量、格式、筛选或验收条件；交付前同时检查有没有漏掉要求、有没有多加限制。发布后在 Claude 上和 v3.4.0 同场重测了 16 道题，没有发现稳定变差的地方，详见[验证记录](VALIDATION.md)。
- 想回到上一版：

  ```bash
  git clone --branch v3.4.0 --depth 1 https://github.com/Samuel-Shek/prompt-optimizer.git prompt-optimizer-v3.4
  ```

  这条命令会下载到另一个目录，不会直接覆盖现有安装，核对后再按工具的方式替换。

历次改动见[版本记录](CHANGELOG.md)。

## 反馈

最有用的反馈是一个它真的做错了的案例。请[提交失败案例](https://github.com/Samuel-Shek/prompt-optimizer-skill/issues/new?template=bad-case.yml)，写明你的输入、它给出的结果和你期望的结果。确认的案例会脱敏后加进 `evals/` 考卷，之后每个版本都要拿它检验。想法和用法问题请到 [Discussions](https://github.com/Samuel-Shek/prompt-optimizer-skill/discussions)。

## 与 Ego Lite、ChatGPT Pro 组合

这个优化器也可以作为一套研究流程的第一步：任务含糊需要整理或你明确要求时，当前 AI 先用它整理任务，再交给 ChatGPT 的 Pro 模型做研究，最后由当前 AI 核验并交付。完整组合包见 [ego-pro-research](https://github.com/Samuel-Shek/ego-pro-research)。优化器本身不依赖这套流程，也不负责操控浏览器。

## 设计参考与许可

设计时参考过多份公开的提示词优化资料，只借鉴思路，没有收入原文，详见[设计参考](docs/design-references.md)。`references/methods.md` 里的四种按需方法，出处写在该文件内。

`SKILL.md` 是唯一入口（适用所有语言），`references/methods.md` 是按需方法，`agents/openai.yaml` 是可选的界面信息，`evals/` 是维护时用的考卷，不会注入生成的提示词。

本仓库原创内容采用 [MIT](LICENSE) 许可。外链的第三方资料归原权利人所有。
