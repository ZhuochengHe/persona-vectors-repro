# 信息缺失识别与主动获取信息（Q01）：问题、假设与路线

状态：计划阶段，尚无实验结果。文献与 benchmark 表在 Google Doc 的 "Q01 Clarification & Q04 Authorization" tab；本文件只维护假设、变体目录和下一步。具体设置与结果在 [is-hil-sql-pilot](studies/hil-sql-pilot.md)。

## 研究问题

Agent 在执行中遇到 blocker（缺失、歧义、矛盾信息）时：

1. **识别（recognition）**：内部表征是否编码"当前有未解决的 blocker"（v_miss）。
2. **行动（action）**：识别后是否去获取信息（提问；之后扩展到检索）而不是猜测推进（v_ask）。
3. **控制**：能否用 steering 提高该问时的提问率，同时不增加不该问时的提问。

定位：已有表征／steering 工作集中在单轮 QA 的 ambiguity 与 answerability；agent 循环中带"已解决"对照、分开报告识别与行动的 steering 结果尚未见到（摘要级检索，未穷尽）。最接近的先例 Heading-Specific Activation Steering（AskUser 向量）需精读后确认差异。

## 假设

| ID | 假设 | 支持的观察 | 反驳的观察 |
|---|---|---|---|
| H1 | 决策点的残差流线性可读出"存在未解决 blocker" | 轨迹内（回答前 vs 回答后）与条件间（blocked vs full-info）的 probe AUC 都明显高于打乱标签和填充文本对照 | 只在条件间可分、轨迹内不可分（说明读到的是 prompt 表面差异） |
| H2 | 8B 模型的欠提问主要是行动失败而非识别失败 | 未提问的 blocker 决策点上 probe 分数仍高 | 未提问时 probe 分数与 full-info 无差别（识别失败） |
| H3 | v_ask 与 v_miss 是不同方向；无条件加 v_ask 会在 full-info 条件下也提高提问 | 余弦相似度低；无条件 steering 使 precision 下降，probe 门控后不下降 | 两者近似共线，或无条件 steering 不引起过度提问 |
| H4 | 最佳读取位置／层与最佳写入位置／层不同 | 离线 AUC 排序与单步 ΔP(ask) 排序不一致 | 两种排序给出同一层 |
| H5 | 从简单成对数据（When2Call、QuestBench）提取的方向可迁移到 HiL SQL | 外部方向在 HiL 决策点上的 AUC 与单步 ΔP(ask) 接近本域方向 | 迁移后接近随机方向 |
| H6 | 可行性：9B 在 HiL SQL full-info 条件下通过率不在地板 | 子集后与用户回顾可行性指标 | 接近地板，则只用 Ask-F1 与决策点指标，不报任务成功率 |

关于 full-info 对照：它把所有 resolution 放回任务，是合格的"blocker 全部已解决"行为对照，也是过度提问的测量条件。唯一需要额外处理的是表征解释：blocked 与 full-info 的 prompt 文本不同，所以 v_miss 的证据不能只来自这一对比，还要有轨迹内对比（H1）。

## 变体目录

从每组的第一项开始做；采集阶段一次保存所有层和位置，使 B–E 组都能离线比较而不必重跑。

**A. 提取对比的来源**
- A1 条件对比：blocked vs full-info 的同题决策点 → v_miss。
- A2 轨迹内对比：同一轨迹中 ask_human 得到 resolution 之前 vs 之后 → v_miss。
- A3 自然行为对比：有未解决 blocker 时提问 vs 未提问 → v_ask。依赖模型自然提问率不退化。
- A4 prompt 诱导对比：正／反 system prompt（"遇到缺失信息先确认" vs "不要提问直接推进"），即本仓库 persona vectors 的做法 → v_ask。A3 不可用时的替代。
- A5 外部成对数据：When2Call 的 follow-up vs tool-call 版本；QuestBench GSM-Q 的缺变量 vs 完整版本。
- A6 SAE 特征：需要有公开 SAE 的模型，8B 级 Qwen 是否有未核实；放在后期。

**B. 方向计算**
- B1 均值差（diff-of-means）。
- B2 logistic probe 的权重方向。
- B3 成对差的 PCA／SVD 主成分。
- B4 稀疏维度掩码：按 probe 权重取 top-k 维，只在这些维上 steer（Sparse Neurons 的做法）。
- B5 SAE latent（随 A6）。

**C. 位置**
- C1 生成前最后一个输入 token。
- C2 `</think>` token（TACT 的提取与 steer 位置，按用户转述，未核实）。
- C3 动作（tool call）的第一个 token。
- C4 最近一次工具返回的 token 均值。
- C5 本步 reasoning token 均值。
- C6 全部输入 token 均值（Sparse Neurons 的 pre-filling 做法）。

**D. 读取方式**
- D1 固定层、单位置的线性 probe 加阈值。
- D2 在均值差方向上的投影加阈值。
- D3 mean pooling 后的线性 probe。

**E. 选层**
- E1 验证集分类 AUC 排序（TACT 的做法，按用户转述）。只回答"哪里读得出"。
- E2 单步 teacher-forced 扫描：在已保存的本模型决策点前缀上加向量，只生成下一步动作，测 ΔP(ask_human)。成本约为一次前向，不需要完整 rollout。
- E3 每隔 k 层同时 steer。
- E4 拓扑选层：<https://arxiv.org/pdf/2611.01493>（尚未阅读，仅登记链接）。
- 闭环确认只对 E1／E2 选出的前 2–3 个配置做。

**F. Steering 方案**
- F0 基线：无干预；仅 prompt 指令（"被阻塞时提问"）。prompt 基线必须有，否则 steering 的增益无法定位。
- F1 无条件加 v_ask（所有生成位置）。
- F2 只在决策位置（C2／C3）加 v_ask。
- F3 probe 门控：v_miss 的 probe 超过阈值时才加 v_ask。
- F4 只加 v_miss：测试增强识别是否足以引起提问。
- F5 负向 steering 或投影消融：必要性检验，预期 recall 下降。
- F6 范数匹配的随机方向对照。

**G. 模拟用户严格度**
- G1 严格判定：沿用论文标准，不匹配时返回 "irrelevant question"。判定模型用 Claude Haiku（论文为 Llama-3.3-70B），闭环默认用它。
- G2 宽松判定：同一批问题离线重判（"一个愿意帮忙的人会不会给出该 resolution"）。
- 只有当 G1 与 G2 的 precision／recall 差距大到改变结论时，才跑宽松判定的闭环版本。分数标为"Claude 判定"，不称官方 HiL-Bench 分数。

**H. 对照条件**
- H1 full-info 且开启 ask_human：过度提问率。
- H2 部分解决：只放回一部分 resolution，检查 probe 分数是否随剩余 blocker 数变化。
- H3 填充对照：blocked 条件加入与 resolution 等长的无关业务文本，排除长度与位置解释。

## 路线

1. [is-hil-sql-pilot](studies/hil-sql-pilot.md)：Qwen3.5-9B 在 HiL SQL 上的可行性与激活采集，先跑 20 题子集。实现方案在该 study 内。HiL 定位为验证集。
2. v_miss 的提取来源（2026-11-16 回退重选）：[When2Call](studies/when2call-extraction.md) 已实现但暂停（缺的是可见的工具参数，且缺参数版整句改写）。重新比较的结果见下方"提取来源比较"。
3. 之后改造第二 benchmark：CLARITI 提问步骤（见下）。

### 提取来源比较（2026-11-16，数据已下载核对的标"已核实"）

选择标准：逐题配对且两边只差缺失部分；缺的是定义、阈值、口径这类领域信息（接近 HiL 的 business-info blocker）；知道缺的是什么；9B 能做；数据公开、成本低。

| 候选 | 配对 | 缺失类型 | 现状 |
|---|---|---|---|
| **BIRD-INTERACT LITE**（HF `birdsql/bird-interact-lite`，CC BY-SA 4.0，已核实） | 300 题；每题有清楚版 `query` 与歧义版 `amb_user_query`（改写，300 题全部不同）；另有 265 条"被删除的知识库条目"标注（`knowledge_ambiguity.deleted_knowledge` 指向 KB 条目 id），可构造**最小差异配对**：同一清楚问题 + 完整 KB vs 删去该条目的 KB | 知识库里的定义与计算公式（例如 SNQI 的计算式），826 条关键歧义另有类型标注（knowledge_linking 368、intent 171、schema_linking 157、semantic 111…） | 数据库是新建的（alien、archeology、polar 等 18 个），与 HiL 的 BIRD dev 数据库不重叠。公开版的 `sol_sql` 与 test case 为空（300 题全空），不能评任务成功率，但提取只需 prompt 级读出。KB 与 schema 是文本，prompt 级读出不需要 PostgreSQL |
| BIRD 训练集 evidence（自建） | 同题带／不带 evidence，只删一段 | 定义与口径 | 官方 train.zip 8.9 GB（含数据库）；evidence 字段格式与必要性筛选待核实。HF 上找到的镜像（567-labs）只有 question／sql，没有 evidence |
| QuestBench GSM-Q／GSME-Q（DeepMind，Apache-2.0，仓库已核实） | 恰好缺一个变量，有完整版 | 数学题里的数值 | 仓库只有生成脚本，数据位置与是否逐题配对待核实；缺失类型与 HiL 不同，适合作泛化检验 |
| CLARITI | 原 issue vs 删信息的改写版 | 实现细节、预期行为 | 改写混杂同 When2Call；数据位置待核实 |

### 已有工作的设置（2026-11-16 阅读，Google Doc Q01 tab 前三篇）

| 论文 | 对比怎么构造 | 表征与干预 | 评价 | 对我们的启示 |
|---|---|---|---|---|
| Sparse Neurons（EMNLP 2025，arXiv 2509.13664 全文） | AmbigQA：原始歧义问题 vs 标注者的消歧改写；SituatedQA：去掉时间／地点 vs 补上。基本是"插入一段消歧词"的近最小差异配对。每类 400 训练、1000 测试 | prefill 阶段所有 prompt token 在固定层的均值，logistic probe；按 probe 权重取 top-k 维（1–3 个神经元即可）。steering 向量 = "歧义且模型弃答"的 100 条 vs "清楚问题"的 100 条，均值中心化后取 PCA 第一主成分，输入后加后缀；只施加在原本直接回答的歧义题上 | 弃答率（GPT-4.1 三分类判定）；跨数据集迁移；TriviaQA 上分类器的误报；已弃答样本的一致性；反向 steering | ① probe 在第 5 层前就饱和，提示可能读到的是表面差异（清楚版多几个词），我们的配对必须控制长度与词面：加"等长但无关"的对照段落。② steering 向量把"歧义"和"弃答行为"混在一起（正类是弃答的歧义题，负类是清楚题），这正是用户笔记指出的问题；我们应把 v_miss（条件对比、行为固定）与 v_ask（同一条件下行为不同）分开提取。③ 它没有测 steering 对清楚问题的过度弃答，只测了分类器误报；我们要测 |
| ClarifySAE（ICLR 2026 workshop；全文未能获取，依据用户笔记） | 歧义 prompt | 用疑问词词表（what／which 等）和 unembedding 投影筛 SAE 特征（ClarifyScore），再 steering | KnowNo，Ask-F1 | 按"输出像不像提问"选特征，选到的是问句形式而不是"该不该问"的决策；提问率上升但 Ask-F1 下降，强度越大越差。所以评价必须同时有提问精度与无缺失时的提问率，不能只看提问率 |
| SAGE-Agent（Findings of ACL 2026，arXiv 2511.08798 全文） | ClarifyBench：同一个真实工具调用派生出 explicit（信息完整）、ambiguous（随机遮去至多 3 个参数后由 GPT-4o 重写问题，人工校验）、infeasible（规则构造会报错的调用）三类；来源 DocPilot 与 BFCL-v3，5 个领域；模拟用户持有真实意图 | 不是表征方法：让 LLM 列出候选工具调用，未知参数写成 `<UNK>`，按参数域的大小算结构化不确定性，用 EVPI 选问题。基线有 ReAct + `ask_question()` 工具（与我们的 ask 工具设定相同）、ProCOT、Active Task Disambiguation；模型为 GPT-4o 与 Qwen2.5-14B，另在 When2Call 上用 GRPO 训练 Qwen2.5-3B／7B | Coverage、工具匹配率、参数匹配率、每题提问数 | ① "列出候选调用并把未知参数标成 `<UNK>`"是一个**不依赖提问行为的识别读出**：可以作为 v_miss probe 的行为标签，把"识别"与"行动"分开（H2）。论文里的 heuristic 版（只看 `<UNK>` 就问）已拿到大部分收益。② explicit／ambiguous／infeasible 三分法正好对应我们的无缺失对照、缺信息、缺能力（Q04 一侧）。③ ambiguous 版仍是 LLM 重写，配对不是最小差异 |

由此对"纯净"设定的修正：

- v_miss 配对除了"有／无那段信息"，还要加第三个版本：**换成同库另一题的无关 evidence**（长度相近、内容无关），排除"多了一段文字"本身的效应。Sparse Neurons 的浅层饱和说明这一点不是可选项。
- 识别标签：SAGE 的 `<UNK>` 做法只适用于工具参数；我们的 blocker（定义、口径、阈值、业务规则）常常超出工具本身，所以不采用（用户判断，2026-11-16）。识别侧先用 Sparse Neurons 式的 probe 作为与已有工作可比的读出，见 [is-ambiguity-probe](studies/ambiguity-neuron-probe.md)。
- v_ask 只在"缺失固定"的输入上对比行为（同一输入多次采样，问 vs 不问），不再用"缺失且提问" vs "完整"这种混合对比。
- 评价 steering 时同时报：缺失时的提问率、提问是否指向缺失项、完整时的提问率（过度提问）。
- 在 Qwen3.5-9B 上复现 Sparse Neurons 的 probe（原作者代码已找到并核对），作为与已有工作可比的基线和流程检查：[is-ambiguity-probe](studies/ambiguity-neuron-probe.md)。

当前倾向（2026-11-16，待用户确认）：v_miss 与 v_ask 的主提取设定用 BIRD train（9428 题，8783 题有 evidence，69 个数据库，与 HiL 的 8 个库无交集；`train.json`／`train_tables.json` 已取到 `${PV_WORK}/external/bird-train/`，未下载数据库）。evidence 需先分类（公式／定义、阈值／常量、取值映射、复述题面），只有前两类作缺失正例，后两类作"删了也不缺"的特异性对照。BIRD-INTERACT LITE 的删知识库条目配对作第二来源；QuestBench GSM-Q 作缺失类型的泛化检验。
4. 闭源或大模型轨迹的 SWE 重放只作为"迁移到难任务"的 teacher-forced 小节，不作主实验。
5. 机理分析（attention head、稀疏维度）在得到稳定行为效应之后。

下面两项是计划中的 study，提交作业前各自在 run_registry.json 登记并建立 study 文件；在此之前只在本节维护。

### 计划：When2Call 提取（拟用 ID `is-when2call-extraction`）

- **问题**：单轮成对数据上得到的 v_miss／v_ask 方向，能否迁移到 HiL SQL 的决策点（H5）。
- **数据**：When2Call 多选测试集，1,062 个源问题各有 tool-call、follow-up（缺一个必需参数）、cannot-answer 版本；CC BY 4.0（dataset card，待核实）。按源问题划分 train／dev／test。
- **采集**：与 HiL 相同的模型、thinking 设置和位置键（单轮下为 `pre`、`think_end`、`act_first`、`think_mean`、`input_mean`），全部层。每题另存四个选项的 log-prob 和一次自由生成的行为标签（调用／追问／拒答／直接回答）。
- **对比**：follow-up 版 vs tool-call 版 → v_miss 类方向；缺参数时追问 vs 直接调用 → v_ask 类方向。
- **复用**：`capture.py` 与 `probe_analysis.py`；只需新增数据载入与单轮入口。约 3.6k 条单轮前向，预计不到 1 GPU 小时。
- **产出**：方向 bundle（raw 与 unit、层号 1 起、hash），供 HiL 决策点上的迁移 AUC 和之后的单步扫描使用。
- **限制**：缺失项是 prompt 中可见的工具参数，不是执行中才出现的 blocker；只用于提取与选层，不作 agent 结论。

### 计划：CLARITI 提问步骤（拟用 ID `is-clariti-ask-step`）

- **问题**：HiL SQL 上的识别／行动结论与 steering 效果，是否在另一任务域（SWE issue 文本）和逐题配对的无 blocker 对照上成立。
- **数据**：500 个 SWE-Bench Verified issue，各有三个删去信息的改写版和原始 issue；数据记录了被隐藏的类别与原文。待核实：数据位置、许可（论文未说明）、隐藏信息字段的格式（混有类别模板，需解析）。
- **改造**：只保留提问步骤，不跑仓库修复。模型读 issue，可调用单一 `ask_user` 工具或声明信息充分并继续。模拟用户用同一个 `ClaudeSimulator`，只依据被隐藏的原文回答。
- **对照**：改写版 vs 原始 issue 逐题配对；原始 issue 上的提问率即过度提问率。
- **指标**：改写版提问率、原始版提问率、问题是否指向被隐藏的信息（Claude 判定）、每题问题数。不报 resolve rate。
- **规模**：先 100 个 issue ×（1 个改写版 + 原始版）。
- **顺序**：数据检查与字段解析可在 HiL 子集运行期间做（不需要 GPU）；采集与 steering 在 HiL 子集回顾之后。
