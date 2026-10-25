# E02：第一轮coherence约束选层

## 做了什么

对evil使用完整重提向量，扫描16层×α={0.1,0.25,0.5,1}。开发集5题×4次，共1300条；分别要求平均coherence≥80和≥75，再最大化正向配对trait增量。两个设置冻结后在10道固定测试题×4次验证，共120条（含共享基线）。

## 结果

| 开发集coherence门槛 | 选中层 / α | 开发集coherence | 测试集trait | 测试集coherence |
|---:|---|---:|---:|---:|
| 80 | 18 / 0.25 | 80.90 | 3.21 | 79.17 |
| 75 | 12 / 0.5 | 76.60 | 11.46 | 77.15 |

测试集无干预trait为0，coherence为89.45。

## 结论

第19层不是唯一应考察的位置。第12层/α=0.5得到较好的效果/连贯性权衡，但没有达到80；开发集达到80的设置在测试集降到79.18，显示小开发集的选择不稳定。后续增加系数网格，而不是只围绕第19层继续调参。

## 对应Drive归档

| 实验 / run ID | Drive文件ID | 下载 |
|---|---|---|
| `eval-evil-coherent-layers-20261023-145208` | `1x9KIJJjHao-HB1ap3xlQWsU0CnjxgrOe` | [ZIP](https://drive.google.com/file/d/1x9KIJJjHao-HB1ap3xlQWsU0CnjxgrOe/view?usp=drivesdk) |

## 归档内看哪些文件

- `config.json`：固定网格和题目划分。
- `development-summary.json`、`selection.json`、`heldout-summary.json`和`layer-curves.csv`：选层依据与验证。

[返回实验索引](README.md)
