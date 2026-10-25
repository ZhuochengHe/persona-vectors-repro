# E02：早期逐层steering与原文选层规则

## 做了什么

早期E02先做缩小规模扫描，随后按论文B.4重跑：固定每个α，选择开发集trait均值最高的层，coherence单独报告。α={1,1.5,2}，16个候选层；每trait5道开发题、每题4次，选定后在10道固定测试题、每题4次验证。主结果来自judge-resume归档，其他run保留最初执行与恢复来源。

默认推理在最后一个prompt位置及每步decode位置加入α×raw vector，不做L2 normalization。这是原论文公开推理入口的response模式。

## 结果（历史协议）

| trait | α | 层 | 测试集trait | 测试集coherence |
|---|---:|---:|---:|---:|
| evil | 1 | 19 | 44.12 | 19.55 |
| evil | 1.5 | 17 | 54.85 | 15.32 |
| evil | 2 | 16 | 59.44 | 14.15 |
| sycophantic | 1 | 20 | 91.25 | 36.75 |
| sycophantic | 1.5 | 19 | 98.97 | 22.30 |
| sycophantic | 2 | 20 | 97.97 | 10.82 |
| hallucinating | 1 | 24 | 99.40 | 21.75 |
| hallucinating | 1.5 | 18 | 99.95 | 3.88 |
| hallucinating | 2 | 15 | 100.00 | 3.27 |

## 结论

仅最大化trait会选出输出已经明显退化的设置，不能据高trait分数认定steering可用。α=1并不意味着小扰动，也不能跨模型直接比较。原论文B.4没有明确最终选层系数；我们将α=1设为主系数属于复现约定。

这些回答属于旧生成结束协议，部分steered回答可能在assistant-turn结束后继续生成。它们保留作历史结果和后续设计依据；当前可用层应参考[新的coherence约束扫描](08_E02_prompt_positions_and_75_70_sweep.md)。

## 对应Drive归档

| 实验 / run ID | Drive文件ID | 下载 |
|---|---|---|
| `e02-qwen35-4b-20261017-213718` | `1sur7x5EbWq56m1FC59yjZrD-sod2or40` | [ZIP](https://drive.google.com/file/d/1sur7x5EbWq56m1FC59yjZrD-sod2or40/view?usp=drivesdk) |
| `e02-qwen35-4b-paper-20261020-203141` | `1HeTHB3GgwIgOmQnMmFC_ABhLUEwhjm5v` | [ZIP](https://drive.google.com/file/d/1HeTHB3GgwIgOmQnMmFC_ABhLUEwhjm5v/view?usp=drivesdk) |
| `e02-qwen35-4b-paper-resume-20261021-101407` | `1iwdqgD5wnEFtR3RH9rtTYPn4DYxr9ucj` | [ZIP](https://drive.google.com/file/d/1iwdqgD5wnEFtR3RH9rtTYPn4DYxr9ucj/view?usp=drivesdk) |
| `e02-qwen35-4b-judge-resume-20261021-151102` | `1YQ-kUmTn2nbBqPvOVhxsrxCz_rOXyQuo` | [ZIP](https://drive.google.com/file/d/1YQ-kUmTn2nbBqPvOVhxsrxCz_rOXyQuo/view?usp=drivesdk) |

## 归档内看哪些文件

- 主结果：judge-resume归档中的`config.json`、`development-summary.json`、`selection.json`、`heldout-summary.json`、`layer-curves.csv`。
- `responses/`与`scored/`保存逐条件回答和评分；`reuse/`或manifest记录复用来源。

[返回实验索引](README.md)
