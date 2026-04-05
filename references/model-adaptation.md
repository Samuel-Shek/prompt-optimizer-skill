# 模型适配参考

本文件用于补充不同模型的提示词改写偏好。只有在用户明确指定模型，或任务对输出结构很敏感时再读取。

## Claude

适合：

- system prompt
- agent 行为规范
- 长上下文任务
- 需要明确边界与角色的任务

改写要点：

- 用清晰的层级或 XML 标签
- 强调 role / constraints / output format
- 适合写成“规则块 + 任务块 + 输出块”

推荐骨架：

```xml
<role>...</role>
<goal>...</goal>
<context>...</context>
<rules>
- ...
</rules>
<output_format>...</output_format>
```

## GPT

适合：

- 通用任务
- 需要结构化输出的任务
- 需要 JSON / 表格 /字段约束的任务

改写要点：

- 用 Markdown 分节
- 有格式约束时写清字段定义
- 需要稳定产出时补 schema 或示例

## Gemini

适合：

- 需要过程清晰的任务
- 需要阶段化产出的任务

改写要点：

- 用 PTCF 思路组织：Purpose / Task / Constraints / Format
- 把目标和格式要求写得非常直白

## DeepSeek

适合：

- 快速执行
- 说明简单直接的任务

改写要点：

- 去掉冗余包装
- 少层级
- 直接说明目标、要求、输出

## 开源模型

适合：

- 上下文短
- 依赖模板或 few-shot 的任务

改写要点：

- 句子短
- 结构简单
- 多示例，少抽象

## 通用判断规则

如果不确定目标模型：

- 默认按 GPT 风格生成
- 需要强约束时偏 GPT
- 需要强角色和边界时偏 Claude
