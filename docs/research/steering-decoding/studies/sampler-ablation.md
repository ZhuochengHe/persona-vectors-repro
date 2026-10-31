# Qwen2.5采样配置与因素拆分

研究ID：`sd-sampler-ablation`。返回[研究线](../overview.md)／[总入口](../../index.md)。

这是一份持续维护的研究记录：同一问题的重跑、模型/系数补测和恢复任务写入本文件，不再递增编号创建文档。以下保留原设置、结果、限制和归档对应关系；历史状态只代表当时，当前状态必须核对具体run。

证据章节：[1](#evidence-11) · [2](#evidence-13)。run与Drive总表见[统一登记表](../../run_registry.json)。

<a id="evidence-11"></a>

## Qwen2.5 evil：upstream采样默认值对照

### 目的与设置

论文正文与附录没有明确指定top_k与repetition_penalty。公开repo的HF steering函数未覆盖这两个参数，当前固定模型revision的generation_config.json默认是20和1.05。本实验验证这组配置的影响，不称为完整upstream管线复现。

仅把top_k从0改为20、repetition_penalty从1.0改为1.05。复用`backup-qwen25-7b-evil-retry-20261027-150332`的evil raw向量（62对，L20范数26.7745）、相同10题×4 rollout与配对seed。固定Qwen2.5-7B-Instruct同revision、BF16、SDPA、response注入、L20，α={0,0.5,1,1.5,2}，temperature=1、top_p=1、max_new_tokens=1000。合计200条新回答；不重提向量。继续Luna原rubric直接评分，无校准。

只比较两个采样配置组合，不区分两个参数各自的贡献。全部生成参数写入每条输出，向量与冻结输入均记录SHA256。旧run保持不变。

### run与Drive对应

run ID：`steer-qwen25-evil-sampling-20261027-192009`。位置：`${PV_WORK}/runs/steer-qwen25-evil-sampling-20261027-192009/`。父run：`backup-qwen25-7b-evil-retry-20261027-150332`。Drive文件ID尚未分配，待完成归档后补充。

### 结果

<!-- qwen25-results:start -->

复用既有向量，已完成200条固定第20层评估回答的生成与评分。
有效提取配对：62对；第20层raw vector范数：26.7745。

| α | evil均值 | coherence均值 | 重复4-gram比例 | 相对扰动 |
|---:|---:|---:|---:|---:|
| 0 | 0.05 | 96.42 | 0.7% | 0.0% |
| 0.5 | 0.10 | 95.70 | 0.3% | 12.5% |
| 1 | 9.95 | 89.08 | 0.4% | 25.0% |
| 1.5 | 73.45 | 60.17 | 0.6% | 37.4% |
| 2 | 97.80 | 34.10 | 2.2% | 49.9% |

在已测系数中存在coherence≥75且trait正向提升的设置，需结合具体回答及不确定性解释。

这不是论文全量规模复现；Luna评分、提取有效样本数及运行设置仍是需要考虑的差异。

<!-- qwen25-results:end -->

### 复现

使用冻结run的`source/scripts/qwen25_backup.slurm generate-steering RUN`，完成后运行`score-steering RUN`；提交时设置PV_WORK。配置模板见`configs/qwen25-sampling-control.json`。

任务ID：{"generate-steering": "64911197", "score-steering": "64911198"}

### 与旧采样配置对比

200条生成与评分全部完成；生成45分22秒，评分10分32秒。所有评分均为数值结果。

| α | 旧evil | 新evil | 旧coherence | 新coherence |
|---:|---:|---:|---:|---:|
| 0 | 0.00 | 0.05 | 96.22 | 96.42 |
| 0.5 | 0.10 | 0.10 | 94.35 | 95.70 |
| 1 | 27.48 | 9.95 | 70.00 | 89.08 |
| 1.5 | 81.12 | 73.45 | 30.15 | 60.17 |
| 2 | 93.90 | 97.80 | 14.70 | 34.10 |

同向量、同题同seed下，改变这两个采样参数后coherence均值提高，尤其α=1从70提高到89.08，evil从27.48降至9.95（相对新基线提升9.90，按题bootstrap 95%区间[1.45,21.275]）。α=1.5仍只有60.18 coherence，α=2只有34.10，不能称为完全解决。α=2重复4-gram比例从8.21%降至2.16%，达到1000 token上限从22/40降至10/40。

这支持采样设置会实质影响本次现象，但未分离top_k与重复惩罚的各自贡献，也未替换成完整upstream生成路径或GPT-4.1-mini评分。此前关于Qwen2.5没有coherence≥75且evil明显提升设置的结论，仅适用于旧采样配置。

可考虑补α=1.1、1.2、1.3、1.4，定位trait/coherence权衡；尚未提交。

---

<a id="evidence-13"></a>

## Qwen2.5：top_k与重复惩罚拆分对照

复用记录11的同一Qwen2.5 evil向量、第20层和10题×4次rollout配对seed。补top_k=20/repetition_penalty=1.0与top_k=0/repetition_penalty=1.05，分别α=1、1.5，共160条新回答。与记录10的0/1.0、记录11的20/1.05组成四组。除这两个参数外不改模型、向量、response注入、temperature=1、top_p=1、max_new_tokens=1000或Luna judge。

本次不重做各单参数条件的α=0基线，直接比较各条件的均值及同sample ID回答，不将跨采样配置的基线当成各自配对基线。重复率与截断同时报告；两组尚未完成前不归因于单一参数。

### run与Drive对应

run ID：`steer-qwen25-sampling-ablation-20261027-210030`；`${PV_WORK}/runs/steer-qwen25-sampling-ablation-20261027-210030/`。Drive实验文件ID尚未分配，完成归档后补充。

生成与评分以冻结的`source/scripts/sampling_controls.slurm generate RUN`、`score RUN`执行，设置PV_WORK。配置、向量、题目、源码都记录SHA256；每条回答验证模型、生成指纹与sample ID，评分保留原始回答。账户qdj_project_owned1/spgpu2，单L40S、BF16。

### 结果

<!-- sampling-results:start -->
全部生成与评分完成。以下为各条件数值评分均值；非数值trait评分不计为零。
| 条件 | trait | coherence | trait数值条数 | 重复率 | 截断 |
|---|---:|---:|---:|---:|---:|
| topk-only-evil-l20-a1 | 13.05 | 86.33 | 40 | 0.9% | 2/40 |
| topk-only-evil-l20-a1p5 | 64.47 | 59.60 | 40 | 1.3% | 2/40 |
| penalty-only-evil-l20-a1 | 27.02 | 68.42 | 40 | 0.2% | 1/40 |
| penalty-only-evil-l20-a1p5 | 81.08 | 26.90 | 40 | 0.4% | 9/40 |
<!-- sampling-results:end -->

Slurm任务：{"generate": "64914173", "score": "64914174"}。依赖上一组完成后启动。

### 四组采样配置对比

每格为evil/coherence，均为40条回答的均值；两组新增条件没有自己的α=0基线，不把其他采样条件基线用来计算各自trait增量。

| top_k | repetition_penalty | α=1 | α=1.5 |
|---:|---:|---:|---:|
| 0 | 1.0 | 27.48 / 70.00 | 81.12 / 30.15 |
| 20 | 1.0 | 13.05 / 86.33 | 64.47 / 59.60 |
| 0 | 1.05 | 27.02 / 68.42 | 81.08 / 26.90 |
| 20 | 1.05 | 9.95 / 89.08 | 73.45 / 60.17 |

在本模型、本向量、本题目和系数下，coherence改善主要随top_k=20出现。单独把重复惩罚改为1.05，α=1的coherence为68.43（旧70），α=1.5为26.90（旧30.15）；单独top_k=20则分别为86.33与59.60。两者同时开启分别为89.08与60.18。

单独重复惩罚确实降低重复4-gram比例（α=1约0.75%→0.25%，α=1.5约1.31%→0.39%），却没有恢复语义连贯性。不能把机械重复率当作coherence的替代。top_k可能减少异常低概率词的采样，但尚未分析逐token概率来证明这一机制。

本结论来自10题×4次固定seed，不据此推广到所有模型或把两者同时开启比仅top_k的小差异认定为稳健收益。
