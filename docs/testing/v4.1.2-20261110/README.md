# v4.1.2 测试记录（2026-11-10）

本页分开记录 v4.1.2 的本地离线验收，以及此前维护者对私有 v4.1.1 加引号规则版本的模型测试。v4.1.2 逐字收录这条规则和评测代码；此前模型结果不冒充本次重新跑出的结果。

> **非 Claude 正式考卷，由 Codex（gpt-6-astra）代跑。** 此前测试时 Claude 命令行不可用，所有模型结果由 Codex（gpt-6-astra，推理 medium）完成：把选定的 `SKILL.md` 当系统指令，经模拟 `claude -p` 参数的转接脚本调用 `codex exec`。被测模型、目标模型和评审是同一个模型。结果只能作为参考信号，不能与历次 Claude 考卷直接比较，也不能证明真实宿主的自动路由已生效。

## 1. 测试层次与方法

| 层次 | 文件或方法 | 是否调用模型 |
|---|---|---|
| 维护者私有离线合约测试 | 76 项，不在公开仓库；旧基线加逐字替换，保留原断言 | 否 |
| 机械保真检查 | `evals/fidelity.py`、`evals/test_fidelity.py` | 否，读取已有输出 |
| 触发判断小考卷 | `evals/trigger_cases.json`、`evals/trigger_eval.py`、`evals/test_trigger_eval.py` | 小考卷调用模型，单元测试不调用 |
| 原有考卷 | `evals/run_eval.py --lang zh|en`、两份 cases 文件 | 是；下述历史结果为 Codex 代跑 |

- 触发判断包含中英各 10 条虚构请求，预期分为 `direct` 与 `invoke`。清楚的问答、翻译、写作、代码和表格整理应直接回答；明显含糊、缺关键信息或明确要求优化提示词时应调用。模拟宿主读取技能的 description，并列出两个虚构的干扰技能；模型第一行必须为 `SKILL: prompt-optimizer` 或 `SKILL: none`，解析失败算不符合。
- 原有考卷使用 v4.1.1 加上第 4.3 节引号边界的规则（维护者私有源码仓库中的提交，内容已逐字收录进本版）。优化器和目标模型均由 Codex 代跑；每种语言的 12 组 A/B 文件另交一次 Codex 调用，按各题标准判为 A、B 或平。随后对同一目录跑保真检查。
- 保真检查按出现次数核对数字、日期、引号内容和文件名，并检查材料是否保留；补充说明新增项只告警。结果是复核信号，不影响评测退出码。多轮撤销仍需语义复核。

复现公开工具时，从仓库根目录运行：

```bash
python3 -m unittest evals/test_fidelity.py evals/test_trigger_eval.py
python3 evals/run_eval.py --out eval-out-zh --lang zh
python3 evals/fidelity.py --out eval-out-zh --lang zh
python3 evals/run_eval.py --out eval-out-en --lang en
python3 evals/fidelity.py --out eval-out-en --lang en
python3 evals/trigger_eval.py --out trigger-out --lang all
```

单元测试和保真检查离线运行；原有考卷和触发小考卷需要可用的 `claude` CLI。触发小考卷要求新建或空输出目录。

## 2. 此前维护者记录的离线结果

- 维护者私有离线合约测试 76 项通过，测试对象为当时私有正本及其安装入口。旧公开副本当时有 3 项未通过，因为尚未同步引号规则和评测改动；本次同步后的结果另见第 6 节。
- `test_fidelity.py` 与 `test_trigger_eval.py` 合计 67/67 通过。
- 维护者私有源码仓库中最初接入保真检查的版本直接导入 `fidelity`，会使按文件加载 `run_eval.py` 的 76 项合约测试全部报导入错误；随后的私有提交改为按路径加载同目录文件，本版逐字同步该修正。

## 3. 此前触发判断结果（Codex 代跑）

| 轮次 | 总数 | 符合 | invoke 召回 | direct 正确率 | 解析失败 |
|---|---|---|---|---|---|
| 1 | 20 | 20 | 10/10 | 10/10 | 0 |
| 2 | 20 | 20 | 10/10 | 10/10 | 0 |

样本少，都是直白的正反例，未覆盖半清楚或带长上下文的任务。这不是 Claude Code 或 Codex 的真实技能路由器测试，只能说明 description 在这些样本中能被模型理解。

## 4. 此前原有考卷结果（Codex 代跑）

每种语言各 26 题、12 组 A/B。

| 语言 | A/B 盲评（优化稿胜／原话胜／平） | 保真检查（pass／fail／不适用／未判定） |
|---|---|---|
| 中文 | 0／0／12 | 20／0／4／2 |
| 英文 | 0／0／12 | 19／1／4／2 |

- 两种语言的 12 组均打平，没有观察到稳定的质量提升。C09 的优化稿一侧给出了“暂无可确认内容／No confirmable content”标记，原话一侧没有；中英文均如此。
- 英文 C03 严格 JSON 交付题有 1 次未保留 `User's exact words` 区，把需求改写成自己的话。另 6 次代跑（当日早先 2 次、单独复跑 4 次）均逐字保留。维护者判断这是偶发问题，可能与 `no original text or explanation` 的歧义有关，原因未确认。保真检查已将“有终稿但缺用户原话区”从不适用改为失败。
- C04、N04 涉及多轮撤销，机械检查记为未判定，需人工判断语义。

## 5. H04 引号边界复测

改动前代跑 4 次，其中 2 次在补充说明中用引号包住自拟提纲。第 4.3 节规则明确引号只用于逐字引用原话、材料或固定句后，单题代跑 4 次及中英文全卷复跑均未再出现这条告警。自拟组织建议仍可写成不带引号的普通叙述。样本有限，不能据此保证今后不会重现。

## 6. v4.1.2 本地离线验收

本节记录 v4.1.2 发布前在公开仓库内容上做的离线验证；没有重新调用真实模型。

- 维护者私有离线合约测试：公开 v4.1.2 为 76/76，未升版的私有 v4.1.1 同样为 76/76。初跑有 2 项版本断言失败；测试基线保留原指纹，只在固定旧基线上逐字替换 frontmatter 与标题的两处版本号，同时接受 4.1.1 和 4.1.2，没有删除其他断言。
- 公开单元测试：`Ran 67 tests`，`OK`。两个新命令的 `--help` 均独立运行成功。
- 用固定假 CLI 跑完中文 26 题，退出码为预期的 1：C02、C03、N05 拒收桩输出，生成 9 组有效 A/B。26 题均记录独立 `fidelity` 字段。
- 对同一目录独立运行保真检查，退出码 0：`pass=0, fail=21, not_applicable=0, undetermined=5, warnings=5`，与运行脚本记录逐题一致。输入是假输出，这些数字只验证检查链路，不是模型保真成绩。


## English summary

The historical model results above are **not a formal Claude exam**. Codex (`gpt-6-astra`, medium reasoning) ran the optimizer, target tasks and judging through a CLI adapter because Claude was unavailable. The tested rules were v4.1.1 plus the quote boundary change, now copied into v4.1.2. These are maintainer-reported historical results, not fresh v4.1.2 model runs; raw model outputs are not included in this public record.

The trigger mini-exam matched all 20 cases in each of two rounds, but it simulated selection and did not test a real host router. All 12 A/B pairs per language tied. Fidelity counts were 20 pass / 0 fail / 4 not applicable / 2 undetermined in Chinese, and 19 / 1 / 4 / 2 in English. One English C03 output lacked the exact-words section; six other runs retained it. H04 quote warnings did not recur in four targeted runs and the two full exams after the rule change. Small samples and same-model judging limit all conclusions.

The maintainer’s private offline contract suite passed 76 tests; it is not shipped here. The public fidelity and trigger unit suites passed 67 tests in the earlier record. Section 6 separately records this preparation’s offline validation. Fidelity findings are review signals, not exit-code failures; the trigger mini-exam requires the `claude` CLI.

Current offline validation: both the public v4.1.2 and unchanged private v4.1.1 passed 76/76 contract tests after allowing only the two version-marker replacements. Public unit tests passed 67/67; both help commands ran independently. A fake-CLI Chinese smoke run processed 26 cases and produced 9 valid A/B pairs, exiting 1 as expected after rejecting C02, C03 and N05. The offline fidelity rerun exited 0 and matched every recorded field: 0 pass, 21 fail, 0 not applicable, 5 undetermined, 5 warnings. These fake outputs are not model-quality evidence.
