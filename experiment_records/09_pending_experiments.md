# 尚未完成的实验与Qwen2.5 backup

## 尚未完成

| 实验 | 计划回答的问题 | 当前状态 / Drive实验ID |
|---|---|---|
| E08后续评估 | 微调后的trait漂移、领域行为和MMLU变化 | adapter训练完成；行为/能力评估未完成，无独立结果归档 |
| E09 | activation位移能否预测微调后的trait变化 | 有策略及框架，未产生正式结果，无对应Drive实验文件ID |
| E10 | 微调后负向steering能否抑制trait并保留能力 | 有策略及框架，未产生正式结果，无对应Drive实验文件ID |
| E11 | preventative steering能否在训练时减少漂移 | 有策略及框架，未产生正式结果，无对应Drive实验文件ID |
| E19 | 数据投影差是否预测微调漂移 | 有策略及框架，未产生正式结果，无对应Drive实验文件ID |
| Qwen2.5-7B backup | 原模型第20层能否复现预期控制效果 | 仅记录；未下载、未提交，无对应Drive实验文件ID |

## Backup的判读

换回Qwen2.5-7B-Instruct后，需要重新提取该模型自己的向量，不能使用Qwen3.5向量。先固定第20层和当前缩小规模，再按需增加提取规模或比较同一向量在upstream与我们实现中的效果。

原模型有效会支持模型差异的重要性；增加样本后有效会支持规模影响；同一向量在upstream有效、我们的推理无效才更直接指向pipeline。单次失败不能断言只可能是pipeline或样本量问题。

## 计划文件

- [总体计划](../docs/plans/persona_vectors_reproduction.md)
- [适配分析](../docs/plans/selected_experiments_adaptation.md)
- [各实验策略](../docs/experiments/strategies/)

下方文档归档包含当时的计划快照，不代表上述实验已经执行。

## 对应Drive归档

| 实验 / run ID | Drive文件ID | 下载 |
|---|---|---|
| `project-documentation` | `1ZVdcLkE0qIXoy4LH4fLfsvaEncNCu3d_` | [ZIP](https://drive.google.com/file/d/1ZVdcLkE0qIXoy4LH4fLfsvaEncNCu3d_/view?usp=drivesdk) |

## 归档内看哪些文件

- 文档归档中的`docs/experiments/strategies/`及`docs/plans/`只提供计划依据。

[返回实验索引](README.md)
