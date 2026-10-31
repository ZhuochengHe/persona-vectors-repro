# E06：prompt投影与行为监测

研究ID：`pv-monitoring`。返回[研究线](../overview.md)／[总入口](../../index.md)。

这是一份持续维护的研究记录：同一问题的重跑、模型/系数补测和恢复任务写入本文件，不再递增编号创建文档。以下保留原设置、结果、限制和归档对应关系；历史状态只代表当时，当前状态必须核对具体run。

证据章节：[1](#evidence-03)。run与Drive总表见[统一登记表](../../run_registry.json)。

<a id="evidence-03"></a>

## E06：prompt投影与后续trait的关系

### 做了什么

对每trait使用8条原始system提示、7道题、每题4次rollout，合计224条回答，三个trait共672条。用最后一个prompt token在选定层的activation，投影到该层persona单位方向，再与后续回答的trait评分关联。投影不读取未来回答。

主层沿用旧E02在α=1时选出的evil第19层、sycophantic第20层、hallucinating第24层；另外报告其他α选层下的敏感性。下表为主层结果，非数值评分保持排除，不填0。

### 结果

| trait | 主层 | 全体相关r | 条件内平均r | 去条件均值后r | 数值评分 / 总回答 |
|---|---:|---:|---:|---:|---:|
| evil | 19 | 0.729 | 0.336 | 0.155 | 196/224 |
| sycophantic | 20 | 0.857 | 0.396 | 0.595 | 224/224 |
| hallucinating | 24 | 0.523 | 0.583 | 0.456 | 223/224 |

### 结论

prompt投影与后续trait存在相关性，但整体r包含提示条件之间的差异，不能当作同一条件内稳定预测的证据。evil去除条件均值后r只有约0.155；sycophantic的条件内信号相对更强。此前提到约0.52的整体相关系数对应hallucinating。

这组实验沿用历史向量、选层及部分旧生成协议，尚未用新第14层和重提向量完整重跑。它不是因果steering实验，也不能替代E02的行为验证。

### 对应Drive归档

| 实验 / run ID | Drive文件ID | 下载 |
|---|---|---|
| `e06-qwen35-4b-20261017-214752` | `1LWO65hgks1w4Tj5GuEHb2ug4fUrNLZS8` | [ZIP](https://drive.google.com/file/d/1LWO65hgks1w4Tj5GuEHb2ug4fUrNLZS8/view?usp=drivesdk) |
| `e06-qwen35-4b-paper-20261020-203500` | `13OHsI0GyEwp2CJ-ZFsm62i_31niWd2XT` | [ZIP](https://drive.google.com/file/d/13OHsI0GyEwp2CJ-ZFsm62i_31niWd2XT/view?usp=drivesdk) |
| `e06-qwen35-4b-paper-resume-20261021-101445` | `12uM9-rU7PjOsLRvabRLxoQI3ackV0lce` | [ZIP](https://drive.google.com/file/d/12uM9-rU7PjOsLRvabRLxoQI3ackV0lce/view?usp=drivesdk) |
| `e06-qwen35-4b-judge-resume-20261021-151102` | `1jbnDJpdZV88JNqto6IW4APn050pNnAhj` | [ZIP](https://drive.google.com/file/d/1jbnDJpdZV88JNqto6IW4APn050pNnAhj/view?usp=drivesdk) |

### 归档内看哪些文件

- judge-resume归档：`summary.json`、`layer-selection.json`、`config.json`、`reuse.json`。
- 各归档中的`responses/`、`scored/`和projection相关输出保存回答、评分及全层探索结果；具体路径以manifest为准。

[返回实验索引](../../index.md)
