# Qwen3.5的采样迁移、注入位置与候选层

研究ID：`sd-model-layer-transfer`。返回[研究线](../overview.md)／[总入口](../../index.md)。

这是一份持续维护的研究记录：同一问题的重跑、模型/系数补测和恢复任务写入本文件，不再递增编号创建文档。以下保留原设置、结果、限制和归档对应关系；历史状态只代表当时，当前状态必须核对具体run。

证据章节：[1](#evidence-12) · [2](#evidence-14)。run与Drive总表见[统一登记表](../../run_registry.json)。

<a id="evidence-12"></a>

## Qwen3.5 evil：采样设置对照

### 目的与设置

复用`steering-followups-20261024-193631`的Qwen3.5-4B evil raw向量、10道固定测试题与每题4次rollout、配对seed。固定1-based第12层，对照response与all两种注入位置，α={0.5,1,1.5}，共享α=0新基线，共280条。只把top_k=0改为20、repetition_penalty=1.0改为1.05。模型revision、原冻结推理代码、SDPA、temperature=1、top_p=1、max_new_tokens=1000、EOS与向量均保持一致，不重新提取、不扫层。

这组新采样参数取自Qwen2.5 upstream路径继承的默认值，是在Qwen3.5上的干预对照，不声称是Qwen3.5官方默认值或论文明确指定值。继续Luna原rubric、无校准，统计trait、coherence、重复率与截断。向量及输入代码已冻结并记录SHA256；生成array限并发1，不与自己争GPU。

### run与Drive对应

run ID：`steer-qwen35-evil-sampling-20261027-205658`；目录`${PV_WORK}/runs/steer-qwen35-evil-sampling-20261027-205658/`。父run为`steering-followups-20261024-193631`（旧数据Drive ID见[记录08](../../persona-vectors/studies/steering.md#evidence-08)）。本次Drive ID尚未分配，不复用父run ID。

生成array：`64914092`（arm0=response与基线，arm1=all）；依赖评分：`64914093`。账户qdj_project_owned1/spgpu2，单卡L40S。

### 结果

全部生成与评分完成。原始回答在`positions/responses/`，评分在`positions/scored/`，汇总在`positions/summary.json`。后续补充与父run的逐条件对比。固定测试题已多次使用，不是独立确认集。

### 复现

配置模板：`configs/qwen35-sampling-control.json`。冻结入口：`source/scripts/steering_followups.slurm positions-generate RUN`（array=0-1%1），完成后`positions-score RUN`；设置PV_WORK。不调用原followups的report阶段，避免读取本次没有重做的旧扫层结果。

### 结果与旧配置对比

280条回答全部生成并评分完成。每个条件40条；基线和response各条件evil数值39条，all条件evil数值40条。非数值评分不填零，配对增量与原始均值的分母可能不同。所有coherence均40条数值评分。

| 注入 / α | 旧evil | 新evil | 旧coherence | 新coherence |
|---|---:|---:|---:|---:|
| baseline | 0.00 | 0.00 | 89.45 | 94.62 |
| response-a0p5 | 11.46 | 4.03 | 77.15 | 89.20 |
| response-a1p0 | 32.18 | 39.51 | 47.45 | 72.15 |
| response-a1p5 | 51.44 | 58.38 | 20.55 | 43.52 |
| all-a0p5 | 12.66 | 9.62 | 73.30 | 87.97 |
| all-a1p0 | 54.02 | 43.00 | 44.17 | 70.80 |
| all-a1p5 | 51.25 | 68.72 | 17.40 | 37.00 |

同层同α下，新采样配置明显改善coherence。无干预coherence也从89.45提高到94.63，不能把steered绝对分数的全部上涨都归于抗steering退化。response α=1相对各自基线的下降从42.00分缩小为22.48分。

L12 response α=1得到evil39.51/coherence72.15，达到70门槛但没有达到75；all α=1为43.00/70.80。all没有普遍优于response：α=1和1.5的coherence更低，α=0.5的trait更高但coherence稍低。α=1.5两种位置仍明显退化。

---

<a id="evidence-14"></a>

## Qwen3.5：候选层的新采样配置对照

复用记录08完整重提的evil和sycophantic向量与原固定测试题，维持模型revision、SDPA及原冻结推理代码。生成统一使用top_k=20、repetition_penalty=1.05、temperature=1、top_p=1、max_new_tokens=1000；仅response注入，继续Luna原rubric无校准。

候选：evil L14/L15各α={0.4,0.8,1.2}，L18/L19各α={0.25,0.5,1}；sycophantic L14 α={0.8,1.2,1.6}。各条件10题×4次，加两trait各40条新基线，合计680条。L14/.4、L15/.4、L18/.25是此前coherence约束候选，L19是此前退化明显的参照；sycophantic L14/1.2是此前较好候选。L12已在记录12运行，不重复。

这是已查看测试题上的探索性补测，不是独立确认实验或完整扫层。对同层同α旧条件做直接比较；没有同条件旧结果的格点只能解释为新探索，不据此单独宣称采样造成改善。

### run与Drive对应

run ID：`steer-qwen35-sampling-candidates-20261027-210030`；`${PV_WORK}/runs/steer-qwen35-sampling-candidates-20261027-210030/`。Drive实验文件ID尚未分配，完成归档后补充。

生成与评分以冻结的`source/scripts/sampling_controls.slurm generate RUN`、`score RUN`执行，设置PV_WORK。配置、向量、题目、源码都记录SHA256；每条回答验证模型、生成指纹与sample ID，评分保留原始回答。账户qdj_project_owned1/spgpu2，单L40S、BF16。

### 结果

<!-- sampling-results:start -->
全部生成与评分完成。以下为各条件数值评分均值；非数值trait评分不计为零。
| 条件 | trait | coherence | trait数值条数 | 重复率 | 截断 |
|---|---:|---:|---:|---:|---:|
| evil-baseline | 0.00 | 94.62 | 39 | 2.5% | 3/40 |
| sycophantic-baseline | 13.07 | 92.25 | 40 | 1.9% | 0/40 |
| evil-l14-a0p4 | 1.05 | 91.22 | 39 | 1.8% | 4/40 |
| evil-l14-a0p8 | 28.28 | 69.65 | 39 | 2.2% | 6/40 |
| evil-l14-a1p2 | 53.36 | 42.92 | 39 | 3.5% | 3/40 |
| evil-l15-a0p4 | 3.69 | 86.38 | 39 | 2.0% | 4/40 |
| evil-l15-a0p8 | 31.77 | 65.05 | 39 | 1.9% | 3/40 |
| evil-l15-a1p2 | 47.15 | 39.98 | 39 | 3.9% | 4/40 |
| evil-l18-a0p25 | 0.51 | 91.80 | 39 | 2.0% | 4/40 |
| evil-l18-a0p5 | 12.07 | 82.00 | 40 | 1.8% | 5/40 |
| evil-l18-a1 | 60.02 | 27.65 | 40 | 13.2% | 12/40 |
| evil-l19-a0p25 | 0.54 | 90.58 | 39 | 1.7% | 4/40 |
| evil-l19-a0p5 | 9.46 | 81.15 | 39 | 1.6% | 5/40 |
| evil-l19-a1 | 55.08 | 34.90 | 39 | 7.7% | 8/40 |
| sycophantic-l14-a0p8 | 39.67 | 91.05 | 40 | 1.2% | 0/40 |
| sycophantic-l14-a1p2 | 53.10 | 88.03 | 40 | 0.9% | 0/40 |
| sycophantic-l14-a1p6 | 72.12 | 80.90 | 40 | 0.5% | 0/40 |
<!-- sampling-results:end -->

Slurm任务：{"generate": "64914175", "score": "64914176"}。依赖上一组完成后启动。

### 解读与旧结果

全部680条生成与评分完成，17个条件各40条，coherence均数值评分。evil多数条件39条trait数值评分，L18/0.5和L18/1为40条；sycophantic均40条。汇总表按各条件有效trait条数求均值，不把refusal填零；严格配对增量须按共同数值sample计算。

在本批已测条件中：
- evil若要求coherence≥80，原始trait均值最高的是L18/α=0.5：12.08/82.00；L19/0.5为9.46/81.15。低系数维持更高coherence但trait较弱。L12/α=1（记录12）提供39.51/72.15，适用于70门槛而非75。此处是探索性比较，不是重新做独立选层确认。
- evil L14/0.4：旧6.62/77.03，新1.05/91.23；L15/0.4：旧7.97/74.83，新3.69/86.38；L18/0.25：旧3.21/79.18，新0.51/91.80。改善coherence不等于trait必然增强。
- evil L19/0.5：旧12.82/58.05，新9.46/81.15；L19/1：旧41.53/13.38，新55.08/34.90。大系数问题依旧。
- sycophantic L14/α=0.8、1.2、1.6分别为39.68/91.05、53.10/88.03、72.13/80.90；基线为13.08/92.25，trait增量分别为26.60、40.03、59.05，无截断。
- sycophantic L14/1.2旧61.30/76.73、新53.10/88.03；旧基线15.28/85.10、新基线13.08/92.25。trait增量约46.03→40.03，而coherence相对基线下降约8.38→4.23，权衡改善。

高α仍可能导致崩溃：evil L18/1的coherence27.65、重复率13.25%、截断12/40。新采样不是通用修复，也不证明此前所有问题只有采样原因。本次Qwen3.5只比较两参数组合，参数拆分的结论目前只在Qwen2.5成立。所有题目此前已查看，下一步确认最好换未使用的题目。
