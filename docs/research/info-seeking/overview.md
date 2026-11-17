# 信息缺失识别与主动获取信息（Q01）：问题、假设与路线

状态（2026-11-17）：HiL SQL 20 题子集与 Sparse Neurons probe 复现已完成，v_miss 的提取来源待定（见"提取来源"）。文献与 benchmark 表在 Google Doc 的 "Q01 Clarification & Q04 Authorization" tab；本文件只维护假设、变体目录和下一步，设置与结果在各 study 中：[is-hil-sql-pilot](studies/hil-sql-pilot.md)、[is-ambiguity-probe](studies/ambiguity-neuron-probe.md)、[is-when2call-extraction](studies/when2call-extraction.md)（暂停）。

## 研究问题

Agent 在执行中遇到 blocker（缺失、歧义、矛盾信息）时：

1. **识别（recognition）**：内部表征是否编码"当前有未解决的 blocker"（v_miss）。
2. **行动（action）**：识别后是否去获取信息（提问；之后扩展到检索）而不是猜测推进（v_ask）。
3. **控制**：能否用 steering 提高该问时的提问率，同时不增加不该问时的提问。

定位：已有表征／steering 工作集中在单轮 QA 的 ambiguity 与 answerability；agent 循环中带"已解决"对照、分开报告识别与行动的 steering 结果尚未见到（摘要级检索，未穷尽）。最接近的先例 Heading-Specific Activation Steering（AskUser 向量）需精读后确认差异。

## 每个 blocker 的漏斗（2026-11-17）

行为侧按 blocker 看四步：① 有没有意识到（识别，对应 v_miss）→ ② 意识到之后的行动：问人、自己查（知识库或数据）、还是猜（按字面或自定默认）（行动，对应 v_ask／v_guess）→ ③ 有没有拿到信息 → ④ 最终 SQL 是否按答案实现。研究的核心在①与②之间（识别了但不行动）；③④是结果端的度量，用来说明问和查的价值，不替代①。实现见 `hil_sql_pilot.py` 的 `annotate`（逐步识别与拍板依据）、`kb-map`（知识库里哪些条目写有答案，按题保存可复用）与 `blocker-outcomes`（逐 blocker 汇总漏斗与正确率）。full-info 条件下答案已给，①不适用，只作对照。

## 假设

| ID | 假设 | 支持的观察 | 反驳的观察 |
|---|---|---|---|
| H1 | 决策点的残差流线性可读出"存在未解决 blocker" | 轨迹内（回答前 vs 回答后）与条件间（blocked vs full-info）的 probe AUC 都明显高于打乱标签和填充文本对照 | 只在条件间可分、轨迹内不可分（说明读到的是 prompt 表面差异） |
| H2 | 8B 模型的欠提问主要是行动失败而非识别失败 | 未提问的 blocker 决策点上 probe 分数仍高 | 未提问时 probe 分数与 full-info 无差别（识别失败） |
| H3 | v_ask 与 v_miss 是不同方向；无条件加 v_ask 会在 full-info 条件下也提高提问 | 余弦相似度低；无条件 steering 使 precision 下降，probe 门控后不下降 | 两者近似共线，或无条件 steering 不引起过度提问 |
| H4 | 最佳读取位置／层与最佳写入位置／层不同 | 离线 AUC 排序与单步 ΔP(ask) 排序不一致 | 两种排序给出同一层 |
| H5 | 从其他领域的成对数据提取的方向可迁移到 HiL SQL | 留出领域与 HiL 决策点上的 AUC、单步 ΔP(ask) 接近本域方向 | 迁移后接近随机方向 |
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
- G1 严格判定：论文的判定 prompt，判定模型用 Claude Haiku（论文为 Llama-3.3-70B）。只接受 32% 的 registry 示例问题，改为离线重判用。
- G2 宽松判定（"一个愿意帮忙的人会不会给出该 resolution"）：闭环默认（2026-11-16 用户决定）。分数标为"Claude 判定"，不称官方 HiL-Bench 分数。

**H. 对照条件**
- H1 full-info 且开启 ask_human：过度提问率。
- H2 部分解决：只放回一部分 resolution，检查 probe 分数是否随剩余 blocker 数变化。
- H3 填充对照：blocked 条件加入与 resolution 等长的无关业务文本，排除长度与位置解释。

## 路线

1. [is-hil-sql-pilot](studies/hil-sql-pilot.md)：完成 20 题子集。HiL 定位为验证集：blocked 条件内几乎所有 blocker 都被意识到，缺少"没意识到"的负例；KB 不含完整答案，评不了自行检索。
2. [is-ambiguity-probe](studies/ambiguity-neuron-probe.md)：完成。原文的稀疏神经元是长度伪影；只作与已有工作可比的基线。
3. v_miss 的提取来源：[When2Call](studies/when2call-extraction.md) 已实现但暂停（缺的是可见的工具参数，且缺参数版整句改写）。新方案见下方"提取来源"。

### 提取来源（2026-11-17 讨论，待用户确认）

**为什么不只用 SQL**：提取和验证都在 SQL 上，就分不清方向读到的是通用的"缺信息"，还是"SQL 题里有个没定义的业务词"。所以把领域作为变量：至少三个领域分别提取，留一个领域做测试，HiL 只作最终验证。

**对配对的要求（用户追问后修正）**：不要求逐字相同，只要求两组之间除了 blocker 没有**系统性**差别。随机的噪声（题目内容、长度在题与题之间变化）会在均值差里抵消，多样性反而有利于泛化。跟条件绑定的差别才是问题：例如 CLARITI 的缺失版全是 GPT 重写的文风，原 issue 全是人写的，均值差里就会混进"文风"。处理办法：
1. 文风对齐：例如让 LLM 把原 issue 用同样文风重写一遍、不删任何信息，作为对照。
2. 多来源交叉：各来源的伪影不同，只保留共有的方向。
3. 留出领域检验：方向在没参与提取的领域和 HiL 上仍有效，就说明噪声没有起作用。
4. 等长无关文本对照保留，作为检查"多一段文字"效应的最便宜手段，不作硬性要求。

**候选**：SQL 用 BIRD-INTERACT LITE（删 KB 条目），数学用 QuestBench GSM-Q（筛过的干净删除对），代码用 CLARITI（文风对齐的完整版作对照）；BFCL 的纯删除对作工具调用领域的小检验集。下表为 2026-11-16／17 核对结果，已下载核对的标"已核实"。

| 候选 | 配对 | 缺失类型 | 现状 |
|---|---|---|---|
| **BIRD-INTERACT LITE**（HF `birdsql/bird-interact-lite`，CC BY-SA 4.0，已核实） | 300 题；每题有清楚版 `query` 与歧义版 `amb_user_query`（改写，300 题全部不同）；另有 265 条"被删除的知识库条目"标注（`knowledge_ambiguity.deleted_knowledge` 指向 KB 条目 id），可构造**最小差异配对**：同一清楚问题 + 完整 KB vs 删去该条目的 KB | 知识库里的定义与计算公式（例如 SNQI 的计算式），826 条关键歧义另有类型标注（knowledge_linking 368、intent 171、schema_linking 157、semantic 111…） | 数据库是新建的（alien、archeology、polar 等 18 个），与 HiL 的 BIRD dev 数据库不重叠。公开版的 `sol_sql` 与 test case 为空（300 题全空），不能评任务成功率，但提取只需 prompt 级读出。KB 与 schema 是文本，prompt 级读出不需要 PostgreSQL |
| BIRD 训练集 evidence（自建） | 同题带／不带 evidence，只删一段 | 定义与口径 | 官方 train.zip 8.9 GB（含数据库）；evidence 字段格式与必要性筛选待核实。HF 上找到的镜像（567-labs）只有 question／sql，没有 evidence |
| QuestBench GSM-Q／GSME-Q（DeepMind；代码 Apache-2.0，数据 CC-BY 4.0；GSM-Q 原题来自 GSM-Plus，CC-BY-SA 4.0；2026-11-17 已核实，数据在 `${PV_WORK}/external/questbench/`） | 逐题配对：GSME-Q 在同一行（`Full Problem` vs `Rewritten Problem`）；GSM-Q 的完整版不在文件里，按 `Question ID` 从 GSM-Plus test 取回（答案 100% 对上）。但多数行除了删必需变量，还删掉了干扰变量的数值；只删必需变量的行：GSM-Q 约 1799／23642（758 道原题，按 `Heldout Constraint` 只有一行近似，未逐条核对），GSME-Q 536／6591。GSM-Q 为人工编辑，词改动中位数 7 个 | 数学题里的一个数值；缺失变量、取值与描述都有标注 | 数学领域的提取源，只用筛过的干净删除对。一题派生几十行，需去重或配平。GSME-Q 是符号形式，离自然语言太远。Logic-Q／Planning-Q 没有配对版本 |
| CLARITI（repo `sani903/Teaching-Effective-Clarification` 的 `data/data.xlsx`；只有仓库的 MIT 许可，无数据许可；2026-11-17 已核实，数据在 `${PV_WORK}/external/clariti/`） | 500 个 issue × 3 个改写，但改写是整篇重写：相似度中位数 0.20，约 30% 比原文长，还会加入原文没有的内容。不能当最小差异配对 | 报错信息、复现步骤、预期行为等，外加一个未命名的"代码位置"类（533 个变体） | 可以自建删除版：`hidden_info` 里被删的原文片段有 84% 能在原 issue 里逐字找到，可以从原文删掉这些片段。约 16% 的片段来自 gold patch 或测试文件，要剔除。`hidden_categories_k` 字段不可靠，应解析 `hidden_info`。Ambig-SWE（`cmu-lti/interactive-swe`）的缺失版是 LLM 摘要，相似度 0.19，也没有被删内容的字段，不采用 |
| BFCL multi_turn_miss_param + arXiv 2610.04429 配对（Apache-2.0；2026-11-17 已核实，数据在 `${PV_WORK}/external/bfcl/`） | 论文 223 对中只有 107 对是 miss_param（另 116 对是 miss_func）；发布的只有 id 与锚点轮，题目文本要从 BFCL V4 文件拼，id 一一对齐。198 条里只有 54 条是纯删除（其中 33 条在论文的 107 对里），142 条是把值换成含糊说法（如 "one of the file"、"several"） | 工具参数的具体值 | 只作工具调用领域的小检验集：用 54 条纯删除，在锚点轮截断、去掉揭示轮 |

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

BIRD train（9428 题，8783 题有 evidence，`${PV_WORK}/external/bird-train/`）原是 SQL 领域的首选；改为多领域方案后作为备选。它的 evidence 多数是复述题面或字段映射，真正缺阈值或定义的需要先分类筛出（简单正则只找到 39 条形如 "elderly refers to age > 65" 的阈值定义）。

4. 闭源或大模型轨迹的 SWE 重放只作为"迁移到难任务"的 teacher-forced 小节，不作主实验。
5. 机理分析（attention head、稀疏维度）在得到稳定行为效应之后。

下面的计划 study 在提交作业前于 run_registry.json 登记并建立 study 文件；在此之前只在本节维护。

### 后续候选：用 persona 方向改变识别与提问（2026-11-17 讨论，靠后）

想法（用户提出）：沿用原 Persona Vectors 的设置（system prompt 里给出某种人格的正向与反向描述，生成大量与该人格相关的单轮对话，再取正负均值差），提取人格方向，看用它 steer 能否让模型意识到更多 blocker、更早意识到，或更愿意提问。待定的是"哪种人格"：候选有尽责／谨慎（Conscientiousness）、好奇（Openness）、合作／愿意征询（Agreeableness），以及"承认不确定"（不属于大五，需自定义）；反向为果断、自信、独立行事。

草稿与未决问题（2026-11-17）：草拟了两个自定义人格，P1 `gap-aware`（意识到并说明缺失，反向为默默假设）与 P2 `consultative`（缺信息时先问，反向为从不询问），外加大五 Conscientiousness 作对照；题目要求为"真实但缺关键信息的请求"。用户的疑虑：P1、P2 已超出"人格"的范畴，更像具体行为，是否还适合用 Chen et al. 的人格提取办法；而且要 Claude 生成带各种 gap 的题目，质量难以保证。先记录，之后再讨论。

参考：Bhandari, Naseem, Nasim, *Geometric dependence of Big Five personality steering directions*（arXiv 2602.15847，2026-01，阅读 HTML 全文）。
- 设置：LLaMA-3-8B-Instruct 与 Ministral-8B-Instruct；方向从带高／低标注的人格数据（Li et al. 2025）在各层估计，再加权合成单一方向；层的选择沿用作者此前的混合策略（Bhandari et al. 2026：离线用中性 prompt 测下一 token 分布对小扰动的敏感度选先验层，运行时再按输入动态调整）；评价用访谈式 BFI 问卷，GPT-4o-mini 判分（1–5），另报流畅度。
- 结论：五个特质方向在几何上不独立，推一个特质会带动其他特质（例如推 Openness，Agreeableness、Conscientiousness、Extraversion 上升，Neuroticism 下降），作者解释为沿一条更宽的"社交"轴移动；强制正交化（Gram-Schmidt、对称白化等 C1–C5）能让余弦接近 0，但行为上的串扰不消失，且流畅度下降。Neuroticism 在 LLaMA-3 上可被强烈 steer，在 Ministral 上几乎无反应。
- 未见代码或向量发布；模型与我们的 Qwen3.5-9B 不同，向量不能直接用，只能按其方法在我们的模型上重提。
- 对我们的含义：若用人格方向去 steer 提问，评价必须同时看副作用（过度提问、任务成功率、回复风格），并预期会有跨特质串扰；与其直接用大五，不如在仓库已有的 Persona Vectors 提取流程（E01）上，自定义一到两个与"信息寻求"直接相关的人格。

### 计划：CLARITI 提问步骤（拟用 ID `is-clariti-ask-step`）

- **问题**：HiL SQL 上的识别／行动结论与 steering 效果，是否在另一任务域（SWE issue 文本）和逐题配对的无 blocker 对照上成立。
- **数据**（2026-11-17 已核实，见上方"提取来源"表）：500 个 SWE-Bench Verified issue，各有三个改写版和原始 issue，记录了被隐藏的类别与原文片段。改写是整篇重写，需要文风对齐的对照；`hidden_categories_k` 不可靠，应解析 `hidden_info_k`；约 16% 的片段来自 gold patch 或测试文件，要剔除。只有仓库的 MIT 许可，没有数据许可。
- **改造**：只保留提问步骤，不跑仓库修复。模型读 issue，可调用单一 `ask_user` 工具或声明信息充分并继续。模拟用户用同一个 `ClaudeSimulator`，只依据被隐藏的原文回答。
- **对照**：改写版 vs 同文风重写的完整版（主对照），另报原始 issue；完整版上的提问率即过度提问率。
- **指标**：改写版提问率、原始版提问率、问题是否指向被隐藏的信息（Claude 判定）、每题问题数。不报 resolve rate。
- **规模**：先 100 个 issue ×（1 个改写版 + 原始版）。
- **顺序**：先等提取来源方案确认。
