# E08：15份LoRA微调训练

## 做了什么

对evil、sycophancy、hallucination、insecure_code、mistake_opinions五类数据，各训练Normal/I/II三个版本。每份从原始Qwen3.5-4B重新初始化LoRA，使用1000个训练问题组和100个开发问题组；不在一个adapter上连续训练多个版本。

设置：rsLoRA rank=32、alpha=64、dropout=0；学习率1e-5、AdamW 8-bit、weight decay=0.01、linear scheduler、warmup 5步；batch=2、gradient accumulation=8、最大长度2048、BF16、1 epoch、seed=0。训练仅监督assistant response。先做真实2048-token反向传播预检，再运行首个Evil-II和其余14份。

## 结果

15/15份训练完成，每份63次optimizer更新。首个Evil-II的平均train loss约1.976，只表示训练过程中的拟合指标。

## 结论

训练管线已实际完成这15份adapter，但行为trait、MMLU和领域任务效果尚未评估。因此目前不能说微调成功诱发了persona漂移，也不能判断能力变化。后续E09/E10/E11/E19还需要行为评估或新的训练/干预。

Drive包含日志、配置、trainer指标和完成标记，不包含adapter权重；权重仍在原计算存储中。

## 对应Drive归档

| 实验 / run ID | Drive文件ID | 下载 |
|---|---|---|
| `e08-training-preflight-20261021-103942` | `18vwbdiYFPeofIDmeoejZ6F8R95x9zZTT` | [ZIP](https://drive.google.com/file/d/18vwbdiYFPeofIDmeoejZ6F8R95x9zZTT/view?usp=drivesdk) |
| `e08-qwen35-4b-evil-ii-20261021-104840` | `1DaheB6xipzY8-p-ANJtlmLlQ5dm5TqEX` | [ZIP](https://drive.google.com/file/d/1DaheB6xipzY8-p-ANJtlmLlQ5dm5TqEX/view?usp=drivesdk) |
| `e08-qwen35-4b-matrix-20261021-121144` | `1JemTpte6bElAHhShc_3t8xongltithEb` | [ZIP](https://drive.google.com/file/d/1JemTpte6bElAHhShc_3t8xongltithEb/view?usp=drivesdk) |

## 归档内看哪些文件

- 首份Evil-II归档：`config.json`、`run.json`、`done.json`。
- 矩阵归档：`matrix.json`及`adapters/<category>/<version>/done.json`、训练指标和配置。
- 预检归档：真实训练预检的日志与JSON结果。

[返回实验索引](README.md)
