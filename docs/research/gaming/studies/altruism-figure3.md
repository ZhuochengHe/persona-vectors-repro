# Qwen3.5 altruism选层与Figure 3

研究ID：`gaming-altruism`。返回[研究线](../overview.md)／[总入口](../../index.md)。

这是一份持续维护的研究记录：同一问题的重跑、模型/系数补测和恢复任务写入本文件，不再递增编号创建文档。以下保留原设置、结果、限制和归档对应关系；历史状态只代表当时，当前状态必须核对具体run。

证据章节：[1](#evidence-18)。run与Drive总表见[统一登记表](../../run_registry.json)。

<a id="evidence-18"></a>

## Gaming Figure 3：Qwen3.5-4B、altruism新向量与coherence约束选层

### 已确认目标

用户2026-10-30选定Qwen3.5-4B、统一Transformers基线与非零steering、建议规模，并要求按我们的方法sweep选层。新增扫层使总预算从1300增至2600条。原论文Figure 3的复现目标、原始prompt版本证据与模型/评分差异见[计划](../protocol.md)。不是固定L20复现，也不是原作者Qwen2.5同模型复制。

模型固定revision851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a，非thinking，BF16。temperature=1、top_p=1、top_k=20、repetition_penalty=1.05、min_new_tokens=1、max_new_tokens=1000。全部prompt与decode位置注入raw向量。Luna原rubric直接评分，不校准，并发2、原retry机制。提取用eager、扫层和游戏评估用SDPA。

### 阶段和预算

| 阶段 | 设置 | 新回答数 |
|---|---|---:|
| 提取 | 作者repo全部40题×5组正负instruction×2极性×1次随机采样 | 400 |
| 扫层开发集 | 16层×4正系数×5个游戏变体×4次，加20条共享基线 | 1300 |
| 选层后预检 | Dictator/PD/Apology开发变体×5系数×4次，独立pilot seed | 60 |
| 正式Figure 3 | 六个原游戏×β=-3..3整数七点×20次 | 840 |
| 总计 | 不重用其他trait或跨模型向量 | 2600 |

代码预检额外只有几条短greedy回答，不算正式实验数据。

层集合：4、8、12、14、15、16、17、18、19、20、21、22、24、26、28、32（1-based）。开发系数0.4、0.8、1.2、1.6。开发集在运行前冻结，收益参数和文字区别于正式六题，也不属于40道提取题；并非将正式游戏结果用于选层。主门槛coherence≥75，补充≥80，在达标设置中最大化配对altruism增量；平局依次高coherence、低系数、低层号。为避免极少数有效评分获胜，至少16/20数值trait配对且覆盖至少4/5题。baseline在各层共享。

仅主门槛选出的层用于正式七点曲线；开发最优系数随selection保留，但不替代原有正负β网格，不重新缩放向量，不根据正式结果换层。所有正式β结果都报告，包括低coherence点。没有合格主候选时停止后续，不默认为第20层。

### 向量与预检门槛

正trait≥50、负trait<50、双方coherence≥50；至少20对、覆盖10道提取题和3组instruction才能进入后续。门槛不随结果放松。保留32层response均值差，不含embedding行；vector[layer-1]与block[layer-1]配对，不使用作者Qwen2.5向量。每层范数保存为metadata。

先在计算节点跑代码测试、零hook等价、真实Qwen3.5 all-hook与作者hook的短greedy输出对照。作者hook通过仅包装layer locator适配Qwen3.5模型壳，注入数学不改。作者脚本会改HF_HOME，导入后恢复原缓存位置。全部操作均在Slurm中；大文件与日志在已有实验存储。

### run、任务与Drive对应

run ID：`eval-qwen35-gaming-altruism-20261030-135918`；位置`${PV_WORK}/runs/eval-qwen35-gaming-altruism-20261030-135918/`。代码、配置、原repo资产和task列表均冻结SHA256；新向量和开发集selection分别生成独立provenance。Drive文件ID尚未分配。

阶段依赖为preflight→extract-generate→extract-score→vectors→scan-generate(array)→scan-score/选层→pilot-generate→pilot-score→evaluation-generate(array)→evaluation-score/绘图。扫层及正式生成最多2张GPU同时运行，评分单进程、内部并发2。为避免与已在跑的采样验证争用judge，extract-score也等待采样验证评分阶段结束（其失败不阻塞gaming自身已成功的提取）。

### 结果

尚未完成。阶段标记在logs；提取回答/评分在extraction；向量在vectors；开发集扫描在scan；选层在selection.json；预检在pilot；正式回答/评分与六panel曲线在evaluation。PNG/PDF各输出altruism与coherence图，并保存每个图点的数值、有效评分数和rollout bootstrap区间。

Figure 3主要是评分曲线。此轮不把Figure 4的金额解析扩展偷偷加入必需任务；原始回答留存，后续可单独解析。每游戏20次仅代表同一prompt的rollout变异，不是20道独立游戏题。

### 复现

配置模板：`configs/gaming-figure3-qwen35.json`。入口：冻结的`source/scripts/gaming_figure3.slurm STAGE RUN`，设置PV_WORK；scan/evaluation generate使用array=0-3%2，其余单任务。模型、题目、向量、generation fingerprint、生成前缀token和评分回答的一致性在各阶段检查。

### Slurm任务ID

| 阶段 | Job ID |
|---|---|
| preflight | 65084244 |
| extract-generate | 65084245 |
| extract-score | 65084246 |
| vectors | 65084247 |
| scan-generate | 65084248 |
| scan-score | 65084249 |
| pilot-generate | 65084250 |
| pilot-score | 65084251 |
| evaluation-generate | 65084252 |
| evaluation-score | 65084253 |

绘图依赖matplotlib==3.10.0；环境版本保留于run/environment.json。上一轮92项代码测试已通过；当前run将重新测试并执行真实模型预检。原预检日志单独保留，未产生正式回答。

<!-- gaming-status:start -->
最近状态：真实模型预检通过，92项代码测试通过，零hook与作者all-hook对照通过。400/400条提取回答已生成，用时2小时1分10秒。尚未评分、未提取向量或扫层；提取评分按预先设置的依赖等待独立采样验证的评分结束，避免Luna任务叠加。当前无gaming失败阶段。
<!-- gaming-status:end -->
