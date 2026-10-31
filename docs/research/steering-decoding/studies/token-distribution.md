# Steering后的token分布机制诊断

研究ID：`sd-distribution`。返回[研究线](../overview.md)／[总入口](../../index.md)。

这是一份持续维护的研究记录：同一问题的重跑、模型/系数补测和恢复任务写入本文件，不再递增编号创建文档。以下保留原设置、结果、限制和归档对应关系；历史状态只代表当时，当前状态必须核对具体run。

证据章节：[1](#evidence-16)。run与Drive总表见[统一登记表](../../run_registry.json)。

<a id="evidence-16"></a>

## Qwen2.5：steering与token分布诊断

### 问题与设置

检验“steering使分布变平/尾部概率变大，从而更易跑偏”的假设。固定Qwen2.5-7B-Instruct原revision、raw evil向量、L20 response注入，复用记录10与13的既有回答和原Luna分数，不重新生成、不调用judge。

每个来源固定所有10道题的rollout=0，避免只挑坏例子。来源：旧采样基线，旧采样α=1与1.5，以及仅top_k=20/重复惩罚1.0的α=1与1.5，共50条已有回答。对40条steered路径分别按同一保存token前缀重放α=0与原α，基线重放一次，共90次KV-cache逐token replay。每步保留历史KV并逐个输入原生成token，hook与原response模式相同，不用只改最后一位的全序列teacher forcing近似。

各步保存原始logits分布与施加原重复惩罚/min_new_tokens后的分布，计算entropy（nats）、top20累计概率、top1概率、实际token排名/概率、top-k后的分布；EOS单独标记，不参与content token均值。精确top20累计概率与HF按第20名阈值保留并列token的概率分别记录。每条回答先按token求均值，再按回答等权汇总，避免长乱码输出主导平均；另报首token与前50token。

同一前缀下有/无steering的比较用于隔离即时分布影响；无steering沿steered回答前缀的重放属于反事实条件，不是模型自由生成。不同采样来源的回答前缀不同，不把它们的直接差值全部归因于单次logits干预。没有逐token人工标注的“首个跑偏点”，排名只用于后续对照上下文，不能把rank>20自动判成语义错误。

### run与Drive对应

run ID：`diagnostic-qwen25-token-distribution-20261028-171548`；`${PV_WORK}/runs/diagnostic-qwen25-token-distribution-20261028-171548/`。原始输入路径和SHA256见config与manifest；Drive文件ID尚未分配。

### 结果

已完成，结果见下节。逐token结果在`tokens/<来源>/<steered或unsteered>/`；每条回答有summary与完整token记录，最终汇总为`summary.json`。源回答保留在`inputs/`。

### 验证与复现

GPU上先验证均匀分布的熵与top20质量、极集中分布的熵与排名，再加载模型。保存top-k处理后的实际token零概率计数，用于识别缓存重放/数值差异是否让原top-k样本看似不在支持集，出现时须先核查而不是直接解释成异常采样。

冻结入口：`source/scripts/token_distribution_diagnostic.slurm RUN`，设置PV_WORK。固定单L40S、BF16、SDPA，账户qdj_project_owned1/spgpu2，最长6小时。

Slurm任务ID：`64977369`。

### 已完成结果与解释

任务64977369成功完成，用时30分19秒，50条已有回答、90次KV-cache重放，无新增生成或judge调用。每个来源10题，每题固定rollout0；先按每条回答的content token平均，再对回答等权平均。

#### 实际生成路径的原始分布（top-k前）

| 路径 | entropy（nats） | top20质量 | top1概率 | 实际选中token排名>20 |
|---|---:|---:|---:|---:|
| 无干预基线 | 0.805 | 99.24% | 74.87% | 0.80% |
| 旧采样α=1 | 1.396 | 95.22% | 63.91% | 4.93% |
| 旧采样α=1.5 | 2.045 | 89.85% | 52.97% | 9.93% |
| 仅top-k α=1 | 1.274 | 96.62% | 65.11% | 0.00% |
| 仅top-k α=1.5 | 1.705 | 93.36% | 57.71% | 0.00% |

上表不同路径有不同的生成上下文，差异不全是即时注入造成。旧采样α=1.5的top20以外累计概率约10.15%，实际约9.93%的content token排名>20；基线分别约0.76%与0.80%。这里的百分比是按回答等权的token比例，并不是低coherence回答比例。

#### 相同已保存前缀上的直接比较

| 固定路径 | 无steering熵 → 有steering熵 | 无steering top20 → 有steering top20 |
|---|---:|---:|
| old-a1 | 1.203 → 1.396 | 96.83% → 95.22% |
| old-a1p5 | 1.808 → 2.045 | 92.35% → 89.85% |
| topk-a1 | 1.078 → 1.274 | 98.10% → 96.62% |
| topk-a1p5 | 1.434 → 1.705 | 95.86% → 93.36% |

同前缀下也观察到steering提高熵、降低top20累计概率，支持注入确实使下一token分布更分散，而不仅是不同文本上下文的相关性。但同前缀直接变化小于完整生成路径间的差异，与“局部分布偏移后，后续上下文继续放大偏移”的解释相容，尚不能单凭这些均值证明具体语义跑偏机制。

首token的top20质量基线99.963%、α=1为99.949%、α=1.5为99.906%，此时尾部还很小；沿回答继续生成后差距扩大。因此不是一开始每一步都没有明显高概率候选：旧采样α=1.5的top1概率平均仍约53%。更准确的说法是尾部质量增加和局部不确定位置增多。

重放一致性：两组仅top-k来源，在原steering下所有已保存content token都未被top-k cutoff排除，实际token零概率计数均0；无steering反事实重放下部分token落出top20属于预期，不当作重放错误。

结论：这批Qwen2.5数据支持“steering使分布更分散、尾部采样增多，top-k截断可减轻退化”的假设。未标注首个语义跑偏位置，也未检验每个尾部token是否错误；不能把尾部token等同于坏token。后续若要定位触发机制，可针对少数转折处查看逐token排名与上下文，或做强制替换token的分支对照；本次未提交新任务。
