# 实验索引

按实验拆分的中文记录、run ID和Drive文件ID见[experiment_records/README.md](../experiment_records/README.md)。本文件保留状态总览和历史提交记录。

2026-10-24 steering后续实验已全部完成：两trait各1300条开发集扫描及共200条固定测试集验证均评分齐全。按coherence≥75选层，sycophantic第14层/α=1.2在测试集trait由15.28升至61.30、coherence为76.73；evil第14层/α=0.4的trait为6.62、coherence为77.03。第12层all注入未改善连贯性。当前无活动任务；Qwen2.5-7B backup未启动。[设置、排名、结果及限制](experiments/2026-10-24_steering_followups.md)。

## 当前状态

| 工作包 | 状态 |
|---|---|
| E01 | 提取完成；evil与sycophantic已按修正协议完整重提 |
| E02 | 已完成多轮steering、随机方向及注入位置对照；最新结果见上方链接 |
| E06 | 原选层方案下的监测实验已完成；部分数据属于历史生成协议 |
| E08 | 15份adapter训练完成；行为与能力评估待做 |
| E09/E10/E11/E19 | 框架与策略已有，正式结果待做 |
| Qwen2.5-7B backup | 仅记录，未启动 |

## 历史提交记录

以下保留早期提交时的设置和任务ID；最新完成状态以上表及具体实验文档为准。

E08 剩余 14 份正式训练当时安排为数组 `64467682`，最多并行 3 份（各 1×L40S/60 GB），依赖数据准备及真实 Code 2048-token batch-2 反向传播检查 `64467677` 成功后启动。每份 1000 训练 + 100 开发问题组，1 epoch / 63 次更新；排除已完成的 Evil-II，全部从原始基座初始化。矩阵配置、各任务身份和数据划分位于 `${PV_WORK}/runs/e08-qwen35-4b-matrix-20261021-121144/matrix.json`，只包含训练，不含行为评估。

E08 首份正式训练已提交：Evil-II，1000 训练问题组 + 100 开发问题组，从原始 Qwen3.5-4B 基座初始化 rs-LoRA，使用已通过预检的作者参数，1 epoch / 63 次更新。Slurm `64457371`（spgpu2，1×L40S）；配置、数据、代码快照与训练产物位于 `${PV_WORK}/runs/e08-qwen35-4b-evil-ii-20261021-104840/`。只启动这一份训练，行为评估尚未启动。

E01 已完成。当前 E02 按论文 B.4 的固定 alpha 最大 trait 均分选层，连贯性只报告、不筛除。三个 alpha 为 1、1.5、2，仍使用16层、每trait5道开发题和4次rollout；旧数据复用，三个trait并行补测。Alpha=1为预先固定的主层，其他alpha各自选层并单独报告。

E06 更新任务已挂在新 E02 后：复用 sycophantic/hallucinating 的448条回答、评分和全层投影，补齐 evil 的224条，随后重算各alpha选层下的监测结果。配置、数据复用来源和任务ID保存在scratch运行目录中。

| 工作包 | 具体策略 | 依赖 | 实现入口 |
|---|---|---|---|
| E01 向量提取 | [E01](experiments/strategies/E01.md) | 基座/原资产 | inference_tasks、generate/score/vectors |
| E02 steering/选层 | [E02](experiments/strategies/E02.md) | E01 | generate的vector/layer/coefficient |
| E06 prompt监测 | [E06](experiments/strategies/E06.md) | E02 | monitor任务、project、analyze E06 |
| E08 常规微调漂移 | [E08](experiments/strategies/E08.md) | 固定训练子集 | prepare-data、train、generate/score/mmlu |
| E09 激活位移预测 | [E09](experiments/strategies/E09.md) | E02、E08 | project prompt_last、analyze E09 |
| E10 微调后steering | [E10](experiments/strategies/E10.md) | E02、E08 | adapter+推理负系数、mmlu |
| E11 preventative steering | [E11](experiments/strategies/E11.md) | E02、共享E08对照 | train的正系数全token hook |
| E19 数据投影差预测 | [E19](experiments/strategies/E19.md) | E02、E08结果用于验证 | dataset/natural任务、基座project、analyze E19 |

[运行手册](experiments/RUNBOOK.md)说明可用CLI、Slurm命令、数据路径与尚未验证的真实环境兼容性。
