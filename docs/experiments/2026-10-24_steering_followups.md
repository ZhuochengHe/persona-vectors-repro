# Steering 后续实验：注入位置、层与系数、trait差异

用户于2026-10-24要求记录本轮想法，并在实验完成后补结果和分析。模型为Qwen3.5-4B；judge为GPT-5.6-Luna，不校准。

## 当前证据

| 已完成实验 | trait均值 | coherence均值 | 解释范围 |
|---|---:|---:|---|
| evil无干预（修正协议，40回答） | 0.00 | 89.45 | 当前对照基线 |
| evil第12层，α=0.5，response | 11.46 | 77.15 | 开发集按75门槛选定，再在固定测试题验证 |
| evil第18层，α=0.25，response | 3.21 | 79.18 | 开发集达到80，测试集未达到80 |
| evil第19层，α=1，response，新向量 | 41.53 | 13.38 | 同方向大系数会严重退化 |
| 第19层等范数随机方向，α=1，3种子均值 | 0.09 | 88.02 | 单纯扰动范数不足以解释persona方向退化 |
| sycophantic无干预（旧协议） | 15.60 | 85.38 | 旧数据，仅提供线索 |
| sycophantic第20层，α=1（旧协议） | 91.25 | 36.75 | 旧生成结束协议存在问题，不能代替本轮比较 |

evil第19层α=1的重复4-gram比例为27.3%，等范数随机方向均值为2.6%。当前证据支持方向相关退化，但尚未确定具体混杂特征。

## 假设与判读

1. **注入位置影响效果。** 原论文仓库默认response，仅改最后一个prompt位置及后续decode位置；2603.21398实验脚本使用all，额外干预全部prompt位置。配对比较才能判断all是否改善trait/coherence权衡；不能预设all一定更好。
2. **第12层只在较小系数下有效。** 测量α=0.5、1、1.5的变化，分清更强trait与输出退化，不能只看trait分数。
3. **层与系数需要联合选择。** 在多个层同步扫描0.4、0.8、1.2、1.6，报告trait增量最高的五个不同层，并寻找coherence达标的设置。
4. **evil可能与模型安全行为发生冲突。** 这是待验证的解释。旧sycophantic也严重退化，说明现象不显然是evil独有。本轮重新提取sycophantic并使用同一运行协议；即使evil更差，也不能证明是安全训练导致，因为trait、题目、向量范数、提取样本均不同。因果归因仍需要额外对照，不把本轮观察当成安全训练的直接证据。

## 本轮固定设置

共同设置：冻结模型revision和代码；非thinking、BF16、SDPA推理；raw mean-difference向量，不做单位归一化。温度1、top_p=1、top_k=0、最多1000新token，使用修正后的assistant-turn EOS；所有条件按sample_id配对采样seed。Luna并发2，超时600秒，保留重试和延后重试；不同评分作业串行执行。保留拒绝/无效标签，均值不以0填充，报告配对数值样本数。

### A：evil第12层注入位置与强度对照

- 两种位置：response（最后一个prefill位置＋每步decode）与all（全部prefill位置＋每步decode）。只改第12层，不是全部层。
- 系数：0.5、1、1.5。包括共享α=0基线。
- 同一组10道固定测试题，每题4次，共280条回答。精确匹配时复用已完成的基线40条和response/α=0.5的40条，新增200条。
- 记录trait、coherence、重复4-gram比例、截断数和非数值评分计数。
- 这些题已经用于之前实验，A是配对诊断，不是全新未查看的测试集。

### B：evil逐层扫描

- 1-based层：4、8、12、14、15、16、17、18、19、20、21、22、24、26、28、32。
- 各层均测α=0.4、0.8、1.2、1.6；位置固定response，以隔离层/强度效应。
- 使用完整重跑E01后的evil向量。
- 开发集5题×4次，共1300条回答（含20条基线）。

### C：sycophantic逐层扫描

- 与B相同层、系数、采样参数和题目划分规模；仍为各trait原repo评估题，不将不同trait的问题视作匹配题目。
- 先完整重跑sycophantic E01：10题×3对正负指令×3次，共180条；重新评分、配对过滤、提取向量。E01使用与已重跑evil相同的eager后端和修正EOS协议。
- 再以SDPA运行1300条开发集回答。

### 选层与验证

- 每个trait报告无coherence筛选时trait配对增量最高的5个不同层，每层展示其最佳系数及coherence。
- 主门槛为平均coherence≥75，补充门槛为≥70；分别在所有候选层/系数中最大化正向配对trait增量。同分依次优先更高coherence、更小α、更小层号。
- 不因为某个候选层未进入无约束前5名就丢弃一个coherence合格的设置；完整曲线保留。
- 若没有正增量且coherence达标的设置，明确报告无合格设置。
- 两个门槛各选择一个设置，冻结后在每trait10道固定测试题×4次上验证；共享基线、相同设置去重，每trait最多120条。
- 已多次查看这组测试题，结果反映重复使用固定测试集的验证，不声称是全新独立确认。测试结果不用于本轮反向改层或改阈值。

新增规模上限：位置对照200＋sycophantic提取180＋两trait扫描2600＋两trait验证240＝3220条回答。另复用80条位置对照数据。优先让位置对照和新sycophantic提取开始；通过预检后排扫描。保留配置、代码、向量来源和实验数据。

## Backup：换回Qwen2.5-7B-Instruct做同模型诊断

状态：用户要求先记录，尚未下载模型或提交此backup任务。用途是区分Qwen3.5模型差异与提取/steering流程的影响。

- 使用原论文同款 `Qwen/Qwen2.5-7B-Instruct`，固定1-based第20层，首先测试evil。预计48GB L40S单卡可用BF16运行7B推理与逐样本activation提取；实际执行前仍需验证显存、模型revision及chat template。模型和缓存放scratch或可用的大容量存储，不放home。
- 必须在Qwen2.5上重新生成正负回答、评分并提取该模型自己的persona vector，不能复用Qwen3.5向量。先保持我们的缩小规模：10题×3对指令×3次，共180条提取回答；记录过滤后有效配对数和逐层范数。
- 第20层使用raw vector，response注入，与原论文公开推理路径对齐。保留无干预和零系数hook一致性检查，固定题目与采样seed；起步可测α={0,0.5,1,1.5,2}，具体规模及系数在实际提交前冻结。
- 记录trait、coherence、重复率、截断、向量范数及相对activation的扰动强度；检查完整回答，避免只凭trait评分认定成功。主judge仍是Luna，不校准；注明它与原论文评分方式的差异。
- 若该模型在当前缩小规模下有效，说明我们的流程至少能在原模型上产生预期效果，增加模型/trait表示差异这一解释的可信度，但不能据此证明Qwen3.5不存在实现问题。
- 若仍无效或严重退化，优先排查pipeline和缩减提取规模，但不能断言一定只有这两个原因。可逐步增加提取问题、指令和rollout，并保持评估条件不变，观察有效配对数、向量稳定性及steering效果是否改善。
- 如能取得与该模型匹配、来源明确的作者向量，再补“作者向量＋我们的推理”及“同一向量＋upstream推理”的受控对照；若无作者向量，则比较同一批回答在两套提取代码下的结果。这样才能进一步区分向量构造问题与运行/注入问题。

这是一项诊断backup，不替代当前Qwen3.5的注入位置和逐层实验，也不在本轮新增3220条预算内。

## 运行位置与任务

<!-- followup-jobs:start -->
运行根目录：${PV_WORK}/runs/steering-followups-20261024-193631

| 阶段 | Slurm任务 |
|---|---|
| check-followup-settings | 64746096 |
| eval-evil-prompt-positions | 64746097 |
| extract-syc-fresh-responses | 64746098 |
| judge-syc-fresh-responses | 64746099 |
| extract-syc-fresh-vectors | 64746100 |
| check-syc-fresh-vector | 64746101 |
| eval-evil-moderate-grid | 64746102 |
| eval-syc-moderate-grid | 64746103 |
| judge-evil-prompt-positions | 64746104 |
| judge-evil-moderate-grid | 64746105 |
| judge-syc-moderate-grid | 64746106 |
| eval-evil-moderate-test | 64746107 |
| eval-syc-moderate-test | 64746108 |
| judge-evil-moderate-test | 64746109 |
| judge-syc-moderate-test | 64746110 |
| report-steering-followups | 64746111 |

全部生成和评分任务依赖前置成功；最终report任务自动回填本文件的结果块。
<!-- followup-jobs:end -->

## 结果与分析

<!-- followup-results:start -->

两组扫描和位置对照均已完成。以下结果由冻结的实验汇总文件生成。

| 第12层设置 | trait均值 | coherence均值 | 重复4-gram比例 |
|---|---:|---:|---:|
| baseline | 0.00 | 89.45 | 2.7% |
| response-a0p5 | 11.46 | 77.15 | 2.9% |
| response-a1p0 | 32.18 | 47.45 | 3.6% |
| response-a1p5 | 51.44 | 20.55 | 13.1% |
| all-a0p5 | 12.66 | 73.30 | 2.3% |
| all-a1p0 | 54.02 | 44.17 | 5.4% |
| all-a1p5 | 51.25 | 17.40 | 9.3% |

各trait的开发集选层及固定测试集验证：

| trait / 门槛 | 层 / α | 开发集trait增量 | 开发集coherence | 测试集trait增量 | 测试集coherence |
|---|---|---:|---:|---:|---:|
| evil / 75 | 14 / 0.4 | 4.47 | 75.25 | 6.62 | 77.03 |
| evil / 70 | 15 / 0.4 | 11.69 | 74.60 | 7.97 | 74.83 |
| sycophantic / 75 | 14 / 1.2 | 46.50 | 76.85 | 46.02 | 76.72 |
| sycophantic / 70 | 14 / 1.2 | 46.50 | 76.85 | 46.02 | 76.72 |

初步解读：

- evil 按75门槛选出的设置，在测试集达到该coherence门槛；不据测试结果重新选层。
- evil 按70门槛选出的设置，在测试集达到该coherence门槛；不据测试结果重新选层。
- sycophantic 按75门槛选出的设置，在测试集达到该coherence门槛；不据测试结果重新选层。
- sycophantic 按70门槛选出的设置，在测试集达到该coherence门槛；不据测试结果重新选层。
- evil第12层 α=0.5：all相对response的平均coherence变化为-3.85；需结合trait与重复率判断是否改善权衡。
- evil第12层 α=1.0：all相对response的平均coherence变化为-3.28；需结合trait与重复率判断是否改善权衡。
- evil第12层 α=1.5：all相对response的平均coherence变化为-3.15；需结合trait与重复率判断是否改善权衡。
- 这些对照不能单独证明安全训练导致崩溃；trait方向、向量范数、题目和提取样本均有差异。
- 逐层完整曲线、排名及非数值评分计数保存在各run的development-summary.json、selection.json和heldout-summary.json。


### 完成核对与补充分析（2026-10-25T10:46:05-04:00）

本轮所有Slurm作业均COMPLETED、退出码0；当前无活动实验。两个trait各1300条开发集回答与评分完成；evil测试集120条，sycophantic测试集80条（两个门槛选中相同设置，已去重）；位置对照280条及sycophantic提取180条也均完成，无待重试项。
已核对两组扫描和测试的2800条生成/评分匹配、生成指纹、开发集均值、选层排序及测试集均值。以下均为Luna直接评分，拒绝/无效评分不填0。

| trait / 选层门槛 | 层 / α | 测试集无干预trait | 测试集steered trait | trait增量 | 无干预coherence | steered coherence | trait数值评分数 |
|---|---|---:|---:|---:|---:|---:|---:|
| evil / 75 | 14 / 0.4 | 0.00 | 6.62 | +6.62 | 89.45 | 77.03 | 39/40 |
| evil / 70 | 15 / 0.4 | 0.00 | 7.97 | +7.97 | 89.45 | 74.83 | 39/40 |
| sycophantic / 75 | 14 / 1.2 | 15.28 | 61.30 | +46.02 | 85.10 | 76.72 | 40/40 |
| sycophantic / 70 | 14 / 1.2 | 15.28 | 61.30 | +46.02 | 85.10 | 76.72 | 40/40 |

前5个不同层（不加coherence门槛，按开发集配对trait增量排名；每层取该增量最高的系数）：

| trait | 排名 | 层 | α | trait增量 | coherence |
|---|---:|---:|---:|---:|---:|
| evil | 1 | 17 | 1.6 | 60.39 | 13.80 |
| evil | 2 | 16 | 1.2 | 55.35 | 33.20 |
| evil | 3 | 18 | 1.6 | 51.76 | 7.75 |
| evil | 4 | 14 | 1.2 | 48.94 | 37.35 |
| evil | 5 | 20 | 1.6 | 46.69 | 11.60 |
| sycophantic | 1 | 20 | 1.6 | 74.15 | 14.30 |
| sycophantic | 2 | 21 | 1.6 | 73.55 | 19.15 |
| sycophantic | 3 | 19 | 1.2 | 72.25 | 18.40 |
| sycophantic | 4 | 18 | 1.6 | 70.90 | 36.00 |
| sycophantic | 5 | 22 | 1.6 | 70.05 | 7.40 |

结论与限制：

- sycophantic第14层/α=1.2在开发集和测试集均达到coherence≥75，测试集trait增量为46.03（问题聚类bootstrap 95%区间31.20–58.93）。这是本轮较清楚的、保留一定连贯性时的trait控制结果。
- evil在coherence≥75门槛下选出的第14层/α=0.4，测试集trait增量仅6.62；放宽到70后选出的第15层/α=0.4，增量为7.97。新增网格未找到强evil效果与较高连贯性兼得的设置。
- 两个trait不加coherence约束的高trait候选均明显退化。因此，输出退化并非evil独有；同时，本轮sycophantic比evil更容易取得较好的效果/连贯性权衡。
- 这支持trait方向及层/系数选择的重要性，但不能把差异直接归因于Qwen3.5的安全训练。两个trait的题目、原始向量范数、提取样本和过滤后样本量不同：sycophantic保留87对，重提evil保留24对。
- 本轮网格为0.4/0.8/1.2/1.6，不包含此前第12层α=0.5；不能据本轮选出的第14层就宣称其优于此前第12层设置。
- 开发集只有5题且evil存在非数值评分：75门槛胜出设置的开发集配对trait均值仅覆盖15条、4题，选层可能不稳定。完整数值计数和置信区间保存在JSON。
- 固定测试题此前已查看，结果不是全新未接触测试集上的独立确认；本次未用测试集重新选层。
- 第12层all注入没有恢复连贯性；提高α仍会明显退化。Qwen2.5-7B backup仍仅记录，未下载或启动。

来源：本run的`evil-scan/selection.json`、`sycophantic-scan/selection.json`、两trait的`heldout-summary.json`及`positions/summary.json`。

<!-- followup-results:end -->
