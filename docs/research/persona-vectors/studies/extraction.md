# E01：persona vector提取

研究ID：`pv-extraction`。返回[研究线](../overview.md)／[总入口](../../index.md)。

这是一份持续维护的研究记录：同一问题的重跑、模型/系数补测和恢复任务写入本文件，不再递增编号创建文档。以下保留原设置、结果、限制和归档对应关系；历史状态只代表当时，当前状态必须核对具体run。

证据章节：[1](#evidence-01)。run与Drive总表见[统一登记表](../../run_registry.json)。

<a id="evidence-01"></a>

## E01：persona vector提取

### 做了什么

在Qwen3.5-4B上，对evil、sycophantic、hallucinating各选10道原始提取题、3组正负指令，每个条件3次rollout。每trait生成180条回答，由Luna按原rubric评分，不校准。只保留正向trait≥50、负向trait<50且正负coherence均≥50的配对。

对每条回答的response token activation取均值，再作正负均值差；每层保存一个raw vector。层号从1开始，取完整block输出；steering使用raw vector，投影使用单位方向。

### 结果

| 提取批次 | evil有效配对 | sycophantic有效配对 | hallucinating有效配对 |
|---|---:|---:|---:|
| 最初提取 | 25 | 87 | 26 |
| 修正回答结束协议后完整重提 | 24 | 87 | 尚未完整重提 |

重提evil位于独立run；重提sycophantic位于最新follow-up归档的`extraction/`及`vectors/`。两者都沿用180条的缩小规模。

### 结论

三种trait都得到非零方向，但有效配对数差异很大。evil与sycophantic的后续效果差异不能只归因于模型防护：24对与87对的提取样本量也是混杂因素。hallucinating旧向量尚不能当作修正协议下完整重跑的结果。向量能否稳定控制行为需要E02验证。

### 对应Drive归档

| 实验 / run ID | Drive文件ID | 下载 |
|---|---|---|
| `e01-qwen35-4b-20261015-233532` | `11xpwtb7H7Yyik9aj3YDGVlqm4Swia8DU` | [ZIP](https://drive.google.com/file/d/11xpwtb7H7Yyik9aj3YDGVlqm4Swia8DU/view?usp=drivesdk) |
| `e01-evil-fresh-turn-end-20261023-122236` | `1VuaC8QbL6rYiKIofsRbWI10ZCz7kC2lp` | [ZIP](https://drive.google.com/file/d/1VuaC8QbL6rYiKIofsRbWI10ZCz7kC2lp/view?usp=drivesdk) |
| `steering-followups-20261024-193631` | `1XxaumScxQhuFr620R3jG2zwN9o3-ASJc` | [ZIP](https://drive.google.com/file/d/1XxaumScxQhuFr620R3jG2zwN9o3-ASJc/view?usp=drivesdk) |

### 归档内看哪些文件

- `e01-*`归档：`config.json`、`tasks/`、`responses/`、`scored/`、`vectors/<trait>.json`和`.pt`。
- follow-up归档：`extraction-config.json`、`extraction/scored.jsonl`、`vectors/sycophantic.json`和`.pt`。

[返回实验索引](../../index.md)
