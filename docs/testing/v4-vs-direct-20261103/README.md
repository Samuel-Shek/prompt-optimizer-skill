# 4.0.0 与直接提问的固定对照（2026-11-03）

方法与结论见 [docs/TESTING.md](../../TESTING.md) 第 6 节。

- `PROTOCOL.json`：运行前冻结的协议（模型、轮次、调用上限、原话侧规则、评分与推广门槛、停止条件）。`source_skill` 是被测 4.0.0 `SKILL.md` 的 SHA-256。
- `JUDGE-RUBRIC.json`：匿名 A/B 评分标准与输出格式。
- `cases.json`：冻结的 12 道虚构题（`raw` 为原话侧输入，`optimizer_input` 为优化器输入，`criteria` 为判据，`strict` 为严格格式要求）。公开时只删除了指向本机证据文件的 `reuse` 字段。
- `RESULTS.csv`：GPT 链路逐题结果（有效配对、胜/平/负、歧义或缺失、硬通过数、保真失败、是否稳定胜出）。

原始调用记录、匿名评分原文和运行脚本含本机环境信息，没有公开。
