# Steering与采样：当前研究思路

## 要回答的问题

Persona steering的coherence退化，是否部分依赖解码策略？改变采样后，在**相近trait强度**下能否得到更好的trait–coherence权衡，而不只是减弱steering效果？

## 目前支持什么

- 同模型、向量、层和系数下，改变采样配置能明显改变coherence；Qwen3.5的不同层和trait表现也不同。[模型/层对照证据与限制](studies/model-layer-transfer.md)
- Qwen2.5的参数拆分中，主要coherence改善随top_k=20出现。单独1.05重复惩罚减少机械重复，却没有恢复平均连贯性；不能把这一归因直接推广到Qwen3.5。[拆分实验](studies/sampler-ablation.md#evidence-13)
- 相同保存前缀上的KV-cache重放显示，steering提高分布熵、降低前20名累计概率；自由生成路径之间的差异更大，与后续上下文放大的解释相容。[token分布诊断](studies/token-distribution.md#evidence-16)

## 假设与未排除的解释

工作假设是：steering让部分位置的概率分布更分散，尾部采样机会增加；进入某些生成路径后，上下文进一步放大偏移，top-k可以截断一部分路径。

这不是已证明的语义触发机制。尾部token不等于错误token，也未人工标注首个跑偏点。替代解释包括：采样只是压低trait、基线同样受益、题目与seed数量有限、向量混入风格特征，以及judge口径差异。模型和向量范数的混杂也未消除。

## 已设计的判别实验

[新题验证](studies/independent-validation.md#evidence-17)固定重复惩罚，只比较top-k0/20；开发集选接近相同trait目标的系数，确认集比较coherence，并报告各自基线的收益。若确认集trait没有匹配，不能强称为等强度比较。实际完成情况和结果查记录及对应run，此文不预先假定结论。

若独立题目上仍稳定改善权衡，再考虑逐token触发点与分支干预；当前均值证据尚不足以证明新颖性或独立论文贡献。Gaming的altruism实验是另一条跨任务验证线，不把它自动视为这一机制假设的确认实验。


## 本研究线的稳定实验记录

- [Qwen2.5模型对照与向量提取](studies/model-control.md)（`sd-model-control`）
- [Qwen2.5采样配置与因素拆分](studies/sampler-ablation.md)（`sd-sampler-ablation`）
- [Qwen3.5的采样迁移、注入位置与候选层](studies/model-layer-transfer.md)（`sd-model-layer-transfer`）
- [Steering后的token分布机制诊断](studies/token-distribution.md)（`sd-distribution`）
- [新题目上的相近trait强度验证](studies/independent-validation.md)（`sd-confirmation`）

历史批次汇总保留如下，后续结论在上方维护；不再新建日期式总结文件。

<a id="batch-20261028"></a>

## 2026-10-28批次的证据归属

原记录11–14共1320条回答及评分，已完成。参数组合/拆分的完整表格归入[sampler-ablation](studies/sampler-ablation.md)，Qwen3.5各层和注入位置结果归入[model-layer-transfer](studies/model-layer-transfer.md)。高层解释在本页维护，不另开逐批总结或重复复制数值表。

各run配置、评分计数、局限与确认实验的关系，以对应study为准；已反复使用的测试题不视为独立确认集。
