# E02：全部prompt注入与新系数扫描

## 做了什么

先固定evil第12层，比较response与all两种注入位置，α={0.5,1,1.5}；每组10题×4次，加共享基线共280条，全部评分完成。response只改最后一个prefill位置及每步decode；all额外修改全部prompt位置，仍只改选定的单层。

随后对evil和完整重提的sycophantic，分别扫描16层×α={0.4,0.8,1.2,1.6}。每trait开发集5题×4次，共1300条。主门槛coherence≥75，补充门槛≥70；在达标设置中最大化正向配对trait增量，同时列出无约束trait增量最高的五个不同层。

选定后固定参数，在每trait10道固定测试题×4次验证。evil含两设置及共享基线共120条；sycophantic两门槛选中同一设置，去重后80条。两组生成、评分和验证均完成。

## 结果：注入位置

| α | response trait | response coherence | all trait | all coherence |
|---:|---:|---:|---:|---:|
| 0.5 | 11.46 | 77.15 | 12.66 | 73.30 |
| 1.0 | 32.18 | 47.45 | 54.02 | 44.17 |
| 1.5 | 51.44 | 20.55 | 51.25 | 17.40 |

all没有恢复连贯性。α=1时trait更高，但coherence仍低；第12层在α=1、1.5时也明显退化。

## 结果：开发集选层后的固定测试集验证

| trait / 门槛 | 层 / α | 测试集基线trait | steering trait | trait增量 | steering coherence |
|---|---|---:|---:|---:|---:|
| evil / 75 | 14 / 0.4 | 0.00 | 6.62 | +6.62 | 77.03 |
| evil / 70 | 15 / 0.4 | 0.00 | 7.97 | +7.97 | 74.83 |
| sycophantic / 75 | 14 / 1.2 | 15.28 | 61.30 | +46.02 | 76.72 |
| sycophantic / 70 | 14 / 1.2 | 15.28 | 61.30 | +46.02 | 76.72 |

## 结论

sycophantic第14层/α=1.2取得明显trait提升，同时保持coherence约76.73；早期第20层的严重退化不代表所有层。evil在本轮网格的coherence约束下提升较小。两个trait无coherence约束的高trait候选都存在严重退化，因此退化并非evil独有。

这些结果不能证明差异来自安全训练：题目、方向范数、提取样本和有效配对数均不同。开发集仅5题，evil的75门槛胜出设置在开发集配对数值评分仅覆盖15条、4题。固定测试题此前已查看，不是全新独立确认集。

本轮网格不含此前第12层/α=0.5，不能据新选择宣称第14层普遍更优。完整前五层排名及逐条件计数见归档selection.json和[详细实验文档](../docs/experiments/2026-10-24_steering_followups.md)。

## 对应Drive归档

| 实验 / run ID | Drive文件ID | 下载 |
|---|---|---|
| `steering-followups-20261024-193631` | `1XxaumScxQhuFr620R3jG2zwN9o3-ASJc` | [ZIP](https://drive.google.com/file/d/1XxaumScxQhuFr620R3jG2zwN9o3-ASJc/view?usp=drivesdk) |

## 归档内看哪些文件

- `positions/summary.json`、`positions/responses/`和`positions/scored/`：注入位置对照。
- `evil-scan/`及`sycophantic-scan/`内的`config.json`、`development-summary.json`、`selection.json`、`heldout-summary.json`。
- `vectors/sycophantic.json`及`extraction/scored.jsonl`：本轮sycophantic重提。

[返回实验索引](README.md)
