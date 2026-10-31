# 新题目上的相近trait强度验证

研究ID：`sd-confirmation`。返回[研究线](../overview.md)／[总入口](../../index.md)。

这是一份持续维护的研究记录：同一问题的重跑、模型/系数补测和恢复任务写入本文件，不再递增编号创建文档。以下保留原设置、结果、限制和归档对应关系；历史状态只代表当时，当前状态必须核对具体run。

证据章节：[1](#evidence-17)。run与Drive总表见[统一登记表](../../run_registry.json)。

<a id="evidence-17"></a>

## 采样验证：新题目上的trait–coherence权衡

### 问题与冻结设置

2026-10-30，测试top-k收益是否在相近trait强度下仍存在，而不只是压低trait换连贯性。本轮仅Qwen2.5-7B-Instruct、evil、L20 response，复用原62对提取的raw向量，不重新提取。固定模型revision、SDPA、temperature=1、top_p=1、repetition_penalty=1.0、max_new_tokens=1000。top_k={0,20}，α={0,0.75,1,1.25,1.5,1.75}，包括两种采样各自α=0基线，所有条件统一Transformers。

原20道eval题此前均已涉及，不能再称独立确认题。本轮新编20题，在生成前冻结，开发10题、确认10题，每题4次，共960条新回答。逐字排除与原extract/eval题重合；仍属于同一宽泛伦理问题分布，不是第三方独立benchmark，也不能保证主题完全独立。资产：`assets/sampling_validation_questions.json`。sample ID跨top-k与α保持一致、同seed配对。

### 分析规则（先于结果固定）

报告全部dev/test trait–coherence曲线、重复率、截断、非数值评分计数。在开发集分别为两种top-k选择最接近trait目标10、25、50、75的α；要求≥30/40数值trait，距目标≤10，平局选更小α。仅开发集选参数，写入`matched-trait-selection.json`后分析对应确认集回答。无合格参数时标注网格不支持，不外推、不看确认集重新选α。

确认集报告配对coherence差、按问题bootstrap的95%区间（2000次、seed20261030）及共同数值样本上的trait均值；确认集两条件trait差≤10且数值样本≥30才标作相近trait，其余保留但不当成等强度证据。另报告top-k基线本身的coherence差，并列出减去基线收益后的差值，区分通用采样收益与steering额外收益。10道确认题和多个目标决定了结果仍属小规模探索，不作正式显著性宣传。

### run与Drive对应

run ID：`eval-qwen25-sampling-confirmation-20261030-133457`；目录`${PV_WORK}/runs/eval-qwen25-sampling-confirmation-20261030-133457/`。Drive文件ID尚未分配。冻结代码、配置、题目、向量均记录SHA256；原始回答、评分、指标全部保留。

### 结果

<!-- sampling-results:start -->
全部生成与评分完成。以下为各条件数值评分均值；非数值trait评分不计为零。
| 条件 | trait | coherence | trait数值条数 | 重复率 | 截断 |
|---|---:|---:|---:|---:|---:|
| development-k0-a0 | 0.00 | 94.60 | 40 | 1.7% | 0/40 |
| development-k0-a0p75 | 0.90 | 89.22 | 40 | 1.5% | 1/40 |
| development-k0-a1 | 9.32 | 77.92 | 40 | 1.8% | 0/40 |
| development-k0-a1p25 | 73.78 | 26.35 | 40 | 3.2% | 9/40 |
| development-k0-a1p5 | 97.58 | 12.72 | 40 | 1.3% | 21/40 |
| development-k0-a1p75 | 99.03 | 9.62 | 40 | 2.6% | 19/40 |
| development-k20-a0 | 0.00 | 95.45 | 40 | 1.9% | 0/40 |
| development-k20-a0p75 | 0.03 | 93.30 | 40 | 1.6% | 0/40 |
| development-k20-a1 | 3.38 | 88.83 | 40 | 1.8% | 0/40 |
| development-k20-a1p25 | 35.02 | 69.60 | 40 | 1.6% | 1/40 |
| development-k20-a1p5 | 88.47 | 36.00 | 40 | 1.5% | 5/40 |
| development-k20-a1p75 | 97.90 | 24.25 | 40 | 3.2% | 15/40 |
| confirmation-k0-a0 | 0.00 | 91.92 | 40 | 2.4% | 0/40 |
| confirmation-k0-a0p75 | 0.72 | 83.33 | 40 | 1.7% | 0/40 |
| confirmation-k0-a1 | 16.00 | 65.17 | 40 | 1.4% | 1/40 |
| confirmation-k0-a1p25 | 72.70 | 28.05 | 40 | 1.4% | 7/40 |
| confirmation-k0-a1p5 | 96.42 | 12.55 | 40 | 1.6% | 18/40 |
| confirmation-k0-a1p75 | 98.15 | 7.75 | 40 | 2.0% | 25/40 |
| confirmation-k20-a0 | 0.00 | 93.05 | 40 | 2.2% | 0/40 |
| confirmation-k20-a0p75 | 0.10 | 91.15 | 40 | 1.8% | 0/40 |
| confirmation-k20-a1 | 2.80 | 84.70 | 40 | 1.6% | 0/40 |
| confirmation-k20-a1p25 | 42.62 | 63.10 | 40 | 1.8% | 3/40 |
| confirmation-k20-a1p5 | 78.55 | 38.98 | 40 | 1.6% | 6/40 |
| confirmation-k20-a1p75 | 96.25 | 29.05 | 40 | 4.4% | 13/40 |
<!-- sampling-results:end -->

开发集选择：`matched-trait-selection.json`；固定确认比较：`matched-trait-confirmation.json`。原始逐条件汇总：`summary.json`。

### 复现

配置模板`configs/sampling-independent-validation.json`。冻结入口`source/scripts/sampling_controls.slurm generate RUN`，完成后`score RUN`；score成功后自动运行`analyze_sampling_validation.py --run RUN`。账户qdj_project_owned1/spgpu2，单L40S，60G内存。实验未更改原始已完成run。

Slurm任务：{"generate": "65083550", "score": "65083551"}。
