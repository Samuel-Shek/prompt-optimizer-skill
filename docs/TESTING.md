# 测试方法

[English summary](#english-summary) · 中文

这份文档写明提示词优化器做过哪些测试、每种测试具体怎么做、怎么判分，以及哪些结论成立、哪些不成立。数字都来自当时保存的运行记录；没有记录的细节，这里也不补。具体逐版数字见 [VALIDATION.md](../VALIDATION.md) 和 [CHANGELOG.md](../CHANGELOG.md)。

先说结论：

- 优化器能比较稳定地**保留原话**（v4 系列的设计目标）。
- 在强模型上，“先优化再执行”与“直接把原话交给模型”相比，**没有测到稳定的成品质量提升**，调用次数、token 和耗时反而增加。这是 v4.0.0 起改为仅手动使用的原因。
- 所有测试样本都小，评审大多与被测模型同属一家或同一家族，不能当作统计意义上的结论。

## 1. 测试分几层

| 层 | 测什么 | 用什么 | 是不是模型效果证据 |
|---|---|---|---|
| 考卷（`evals/`） | 优化器自身是否守规则；部分题比较原话与优化稿的执行结果 | `cases.json`、`run_eval.py`、Claude 命令行 | 是，但每条件只跑 1–3 次 |
| 针对性对照 | 某一版改动是否修掉了某个具体问题 | 为该问题写的 dev 题，新旧版各跑若干次 | 是，但题目是为这次修改写的 |
| 回归盲评 | 新版有没有把别处改坏 | 原有题目新旧版各跑一次，打乱顺序交独立评审 | 是，评审与被测同家族 |
| 与直接提问的固定对照 | 加入优化环节能否让最终成品明显更好 | 冻结的 12 题 × 3 轮，匿名 A/B 评分 | 是，本仓库里规模最大的一次 |
| 离线合约测试 | 评测脚本和规则文本是否按预期改动 | 用假命令行代替模型的单元测试 | **不是**，只证明脚本行为 |
| 网页实测 | 在真实聊天网页里是否照规则交付 | 手动提交、脚本机械计分、人工裁决 | 是，但每例只跑一次 |

## 2. 考卷：`evals/cases.json`

26 道中文虚构题，材料全部虚构，不含真实客户或个人信息。每题字段：

- `id`、`group`（分组）、`type`（考点）。
- `optimizer_input`：原样交给优化器的输入。
- `opt_checks`：优化器输出要满足的检查项（例如“字段名逐字保留，不增删字段”“示例来信内容不被改写成真实事实”）。这些是**人工检查项**，脚本不声称已执行。
- `effect`（部分题有）：效果对比用。`task` 是原话侧的任务，`material` 是两侧共用的材料，`criteria` 是评判标准；可选 `swap_material`（见下文 C02）和 `deployment_role`（见下文 C09）。
- `mech`（部分题有）：脚本能做的字面检查，见第 3 节。

### 分组

| 组 | 题号 | 用途 |
|---|---|---|
| `main` | C01–C12（12 题） | 日常基线与改进对比。覆盖短任务、严格格式提取、事实状态、多轮修改与撤销、材料夹带指令、只审不改、信息不足、决策、长期 Agent/System Prompt、编程任务、简单翻译、分批发送材料。 |
| `holdout` | H01–H04（4 题） | 原意是修改优化器时不拿来调规则，只查有没有改坏别处。**H04 已在 3.5.2 时用来发现问题，对该问题不再独立；H01–H03 没有效果题。** 所以 holdout 不能当作独立效果证据。 |
| `dev` | N01–N10（10 题） | 已知问题的回归题，每题对应一次具体修改：N01 禁用词不扩大、N02 相对时间保留、N03 待填空位照样交付、N04 撤销理由带出的限制、N05 严格 JSON、N06 简单任务写短与全角标点、N07–N10 材料含注入/无注入/规则段注入/混合引用。**这些题是为调规则写的，对应修改在这些题上通过，不能证明在别的题上同样有效。** |

“mech”不是一个分组，是题目上的机械检查字段。

英文版考卷 `evals/cases.en.json` 共 22 题（main 12、holdout 4、dev N01–N06），与 v3.5.3 时的中文题同编号、同考点，配合英文版 v3.5.3 使用（见第 3 节末）。

### 每题怎么出、怎么判

- 题目来自实际遇到的失误类型（多加交付物、扩大禁用词、把相对时间改成具体日期、示例名字被当真名、把材料里的注入删掉等），改写成虚构场景。
- 判优化器：逐条看 `opt_checks`，记通过、部分通过、不通过。
- 判效果：同一目标模型、同一中性 system prompt（中文“你是一个乐于助人的助手。”），分别执行原话和优化稿，按 `criteria` 比较两份结果。

两道题有特别处理：

- **C02（客户来信提取 JSON）**：优化器输入里带一封示例来信。若效果测试仍用这封信，优化稿里已经“见过”答案，对比不公平。所以效果测试换一封新来信（无人名、有预算）。脚本要求旧示例在优化稿中恰好出现一次才做精确替换，替换后再查“陈思远”“星河包装”“小型叉车”“20 台”等旧示例残留，命中即判 `verbatim_fail`，该题不形成对照。
- **C09（长期周报助手 System Prompt）**：默认两侧都按 user 角色发送（user-baseline）。另有可选的 system-deployment 模式，两侧同为 system、材料同样作为 user 输入。两种模式分开报告，不混算。

## 3. 评测脚本：`evals/run_eval.py`

需要 Claude Code 命令行（`claude`）。默认优化器 `opus`、执行模型 `sonnet`。

```bash
python3 evals/run_eval.py --out ./eval-out --opt-model opus --target-model sonnet
# 只跑指定题、目标每侧两轮
python3 evals/run_eval.py --out ./eval-out2 --ids C02,C09,N05 --rounds 2
# C09 的部署模式，单独报告
python3 evals/run_eval.py --out ./eval-out3 --ids C09 --effect-mode system-deployment
```

流程：

1. **优化阶段**：把 `SKILL.md` 加上 `references/methods.md` 作为优化器的 system prompt（注意：这里总是附上 methods，和实际使用时按需读取不同，manifest 里有记录），对每题的 `optimizer_input` 只跑一次。
2. **提取优化稿**：严格 JSON 题要求整段是只有一个非空字符串 `prompt` 的 JSON，否则记 `optimizer_format_failed`；其他题取唯一的顶层代码块，多个顶层代码块记 `multi_block`，未闭合记格式失败。既没有效果题也没有 mech 检查的题（如审阅题、元问题题）不做提取。
3. **执行阶段**（只对有 `effect` 的题）：原话侧 = `task` + 材料；优化侧 = 提取出的优化稿（若不含材料则附上材料）。两侧用相同模型、相同中性 system prompt、各自独立调用。`--rounds N` 只重复执行阶段，优化稿仍只有一份。
4. **生成盲评文件**：每对结果按“种子:题号:轮次”独立打乱 A/B 顺序，写成 `*.blind.md`（只含任务、材料、评判标准和 A/B 两份结果），对应关系写入 `blind_key.json`。**评审只应拿到 `*.blind.md`。**
5. **记录**：`manifest.json` 记下 SKILL、methods、考卷、脚本四个文件的 SHA-256，优化器与目标模型、题号、轮次、效果模式、随机种子、传给 `claude` 的固定参数和中性 system prompt，以及每次调用的退出码、耗时和输出哈希。任一侧失败、限流通知或空输出都不形成对照，并写明原因；脚本以非零状态退出。
6. **续跑**：`--resume` 只在上一条列出的源文件哈希和配置都一致时，复用哈希校验通过的成功输出；否则拒绝续跑、不改旧目录。`--workers` 和 `--timeout` 不在校验范围内，可以在续跑时改。

**脚本不打分。** 它只记录输出、做机械检查、生成盲评文件。效果好坏由人或另一个只读盲评文件的评审判断。

### 机械检查（`mech`）

都是字面检查和人工复核线索，命中不等于语义违规：

| 字段 | 检查对象 | 含义 |
|---|---|---|
| `banned` | 目标输出 | 禁用词是否出现 |
| `keep` | 优化稿和目标输出 | 必须逐字保留的片段是否缺失 |
| `carry` | 优化稿 | 应带入的限制是否缺失 |
| `widen_signals` | 优化稿 | 擅自扩大范围的信号词 |
| `ask_signals` | 目标输出 | 停下索要信息的信号词 |
| `strict_opt_json` | 优化器原始输出 | 是否是只含非空 `prompt` 的纯 JSON |
| `target_json_keys` | 目标输出全文 | 能否整段解析为 JSON 且键名正确 |
| `max_extra_headings` | 优化稿 | Markdown 标题数是否超限（纯文本标签不计） |
| `zh_fullwidth` | 目标输出 | 只记录半角标点线索 |
| `effective_split` | — | 原值保留，**明确未实现**，历史语义未知 |

### 旧版双语脚本

`evals/run_eval_v3.py` 是 v3.5.x 时期的双语脚本，英文版（仍为 v3.5.3）用它跑 `cases.en.json`：

```bash
python3 evals/run_eval_v3.py --lang en --out ./eval-out-en --opt-model opus --target-model sonnet
```

它没有 4.0.1 之后的修正（C02 精确换材料、mech 全部接入、失败不出假对照、续跑校验哈希等）。中文版请用 `run_eval.py`。

## 4. 针对性对照与回归盲评（v3.5.x）

v3.5.2 和 v3.5.3 的做法如下（v3.5.0、v3.5.1 的做法不同，例如 v3.5.1 英文版每题只跑一次、没有盲评；各版细节和数字以 [VALIDATION.md](../VALIDATION.md) 为准）：

1. **针对性对照**：为本次要修的问题写 dev 题，旧版和候选版中英文各跑 3 次，每次独立生成优化稿，数出现问题的次数（例如 v3.5.3 的“邮件题执行模型停下索要信息” 5/6 → 0/6）。
2. **回归**：原有 16 题中英文各跑 1 次，新旧两版输出打乱顺序、隐去版本，由一个独立的 Claude 子代理按每题检查项盲评，记“新版更好 / 旧版更好 / 相同”和不通过项。
3. 盲评后若再微调一句，重跑相关题并由执行测试的会话人工核对，**没有再盲评**，VALIDATION 里都单独注明。

v3.3 时还做过一次 GPT 侧独立复核（同一考卷，由 GPT 负责优化与执行），见 [evals/README.md](../evals/README.md)。

局限：多数条件 1–3 次；评分者与被测模型同属一家；dev 题为修改专门写。

## 5. v4 的“逐字照抄”候选对照（2026-10-29）

v4 把规则改成“原话为准、补充从属”。改版前做了一次候选对照（当时私有正式版为 3.5.5，未公开发布）：

- 优化器 claude-opus-5、执行器 sonnet、评审 opus，全部 effort high；工具、设置和 MCP 关闭。
- **针对性 18 份**：为“改意思”写的题，每个版本生成 18 份优化稿，逐份判是否严重失真（例如把 budget 扩为 spending、断言没有预约工具、新增“某地点不要出现”）。再各执行 18 次看执行失败。
- **中文 22 题回归**：由 opus 统一评审，人工复核失败项；只针对旧版结构的检查项按事先约定不计。
- **事先冻结三道门槛**：G1 候选严重失真为 0；G2 执行失败不多于正式版且没有目标失真；G3 回归不新增失败。批次上限事先定好。
- 结果：严重失真正式版至少 8/18，候选 1、2、3 分别为 2/18、3/18、1/18；三个候选都**没有**同时满足 G1–G3。之后由维护者决定采用候选 3 作为 4.0.0。
- 这批**没有盲评**：两版结构差别明显，做不到。独立审查另外发现，当时的 `claude -p` 执行器能看到运行者账号信息，有输出把它写了进去，说明这一批及以往用同一入口的测试隔离都不完整。

## 6. 与直接提问的固定对照（GPT 35 组，2026-11-03）

这是“先优化再执行”和“直接问”的正面比较。冻结的协议、评分标准、题目和逐题结果已公开在 [docs/testing/v4-vs-direct-20261103/](testing/v4-vs-direct-20261103/)（题目文件只删除了指向本机证据的字段）。

**设计**

- 固定被测版本 4.0.0（`PROTOCOL.json` 里有 SKILL 的 SHA-256），运行前冻结题库、协议、评分标准和脚本。
- 题库 12 题：8 中文、4 英文；六类（沟通、周报助手、结构提取、零散多轮、事实约束写作、决策规划）各 2 题；6 道旧题、6 道新写的虚构题（K01–K06）。每题 3 轮。
- 原话侧保留完整需求、全部修改和相同材料，只去掉“帮我优化”这类控制语；优化稿不做人工修补。system prompt 类任务两侧角色相同。两侧用相同设置、独立空白会话，按冻结顺序交替运行。
- 计划两条链路：GPT（gpt-6.1-sol 优化和执行，effort max）和 Claude（opus-5 优化、sonnet-5 执行，effort high）。
- 不因效果不好追加题目、候选或轮次；拒绝、模型不符或隐私污染就停止受影响的链路。

**怎么盲、怎么判**

- 先做机械检查，再把原任务和匿名 A/B 两份成品交给独立的 GPT 空白会话评分。评审看不到优化稿、版本标签和 A/B 映射。
- 评分（`JUDGE-RUBRIC.json`）：满分 10，要求满足 0–4、事实与逻辑 0–3、可用性 0–3；另判每份是否硬通过（每条原始硬要求，含字数和逐字文本，true/false/歧义）、是否需要实质返工。
- **“明显胜”的定义**：一侧硬通过而另一侧需要实质返工；或双方都硬通过且分差 ≥ 2，并能指出具体的实质改善（不算排版偏好）。双方都失败不算谁胜。拿不准记歧义，不强判。
- **稳定胜出**：3 轮中至少 2 次明显胜且没有输。推广门槛：每条链路至少 8 题稳定胜出，其中至少 4 道新题。
- 正式评分前，用两份已知优劣的样本并交换位置校验评审，两项都通过（只说明这类明显错误能被识别，不认证评审全面准确）。歧义、机械失败和严重问题由运行者和同一独立审查者在不知道映射时核对，冻结评分和更正记录后才解盲。

**结果**

- GPT 链路：36 组中 35 组有效（C01 第一轮预检时取消）。明显胜 0、实质平 35、明显负 0；稳定胜出 0/12 题。35 份优化稿保真全部通过。成品硬要求确定通过：原话 29/35、优化 30/35，其余为歧义，没有确定失败；这 1 份的差别不能当作质量提升。
- 用量：优化整链的输入、输出 token 都约为直接执行的 2.05 倍；同一有效配对的耗时中位数，直接问 28.0 秒，优化生成加执行 77.1 秒。
- Claude 链路：首次调用被订阅入口拒绝（403），0 组有效。这是证据缺口，不是 Claude 的质量结论。

**这次测试的局限**

- 评审是同一模型家族的独立会话，不是跨家族验证。
- 评审运行环境的工作目录名暴露了研究主题和 v4 线索，A/B 映射仍隐藏；所以只能算“未完全隐藏背景的匿名评审”。
- 首阶段 39 次成功调用后发现命令行仍附加了运行者的私人记忆和技能目录，这些调用全部剔除，与得分无关；之后只对评测子进程关闭记忆与技能，并逐条核查实际输入。
- 题目原话本来就写得较完整，GPT 在 max 档直接回答已经很强，评分有上限效应。结果不证明优化器对所有杂乱口语需求、较弱模型或长期复用的任务书都没有价值，这些用途本次没有测。

## 7. Gemini 对照（6 组）

与上一节同期计划了 Gemini 链路 36 组，只完成了 6 组完整对照，每题一轮。汇总为确认明显胜 0、平 5、负 0、幅度歧义 1，没有稳定胜出；其中一组（K05）的优化稿擅自增加了一项必须通过的条件，保真失败。配对和判定口径与第 6 节相同。这一链路的逐组原始记录没有随本仓库公开，这里只能给出汇总。

## 8. 离线合约测试（4.0.1–4.0.4）

4.0.1 之后的修订由一个模型实施、另一个模型独立审阅，每轮都在本机跑一套离线测试：用一个假的 `claude` 命令行返回预设文本，检查评测脚本和规则文本的行为。覆盖的内容包括：

- 严格 JSON 的解包与拒绝、单个外层代码块保留内层、多个顶层代码块拒绝、未闭合代码块拒绝；
- C02 只把新材料送到两侧、旧示例残留即拒绝；C09 的 user 基线与 system 部署模式；
- 优化器或目标失败、限流、超时、无效 UTF-8 不形成对照，退出码非零；
- 续跑时任一源文件哈希或配置不一致即拒绝，篡改过的输出会重跑，旧派生文件隔离；
- A/B 标签在前面题目状态变化时保持稳定；
- `SKILL.md` 和 `methods.md` 只有允许的文字改动，原有题目不变。

4.0.1 为 28 项，4.0.2 为 66 项，4.0.3 和 4.0.4 为 76 项，候选与安装副本都全部通过。**这些测试不调用真实模型，不是效果证据。** 测试文件依赖各版本的私有快照目录做逐字对比，没有随本仓库公开。

## 9. 网页实测（4.0.2–4.0.4）

在 Gemini 4 Argon（思考“高”）和 ChatGPT 网页上手动提交，每例一个新会话：

- **优化器阶段**：T1–T8 共 9 项，覆盖逐字保留（标点、代码、否定）、补充从属和两层格式、已明确的任务少改、欠规格不杜撰、混合引用中的注入、旧示例实体不扩散、审阅题不出重写稿、Manual-only 的显式与未显式调用（网页上只能模拟）。用一个小脚本按每例的判据机械计分。
- **目标执行阶段**：对部分题分别用原话和优化稿在新会话里执行，以盲标签（A/B）记录，再按判据计分。
- 4.0.2 上 T5 失败：优化器把材料里的注入注释删掉了。这促成了 4.0.3。4.0.3 重测 13 项判据（优化器 9 + 目标 4），12 项通过，唯一失败是 T5 的原话侧对照（直接把原话交给执行模型的那一侧）；优化侧全部通过。只跑一次，只测了 Gemini。
- 4.0.4：用文件附件方式提交 10 例回归，GPT、Gemini 各一次，机械计分 9/10、8/10；3 处关键词未过，由两个模型分别做语义裁决，判为合规。原话与优化稿的目标对照没有测。一个旧判据（T8b）被确认是误判。
- 同一份输入在输入框键入和文件附件两种提交方式下表现可能不同（例如反斜杠），根因没有最终证明，所以 4.0.4 没有为此加规则。

**这些都是单次小样本**，只能说明“这几例照规则交付了”，不能说明模型行为已普遍修复，也不能说明有质量净收益。

## 10. 哪些结论成立，哪些不成立

成立（有记录支持）：

- v4 规则下优化稿能较稳定地保留原话：固定对照中 35/35 份保真通过；候选对照中严重失真从至少 8/18 降到 1/18。
- 在本次 12 题、GPT max 档的条件下，加入优化环节没有让成品明显更好（35 组 0 胜），且用量约翻倍、耗时增加。
- 3.5.x 各版针对的具体问题，在对应 dev 题上次数下降（见 VALIDATION）。

不成立或没有证据：

- “用了优化器结果明显更好”——没有测到。
- “在所有模型、所有用途上都无效”——也不能这样外推；较弱模型、杂乱口语需求、长期复用的任务书没有系统测过。
- 4.0.1–4.0.4 修复了真实模型的行为——只有离线测试和单次网页样本。
- Claude 链路的 v4 对直接提问结论——入口 403，没有数据。
- 统计显著性——多数条件只有 1–3 次（部分历史复测更多），没有做统计显著性检验。

## 11. 自己复现

1. 安装 Claude Code 命令行并登录。
2. 建议在一个干净环境里运行：关闭个人记忆、自定义技能和 MCP，避免命令行把账号或私人上下文带进测试（我们在 10-29 和 11-03 都踩过这个坑）。
3. 运行第 3 节的命令，把 `*.blind.md` 交给另一个模型或人评审，评完再看 `blind_key.json`。
4. 想复现第 6 节的固定对照，可以用 `docs/testing/v4-vs-direct-20261103/` 里的题目、协议和评分标准；原运行脚本依赖本机环境，没有公开。

发现优化器做错的真实案例，欢迎[提交失败案例](https://github.com/Samuel-Shek/prompt-optimizer-skill/issues/new?template=bad-case.yml)。

## English summary

How Prompt Optimizer was tested, in brief. All numbers come from saved run records; details that were not recorded are not filled in here.

- **Exam (`evals/`)**: 26 fictional Chinese cases in three groups: `main` (12, everyday baseline), `holdout` (4; no longer independent, since H04 was used to find a bug and H01–H03 have no effect test) and `dev` (10 regression cases written for specific fixes). `mech` is a per-case field for literal checks, not a group. `run_eval.py` runs the optimizer once per case, runs the same target model on the original request and the optimized prompt with an identical neutral system prompt, writes A/B-shuffled blind files, and records SHA-256 hashes of all sources. It does not score quality. The English edition (v3.5.3) uses `run_eval_v3.py --lang en` with `cases.en.json`.
- **Fixed comparison against asking directly (2026-11-03)**: 12 frozen cases × 3 rounds, with GPT-6.1 Sol at max effort as both optimizer and executor, and an anonymous A/B judge in a separate GPT session. Result: 35 valid pairs, 0 clear wins, 35 ties, 0 losses; 35/35 optimized prompts kept the original wording. The optimizing chain used about 2.05× the tokens of asking directly. The Claude route got 0 valid pairs (403). Limits: the judge came from the same model family, and the judge's working directory leaked the study topic. Protocol, rubric, cases and results are in [`docs/testing/v4-vs-direct-20261103/`](testing/v4-vs-direct-20261103/).
- **Gemini**: 6 of 36 planned pairs completed: 0 wins, 5 ties, 0 losses, 1 ambiguous. In one pair (K05) the optimized prompt added a condition, so it failed fidelity.
- **4.0.1–4.0.4**: these revisions were verified only statically and offline. The offline tests (76 for 4.0.4) use a fake CLI and are not model evidence. Web checks were single small samples.
- **Not supported by the evidence**: that the optimizer makes results clearly better; that it is useless everywhere; any statistical significance.
