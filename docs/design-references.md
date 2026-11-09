# 设计参考

这份说明原先放在 README 里，2026-10-22 起移到这里，内容没有改动。

优化器在 v3.3 之后，对公开的提示词优化资料做过一次集中阅读和比较，包括 LangMem、Prompt Optimizer（linshenkx）、OpenAI 公开的文本元提示词与 Cookbook 评估示例、LangGPT、Rosetta、Anthropic 与 AWS 的元提示词、Lyra、Hugging Face 上两个公开项目。这些资料只作设计参考，本仓库的指令均为自行撰写，没有收入它们的原文；各来源的许可证请以原项目为准。

比较后吸收得很少：

- 采纳“只在有失败证据时才改、做最小改动”的思路（来自 LangMem）。做法是用考卷找出失败，再只加对应的句子，没有另做一个修订模式。
- 采纳“先有考卷和基线分数，再改提示词”的做法（DSPy、Anthropic 与 OpenAI 的评估工具都是这个方向）。
- 没有吸收：固定角色外壳、固定欢迎语和选模式、每次固定追问几个问题、固定输出多种变体。这些与“按任务选结构”冲突。

`references/methods.md` 里的四种按需方法，借鉴自数字生命卡兹克分享的常用提示词，出处写在该文件内。

v3.4.0 发布时尚未做这些来源的逐项对比。历史 v3.5.0-beta.1 测试版只比较了两个指定公开模板，并非它们的完整产品；结果和局限见[测试说明](https://github.com/Samuel-Shek/prompt-optimizer/blob/v3.5.0-beta.1/docs/v3.5-beta-evaluation.md)。

