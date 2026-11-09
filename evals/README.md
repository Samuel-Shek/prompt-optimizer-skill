# 考卷（evals）

这是 prompt-optimizer 的维护用考卷。它不被 `SKILL.md` 引用，不会注入任何生成的提示词。

## 内容

- `cases.json`：26 道中文虚构题（材料均为虚构，不含真实客户或私人信息）。
  - `main` 组 12 题（C01–C12）：日常基线与改进对比；
  - `holdout` 组 4 题（H01–H04）：原意是不拿来调规则；H04 已参与调规则，H01–H03 没有效果题，所以不能当作独立效果证据；
  - `dev` 组 10 题（N01–N10）：已知问题的回归题，每题对应一次具体修改。
- `cases.en.json`：英文版 v3.5.3 用的 16 道题，与 v3.5.x 中文题同编号、同考点。
- `run_eval.py`：中文版（v4.0.4）用的评测脚本，需要 Claude 命令行（`claude`）。
- `run_eval_v3.py`：v3.5.x 时期的双语脚本，英文版用 `--lang en` 跑 `cases.en.json`；它没有 4.0.1 之后的修正。

每题怎么出、怎么判，脚本流程、机械检查和盲评设计，详见 [docs/TESTING.md](../docs/TESTING.md)。

每道题有 `opt_checks`（优化器自身是否按规则交付：保留精确字符串、事实状态、不执行夹带指令、只审阅不改写等）；有 `effect` 的题另有效果对比，同一目标模型分别执行“原话”和“优化后提示词”。

## 怎么跑

```bash
python3 evals/run_eval.py --out ./eval-out --opt-model opus --target-model sonnet
```

英文版（v3.5.3）用旧版双语脚本：

```bash
python3 evals/run_eval_v3.py --lang en --out ./eval-out-en --opt-model opus --target-model sonnet
```

English: the English edition (v3.5.3) is tested with `run_eval_v3.py --lang en` and `cases.en.json`; `run_eval.py` tests the Chinese edition only.

`run_eval.py` 常用参数：`--ids C01,C02` 只跑指定题；`--rounds 2` 目标任务每侧跑两轮（优化稿仍只生成一次）；`--skill 路径` 测试另一版 `SKILL.md`；`--effect-mode system-deployment` 让声明了部署角色的题（C09）两侧同为 system，单独报告；`--resume` 只在源文件哈希与配置都一致时复用已校验的成功输出。输出目录须为空或用 `--resume`。

脚本只记录输出和少量机械检查，并生成随机顺序的 A/B 盲评文件。**效果好坏由人（或另一个读取保存文件的评审）判断，脚本不打分。** 也可以不用脚本，把 `cases.json` 里的 `optimizer_input` 手动交给任何模型。

## 已有结果

2026-10-13 至 10-14，用本考卷对 v3.3、v3.4 各做过测试（均为虚构材料）：

**v3.3 首轮（Claude Opus 当优化器，Sonnet 当执行模型）**

- 优化器自身检查：16 题通过 11、部分通过 4、不通过 1。扣分主要是“加料”：多加交付物、默认值和非必要的待填空位。
- 7 道效果题，每题 2 轮：优化后更好 2、略好 1、没区别或没带来好处 2、各有优劣 2。
- 优化后的提示词中位数约为原话的 9 倍长。

**同一考卷，GPT 侧独立复核 v3.3（gpt-6.1-sol 负责优化与执行）**

- 优化器自身检查：57 项全部通过。
- 14 组目标任务比较：优化后更好 4、原话更好 1、差不多 9。优化后的提示词中位数约为原话的 4.5 倍长。
- 周报题（C09）两边都出现真退步：优化后的提示词把“没有证据的不要写”改得更严，执行时漏写了有据的进展。这直接促成了 v3.4 的第一句。

**v3.4 复测**：见 [VALIDATION.md](../VALIDATION.md) 中 v3.4.0 一节的“复测摘要”（原在根目录 README，2026-10-22 移入）。

## 局限

- 评判主要由 Claude 完成，与被测模型同属一家；GPT 侧独立复核只覆盖 v3.3。
- 每个条件只有 1 到 10 次运行，只能看趋势，不能得出统计显著性。
- 第 2 轮不是盲评。
- 只有 C09 周报和 H04 公众号两题用最终文字完整跑过 v3.4 的执行效果，其余题的执行效果沿用前两稿数据。
- 没有与其他提示词优化产品做过对跑。
- 简单任务（翻译、短消息）没有稳定收益；格式严格、有硬性限制的任务更可能有帮助。
