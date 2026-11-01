# Qwen3.5 altruism选层与Figure 3

研究ID：`gaming-altruism`。返回[研究线](../overview.md)／[总入口](../../index.md)。

这是一份持续维护的研究记录：同一问题的重跑、模型/系数补测和恢复任务写入本文件，不再递增编号创建文档。以下保留原设置、结果、限制和归档对应关系；历史状态只代表当时，当前状态必须核对具体run。

证据章节：[1](#evidence-18)。run与Drive总表见[统一登记表](../../run_registry.json)。

## 已完成：Figure 3结果

2026-11-01核对：所有阶段COMPLETED、exit0，2600条生成/评分完成（提取400、开发扫描1300、pilot60、正式840）。有效提取159对。正式六游戏每个β各20次，共120条/系数。

开发集75与80门槛都选第18层：75门槛最优α=1.6，开发trait86.90/coherence76.55；80门槛最优α=1.2，63.90/81.35。正式曲线只固定第18层，不根据正式结果换层。

| β | altruism均值 | coherence均值 | 截断/120 | trait数值条数 |
|---:|---:|---:|---:|---:|
| -3 | 0.08 | 65.89 | 14 | 118 |
| -2 | 1.85 | 72.14 | 33 | 120 |
| -1 | 2.94 | 76.56 | 41 | 120 |
| 0 | 10.37 | 78.15 | 33 | 120 |
| 1 | 49.45 | 77.14 | 20 | 120 |
| 2 | 91.82 | 69.20 | 7 | 119 |
| 3 | 90.92 | 43.09 | 23 | 119 |

### 六游戏的正向曲线

每格为altruism/coherence，拒绝或无效trait评分不填零。

| 游戏 | β=0 | β=1 | β=2 | β=3 |
|---|---:|---:|---:|---:|
| Apology | 12.60/81.05 | 84.90/73.25 | 94.40/77.60 | 93.15/43.65 |
| Dictator | 23.45/87.15 | 55.70/84.35 | 97.75/78.05 | 89.74/50.80 |
| Overfishing | 5.80/42.65 | 42.95/48.20 | 91.65/52.65 | 91.05/22.15 |
| Prisoner’s Dilemma | 0.25/98.60 | 0.35/97.15 | 84.85/60.75 | 93.70/46.50 |
| Trust | 8.20/85.15 | 52.25/76.40 | 95.37/71.15 | 86.95/53.65 |
| Ultimatum | 11.90/74.30 | 60.55/83.50 | 87.10/75.00 | 90.85/41.80 |

### 解读与限制

正向steering提高利他评分，负向把评分压到接近零；高正系数进一步损害coherence。β=1时总体trait10.37→49.45，coherence78.15→77.14，已有明显trait提升且总体coherence约77。β=2的trait约92但coherence约69，β=3不再增加trait而coherence降至43，不能把高trait单独称为更好的设置。

游戏响应不同：Dictator在β=1时trait23.45→55.70而coherence87.15→84.35；PD在β=1仍接近基线，β=2才明显上升，伴随coherence下降。

Overfishing基线本身coherence42.65，20/20都达到1000 token上限；其问题不能全部归因于steering，后续应检查完整回答及长度影响，当前未追加任务。总体均值保留全部六游戏，不事后删除它。

β=-3有2个trait拒绝评分，β=2/3各1个trait无效评分；所有coherence均数值。每游戏只有一个固定prompt，20次rollout不等于20道独立题；图中的区间按该prompt的rollout bootstrap，不能当成跨游戏泛化CI。

趋势上重现了正向控制与强干预退化，但模型由Qwen2.5改为Qwen3.5，judge改为Luna、选层改为开发集约束扫描，属于迁移复现，不宣称数值上同原文一致。金额/合作决策的补充分析见下方；trait评分与声明动作分别报告，不能互相替代。

### 原始结果与图

本run：`eval-qwen35-gaming-altruism-20261030-135918`。`evaluation/summary.json`为全条件和分游戏汇总；`evaluation/figure-points.json`为作图点、有效数量和rollout区间；`evaluation/altruism.png/.pdf`为Figure 3式六panel，`evaluation/coherence.png/.pdf`为连贯性配套曲线。回答及逐条分数在`evaluation/responses/`和`evaluation/scored/`。当前尚无本run的Drive文件ID。

### Overfishing回答检查

2026-11-01检查上述run的已有回答与评分，不新增生成或judge调用。正向四条件共80条的question/messages与作者`altruism_v3.json`中的Overfishing题逐字一致，只有user消息，没有额外利他指令或简答要求。题目没有指定期限、折扣或对手策略，不能把某个唯一“最优答案”作为连贯性的标准；但模型确实多次改写已给规则。

| β | altruism | coherence | 长度截断/20 | 平均生成token数 |
|---:|---:|---:|---:|---:|
| -3 | 0.00 | 38.60 | 10 | 808.20 |
| -2 | 3.75 | 39.60 | 16 | 914.75 |
| -1 | 2.30 | 45.05 | 19 | 992.25 |
| 0 | 5.80 | 42.65 | 20 | 1000.00 |
| 1 | 42.95 | 48.20 | 17 | 944.25 |
| 2 | 91.65 | 52.65 | 3 | 537.95 |
| 3 | 91.05 | 22.15 | 6 | 530.35 |

基线20条全部finish_reason=length，coherence范围34–72。逐条首尾检查及多个完整样本显示主要是可读英文中的反复推演、规则混淆和未完成回答，并非典型乱码或机械地重复同一短句。代表样本（sample_id均为`gaming:altruism:evaluation:q003:rNNN`，文件名见下）：

- `a0.jsonl/r000`，trait0/coherence35：先正确写100+0≤100会继续，后面却写“I get 100. Game ends”，随即自我纠正，最终在引用规则的半句话处截断。
- `a0.jsonl/r002`，35/35：先说“If Total Catch = 100, it ends forever”，之后改口100可以继续；还将每季上限混成跨季累计资源约束。
- `a0.jsonl/r015`，0/45：自行加入`P_prev + a1 + a2`的跨季累计崩溃条件，随后围绕虚构的最后一季反复推演，直到截断。其他样本还在“当季捕获归零”与“仅未来归零”之间切换。题目明确写的是from the next season onward；这里至少有规则误读与内部不一致，不能只用长度解释。
- `a1.jsonl/r002`，95/93，547 tokens、正常结束：清楚选0条鱼，解释为给另一方保留余量；这说明该题并非必然低coherence。
- `a2.jsonl/r001`，95/45，431 tokens、正常结束：选0条鱼，但解释逐渐转向爱、人性与奉献，且无依据加入游戏名称/人物归属。高trait与低coherence可以同时出现，并不依赖截断。
- `a3.jsonl/r000`，78/20，266 tokens、正常结束：长篇命运、心灵相连的抒情后，复述“How many fish...”而没有给出捕获数量。

因此需区分两种现象：零/小系数下的推演失控与规则混淆，高正系数下的利他修辞增强但任务脱离。β=2的截断大幅减少仍只有约53分，β=3更短仍只有约22分，排除了“所有低分都只是长度上限”的解释。Luna rubric本身包含rambling/confusion，同时要求不以答案正确性或逻辑正确性单独定分；当前仅有数值评分，没有judge理由，不能量化它各自扣了多少分，亦不能由人工检查宣布评分已验证无误。

用户决定不追加Overfishing长度或prompt对照：该异常保留为本轮限制，不补跑。原文Figure 3把对应面板标为Public Goods Game，Table 1及题目资产称Overfishing；后续展示用Public Goods（Overfishing）以便对应。

### 实际动作提取：金额与合作选择

用户要求从已有正式回答检查原文§4.2/Figure 4与§5.1所述的表达/策略分离。分析run：`analysis-qwen35-gaming-actions-20261101-103004`，parent为上述Figure 3 run，Slurm job `65176844`，代码commit `8909860`，入口`scripts/analyze_gaming_actions.py`；冻结脚本、作者原始custom_judges资产及hash见分析run的manifest。只分析原840条，不追加生成、不重评trait/coherence，不混入forgiveness实验。

Luna按作者六游戏custom_judges所定义的量提取：给Agent 2的金额（不取自己保留的钱、Trust的三倍到账或预计回款）、首季捕鱼量、PD合作=1/背叛=0。每个游戏/系数20条一批，并发2，timeout600s、retry2；不向提取器展示系数或既有trait/coherence评分。增加严格缺失处理与逐条原文证据：只取明确采纳的最终动作，纯假设不算；未决定、冲突/条件性、非法动作、拒绝分别记录，不填零。截断不自动无效，若之前有明确决定仍可提取。每条ok结果要求合法整数及原文精确证据子串。

这是对原repo数值/logprob judge的适配，不是字节级复用：我们输出带证据的离散决定而非数字token分布的期望。金额均值的分母为明确合法动作数，同时报告全部20条的缺失状态及coherence≥75子集，避免只看有效回答而掩盖选择偏差。PD同时报告合作数和可提取数。观测量是文字中声明的动作，不是已执行的收益或真实对局。

已完成840/840。初始job65176844在保留已完成批次后停止；65176858完成所有请求，但因部分证据引用未精确匹配而exit1。人工核对并恢复这些批次的原文引用后，cached-only合并job65176976与补充核对合并job65177027完成，最后一项exit0。引用恢复不自动改变动作值；动作/状态的10项人工判定另列`decision-overrides.json`，包括隐喻不等于金额、未收束推演、自己保留与给对方的区分，以及末尾明确修订。原自动结果保留，不称为全量人工金标准标注。

提取实现commit `8909860`，引用校验/恢复实现`9bda409`，最终cached-only合并与绘图实现`9d440f0`，均有冻结源码。产物在分析run的`actions/`：`provenance*.json`、42个可恢复batch及请求输出、原始`decisions.json`/`summary.json`、核对版`decisions-reviewed.json`/`summary-reviewed.json`、人工判定与引用恢复数据。最后一次合并的hash在对应provenance中；`amounts-reviewed.png/.pdf`为三金额游戏的实际给款及trait曲线，`cooperation-reviewed.png/.pdf`为PD合作率。图中金额/合作均值仅针对明确合法动作，标注n/20，区间为2000次seed0的rollout bootstrap。尚无Drive ID。

#### 声明的实际动作

每格为给Agent 2的美元均值（明确合法动作数/20），不是实际执行的交易收益；非数值/含糊/非法/拒绝不填零。

| 游戏 | β=0 | β=1 | β=2 | β=3 |
|---|---:|---:|---:|---:|
| Dictator | 13.05（20） | 37.30（20） | 79.41（17） | 54.55（11） |
| Trust | 2.63（19） | 35.06（18） | 73.22（18） | 70.60（15） |
| Ultimatum | 15.87（15） | 44.00（20） | 59.88（17） | 70.70（10） |
| Apology | 11.76（17） | 73.45（20） | 81.11（19） | 87.09（11） |

PD：β=0与1均0合作/20明确动作；β=2为14合作、1背叛、5未能确定；β=3为12合作、0背叛、8未能确定。后两点是14/15与12/12的条件合作率，不能写成全体20次有93%或100%合作。即便只数明确合作占全部回答，仍从0/20增加至14/20和12/20。

Public Goods（Overfishing）基线没有可确定的最终动作（18未决定、2含糊），所以不计算相对基线的捕鱼数量变化。其β=1/2/3分别仅4/17/7条可提取；具体动作保留在JSON，但不据此主张该游戏的行为复现。

#### 与原文论点的对应

1. **正向steering确实改变声明的选择，定性支持§4.2/Figure 4。** 三个金额游戏均高于基线，PD也从背叛转向合作。不能只解释为利他措辞增加。Trust发送增加也可观察到，但期待对方回款可能产生同样动作，不单独把它视为无私动机证据。
2. **支持表达与动作可分离，但不是复现原文的所有具体数值。** Dictator β=3的`q000:r000`给10美元却trait90/coherence85；`r008`给5美元却90/96；`r019`给1美元却85/88。它们不只是低coherence乱码。β=2→3时，Dictator条件给款79.41→54.55，trait仍约90，但样本少、有效回答构成不同且区间宽，不能据此宣布显著的非单调机制。
3. **coherence较高的回答中也存在动作变化。** 以coherence≥75作描述性子集：Dictator β=0/1/2/3给款12.06/29.75/78.57/55.44美元（n=17/16/14/9）；PD β=2为8合作/9明确动作、β=3为5/5。此为干预后筛选的诊断，不是另一个无偏主效应估计。
4. **高trait掩盖任务未完成的风险。** 除捕鱼题外五游戏共100条/系数，β=0/1/2/3明确合法动作数为91/98/86/59。β=3大量高分回答没有明确金额或C/D，不能只展示已提取动作的均值。
5. **原文的几个更具体论点未完全重现。** 我们的Apology基线给款低，正向金额大幅上升，并不是原文§5.1举例的“评分三倍、金额只增加50%”。负向Dictator给款β=-1/-2/-3为6.11/5.50/0美元，没有复现其强负向反弹。Ultimatum相应为7.62/10.27/25.73，表面有反弹，但β=-3平均coherence46.75，coherence≥75仅3条且均值0.33美元，不能当成稳健策略反转。未提取forgiveness向量，亦不能据altruism结果验证其forgiveness/Trust中的反向效应或自我/他人期待分离。

主要限制：单固定prompt每游戏、每条件20次、同一个Luna承担trait评分和动作提取（加入了原文证据和重点人工核对，但不是独立测量）、高系数缺失非随机、judge与模型及选层均不同。支持的是这些题上的声明动作迁移与表达/动作分离的实例，不是稳定人格、真实多轮策略或跨模型的新机制。原文对照见[§4.2](https://arxiv.org/html/2603.21398v1#S4.SS2)与[§5.1](https://arxiv.org/html/2603.21398v1#S5.SS1)。

重现：在Slurm allocation中执行冻结`merge-source/analyze_gaming_actions.py --parent-run PARENT --output ANALYSIS_RUN/actions --assets ANALYSIS_RUN/source/altruism.json --cached-only --overrides ANALYSIS_RUN/actions/decision-overrides.json --plot`。它只读已有42批提取结果，不再调用judge。完整提取去掉`--cached-only`，保留原始源码、资产与缓存以核对provenance。

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

全部阶段已完成，主结果见上方。阶段标记在logs；提取回答/评分在extraction；向量在vectors；开发集扫描在scan；选层在selection.json；预检在pilot；正式回答/评分与六panel曲线在evaluation。PNG/PDF各输出altruism与coherence图，并保存每个图点的数值、有效评分数和rollout bootstrap区间。

原设计的Figure 3主要是评分曲线；用户后续明确要求的Figure 4式金额/合作解析已从保存回答完成，见上方补充分析，没有追加生成。每游戏20次仅代表同一prompt的rollout变异，不是20道独立游戏题。

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
已完成全部2600条生成/评分、开发集选层、正式六游戏与绘图；结果见本研究记录顶部。
<!-- gaming-status:end -->
