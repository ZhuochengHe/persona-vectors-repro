# 实验记录索引

这里用中文按实验记录做了什么、结果和结论；代码文件导航见[英文README](../README.md)。本目录不保存原始回答或大型日志，它们在Drive的ZIP归档中。

编号说明：`E01/E02/...`是论文复现工作包；完整目录名是run ID；Drive文件ID是对应ZIP在Google Drive中的文件ID，与Slurm任务ID不同。一个工作包可能有多次run；一个follow-up归档也可能同时包含E01重提和E02对照。

共同口径：Qwen3.5-4B，层号从1开始；raw vector用于steering，单位方向用于投影；Luna直接评分、不校准。拒绝/无效评分不填0。旧回答结束协议的结果与修正协议分开解释。

## 按实验阅读

| 记录 | 内容 |
|---|---|
| [E01：persona vector提取](01_E01_persona_vectors.md) | 对应归档、设置、结果及限制 |
| [E02：早期逐层steering与原文选层规则](02_E02_original_layer_sweeps.md) | 对应归档、设置、结果及限制 |
| [E06：prompt投影与后续trait的关系](03_E06_prompt_monitoring.md) | 对应归档、设置、结果及限制 |
| [E08：15份LoRA微调训练](04_E08_lora_training.md) | 对应归档、设置、结果及限制 |
| [E02诊断：小系数、向量边界和实际扰动](05_E02_vector_and_runtime_controls.md) | 对应归档、设置、结果及限制 |
| [E02：等范数随机方向对照](06_E02_random_direction_control.md) | 对应归档、设置、结果及限制 |
| [E02：第一轮coherence约束选层](07_E02_coherence_80_75.md) | 对应归档、设置、结果及限制 |
| [E02：全部prompt注入与新系数扫描](08_E02_prompt_positions_and_75_70_sweep.md) | 对应归档、设置、结果及限制 |
| [尚未完成的实验与Qwen2.5 backup](09_pending_experiments.md) | 对应归档、设置、结果及限制 |

## 全部Drive归档对应表

[Drive总文件夹](https://drive.google.com/drive/folders/1Y9fgfox6sSKq2qOig1c53hWE8oMZIZuZ) · [ZIP目录](https://drive.google.com/drive/folders/1LMtl7nUM6wGYqgC_TPtwZM3LtGmd0jf8)。原始日志在2026-10-25上传；下表完整覆盖24个ZIP，其中21个为run归档，其余是公共日志、环境指针和文档。

| run / 归档ID | 中文记录 | Drive文件ID | 下载 |
|---|---|---|---|
| `e01-evil-fresh-turn-end-20261023-122236` | [01_E01_persona_vectors.md](01_E01_persona_vectors.md) | `1VuaC8QbL6rYiKIofsRbWI10ZCz7kC2lp` | [ZIP](https://drive.google.com/file/d/1VuaC8QbL6rYiKIofsRbWI10ZCz7kC2lp/view?usp=drivesdk) |
| `e01-qwen35-4b-20261015-233532` | [01_E01_persona_vectors.md](01_E01_persona_vectors.md) | `11xpwtb7H7Yyik9aj3YDGVlqm4Swia8DU` | [ZIP](https://drive.google.com/file/d/11xpwtb7H7Yyik9aj3YDGVlqm4Swia8DU/view?usp=drivesdk) |
| `e02-evil-small-alpha-20261023-101344` | [05_E02_vector_and_runtime_controls.md](05_E02_vector_and_runtime_controls.md) | `1UItEBgN1sDwppFdLq8GZBG-gVISGLqfL` | [ZIP](https://drive.google.com/file/d/1UItEBgN1sDwppFdLq8GZBG-gVISGLqfL/view?usp=drivesdk) |
| `e02-qwen35-4b-20261017-213718` | [02_E02_original_layer_sweeps.md](02_E02_original_layer_sweeps.md) | `1sur7x5EbWq56m1FC59yjZrD-sod2or40` | [ZIP](https://drive.google.com/file/d/1sur7x5EbWq56m1FC59yjZrD-sod2or40/view?usp=drivesdk) |
| `e02-qwen35-4b-judge-resume-20261021-151102` | [02_E02_original_layer_sweeps.md](02_E02_original_layer_sweeps.md) | `1YQ-kUmTn2nbBqPvOVhxsrxCz_rOXyQuo` | [ZIP](https://drive.google.com/file/d/1YQ-kUmTn2nbBqPvOVhxsrxCz_rOXyQuo/view?usp=drivesdk) |
| `e02-qwen35-4b-paper-20261020-203141` | [02_E02_original_layer_sweeps.md](02_E02_original_layer_sweeps.md) | `1HeTHB3GgwIgOmQnMmFC_ABhLUEwhjm5v` | [ZIP](https://drive.google.com/file/d/1HeTHB3GgwIgOmQnMmFC_ABhLUEwhjm5v/view?usp=drivesdk) |
| `e02-qwen35-4b-paper-resume-20261021-101407` | [02_E02_original_layer_sweeps.md](02_E02_original_layer_sweeps.md) | `1iwdqgD5wnEFtR3RH9rtTYPn4DYxr9ucj` | [ZIP](https://drive.google.com/file/d/1iwdqgD5wnEFtR3RH9rtTYPn4DYxr9ucj/view?usp=drivesdk) |
| `e06-qwen35-4b-20261017-214752` | [03_E06_prompt_monitoring.md](03_E06_prompt_monitoring.md) | `1LWO65hgks1w4Tj5GuEHb2ug4fUrNLZS8` | [ZIP](https://drive.google.com/file/d/1LWO65hgks1w4Tj5GuEHb2ug4fUrNLZS8/view?usp=drivesdk) |
| `e06-qwen35-4b-judge-resume-20261021-151102` | [03_E06_prompt_monitoring.md](03_E06_prompt_monitoring.md) | `1jbnDJpdZV88JNqto6IW4APn050pNnAhj` | [ZIP](https://drive.google.com/file/d/1jbnDJpdZV88JNqto6IW4APn050pNnAhj/view?usp=drivesdk) |
| `e06-qwen35-4b-paper-20261020-203500` | [03_E06_prompt_monitoring.md](03_E06_prompt_monitoring.md) | `13OHsI0GyEwp2CJ-ZFsm62i_31niWd2XT` | [ZIP](https://drive.google.com/file/d/13OHsI0GyEwp2CJ-ZFsm62i_31niWd2XT/view?usp=drivesdk) |
| `e06-qwen35-4b-paper-resume-20261021-101445` | [03_E06_prompt_monitoring.md](03_E06_prompt_monitoring.md) | `12uM9-rU7PjOsLRvabRLxoQI3ackV0lce` | [ZIP](https://drive.google.com/file/d/12uM9-rU7PjOsLRvabRLxoQI3ackV0lce/view?usp=drivesdk) |
| `e08-qwen35-4b-evil-ii-20261021-104840` | [04_E08_lora_training.md](04_E08_lora_training.md) | `1DaheB6xipzY8-p-ANJtlmLlQ5dm5TqEX` | [ZIP](https://drive.google.com/file/d/1DaheB6xipzY8-p-ANJtlmLlQ5dm5TqEX/view?usp=drivesdk) |
| `e08-qwen35-4b-matrix-20261021-121144` | [04_E08_lora_training.md](04_E08_lora_training.md) | `1JemTpte6bElAHhShc_3t8xongltithEb` | [ZIP](https://drive.google.com/file/d/1JemTpte6bElAHhShc_3t8xongltithEb/view?usp=drivesdk) |
| `e08-training-preflight-20261021-103942` | [04_E08_lora_training.md](04_E08_lora_training.md) | `18vwbdiYFPeofIDmeoejZ6F8R95x9zZTT` | [ZIP](https://drive.google.com/file/d/18vwbdiYFPeofIDmeoejZ6F8R95x9zZTT/view?usp=drivesdk) |
| `eval-evil-coherent-layers-20261023-145208` | [07_E02_coherence_80_75.md](07_E02_coherence_80_75.md) | `1x9KIJJjHao-HB1ap3xlQWsU0CnjxgrOe` | [ZIP](https://drive.google.com/file/d/1x9KIJJjHao-HB1ap3xlQWsU0CnjxgrOe/view?usp=drivesdk) |
| `eval-evil-random-control-20261023-144307` | [06_E02_random_direction_control.md](06_E02_random_direction_control.md) | `1-UAyz24DXqWA7sYwsRrUizZkCrodRs96` | [ZIP](https://drive.google.com/file/d/1-UAyz24DXqWA7sYwsRrUizZkCrodRs96/view?usp=drivesdk) |
| `evil-vector-boundary-20261023-121712` | [05_E02_vector_and_runtime_controls.md](05_E02_vector_and_runtime_controls.md) | `17BYDH0NRSKy74DBNYcyZM6pXrSubZbXe` | [ZIP](https://drive.google.com/file/d/17BYDH0NRSKy74DBNYcyZM6pXrSubZbXe/view?usp=drivesdk) |
| `perturbation-norm-20261023-141237` | [05_E02_vector_and_runtime_controls.md](05_E02_vector_and_runtime_controls.md) | `1ki2k7ofakvVFdTu9TYelgyTVPCzMjH0s` | [ZIP](https://drive.google.com/file/d/1ki2k7ofakvVFdTu9TYelgyTVPCzMjH0s/view?usp=drivesdk) |
| `project-documentation` | [09_pending_experiments.md](09_pending_experiments.md) | `1ZVdcLkE0qIXoy4LH4fLfsvaEncNCu3d_` | [ZIP](https://drive.google.com/file/d/1ZVdcLkE0qIXoy4LH4fLfsvaEncNCu3d_/view?usp=drivesdk) |
| `runtime-interactions-20261023-114603` | [05_E02_vector_and_runtime_controls.md](05_E02_vector_and_runtime_controls.md) | `1hJ3-XOiPqc9k9In3dTh4GnPeEqHA_r86` | [ZIP](https://drive.google.com/file/d/1hJ3-XOiPqc9k9In3dTh4GnPeEqHA_r86/view?usp=drivesdk) |
| `runtime-interactions-20261023-115342` | [05_E02_vector_and_runtime_controls.md](05_E02_vector_and_runtime_controls.md) | `1a0_G6VnEslX3mVrmbkmGzLg-jY-IAr6V` | [ZIP](https://drive.google.com/file/d/1a0_G6VnEslX3mVrmbkmGzLg-jY-IAr6V/view?usp=drivesdk) |
| `slurm-stdout-stderr` | [公共日志 / 环境](README.md) | `1TJh8w0Zl0WS8G1EP9AWKY7ToVblzIA9w` | [ZIP](https://drive.google.com/file/d/1TJh8w0Zl0WS8G1EP9AWKY7ToVblzIA9w/view?usp=drivesdk) |
| `steering-followups-20261024-193631` | [08_E02_prompt_positions_and_75_70_sweep.md](08_E02_prompt_positions_and_75_70_sweep.md) | `1XxaumScxQhuFr620R3jG2zwN9o3-ASJc` | [ZIP](https://drive.google.com/file/d/1XxaumScxQhuFr620R3jG2zwN9o3-ASJc/view?usp=drivesdk) |
| `workspace-run-pointers-and-environment` | [公共日志 / 环境](README.md) | `1EeMv8WKnlGBsif3TopGNbSh6bdGQGRpq` | [ZIP](https://drive.google.com/file/d/1EeMv8WKnlGBsif3TopGNbSh6bdGQGRpq/view?usp=drivesdk) |

归档内路径相对于解压后的ZIP根目录。`files-manifest.csv`和`SHA256SUMS`在Drive总文件夹，分别校验单文件和ZIP。模型/adapter权重不在Drive归档中。历史失败或恢复run保留用于对应来源，后续有效结果以各记录明确标出的汇总为准。
