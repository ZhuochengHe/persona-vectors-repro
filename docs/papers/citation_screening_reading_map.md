# Persona Vectors 被引文献阅读导航

**当前主阅读清单已压缩为[高价值精选30篇（先读10篇）](citation_screening_shortlist.md)。本文保留第一轮宽口径结果，不再作为逐篇必读清单。**

更新：2026-10-30。阶段：完整源列表获取与逐篇标题/摘要初筛完成；九个方向为人工初步聚类，可随全文阅读更新。

[规则基准](citation_screening_rules.md) · [完整工作CSV](citation_screening_working.csv) · [保留集CSV](citation_screening_retained.csv) · [抓取清单及哈希](citation_screening_sources/manifest.json)

## 本批范围与结果

唯一候选来源是种子论文 [2507.21509](https://arxiv.org/abs/2507.21509) 的 [mlsanity直接被引接口](https://mlsanity.com/api/papers/2507.21509/citers?sort=cited&area=all)。获取开始时间：`2026-10-30T20:24:01.677751+00:00`。四页返回总数一致，已保存原始JSON；没有添加主题搜索候选，也没有递归扩展。

- 源列表：376 条，376 个不同 arXiv ID；官方arXiv标题、作者、摘要补齐 376 条。
- 保留 351 条：核心相关 166、问题相关 92、方法参考 93。
- 标题或摘要命中 persona 的 85 条全部保留；另有待定 13 条、排除 12 条，理由均留在工作表。
- 抽查 27 条正文引用关系：24 条在官方HTML定位到种子引用；其余3条HTML未找到，仍仅按源列表记录。未对376条逐一独立核对参考文献。
- 对规范化arXiv ID、完全一致标题和非空DOI做去重检查，没有发现精确重复。C148/C173疑似前作/扩展版，暂保留关联注记；因此376不是已确认的独立研究数。
- 这是mlsanity这一来源的完整快照，不代表Google Scholar、Semantic Scholar等所有数据库的完整并集。

筛选采用宽口径，目的是帮助发现研究问题；用户画像、社会模拟、哲学理论等不会因偏离现有实验被自动排除。论文的经验性主张目前大多依据作者摘要，未完成方法、数据和统计可信度审计。

## 按方向逐块读

每组提供5篇起步串、延伸列表、全部保留记录。全局P1共45条，只表示起步导航；不需要先读完45篇才选方向。

| 方向 | 主类记录数 | 主要问题 |
|---|---:|---|
| [人格空间与表征](citation_reading_groups/01_persona_space.md) | 42 | 人格、价值和角色究竟是单方向、子空间，还是弯曲流形？ |
| [情绪与情感行为](citation_reading_groups/02_emotion.md) | 12 | 情绪方向读到的是词语、情境、功能性状态，还是可控制的行为因素？ |
| [人格形成与训练泛化](citation_reading_groups/03_training.md) | 83 | 人格如何形成，为什么窄域数据会改变跨域行为，什么干预可以持久保留？ |
| [多轮人格与角色稳定性](citation_reading_groups/04_dialogue.md) | 16 | 人格如何在持续交互中保持、漂移、切换和恢复？ |
| [控制方法与干预边界](citation_reading_groups/05_control.md) | 71 | 怎样实现组合、动态、精细控制，并识别副作用和方法失效？ |
| [人格测量与行为效度](citation_reading_groups/06_measurement.md) | 33 | 问卷、自报、探针和judge评分，究竟能否预测实际行动？ |
| [社会互动与行为模拟](citation_reading_groups/07_social.md) | 54 | 人格和对他人的表征如何影响合作、决策、用户模拟及社会互动？ |
| [内部监测与模型审计](citation_reading_groups/08_monitoring.md) | 29 | 内部信号能否提前预测行为，并在跨任务、训练和agent流程中保持可靠？ |
| [身份、意识与理论解释](citation_reading_groups/09_identity.md) | 11 | 人格、身份、自我报告和功能性情绪，应当如何解释？ |

## 几组适合并读的分歧

- **人格向量能组合到什么程度**：[PERSONA: Dynamic and Compositional Inference-Time Personality Control via Activation Vector Algebra](https://arxiv.org/abs/2602.15669)（PV-C037） → [Do Personality Traits Interfere? Geometric Limitations of Steering in Large Language Models](https://arxiv.org/abs/2602.15847)（PV-C104） → [Steering Interference Reflects the Model's Defaults, Not the Behavior Directions](https://arxiv.org/abs/2609.06951)（PV-C310） → [PersonaManifold: Revealing and Exploiting Curved Geometry in LLM Persona Representations](https://arxiv.org/abs/2609.34571)（PV-C334）。对照向量代数、trait干扰、模型默认倾向与曲面几何，避免只看其中一种解释。
- **失配是人格招募、身份失稳还是数据泛化**：[Emergent Misalignment Recruits a Pre-existing Persona Subspace](https://arxiv.org/abs/2607.21356)（PV-C155） → [Self-Recognition Finetuning can Prevent and Reverse Emergent Misalignment](https://arxiv.org/abs/2606.23700)（PV-C214） → [Emergent Misalignment Is Not Magical](https://arxiv.org/abs/2608.29118)（PV-C303） → [Transplanting, inverting, and preventing a misalignment persona: method-conditional emergent misalignment in Qwen2.5](https://arxiv.org/abs/2607.04510)（PV-C283）。这些摘要提出不同解释，应用范围和对照条件应在全文阅读中逐项比较。
- **可读、可控和自然使用是否一致**：[Linear Personality Probing and Steering in LLMs: A Big Five Study](https://arxiv.org/abs/2512.17639)（PV-C058） → [Detection != Reliable Control: Decodable Empathy Directions Yield at Most Partial Shifts in Automated Empathy Scores](https://arxiv.org/abs/2608.24901)（PV-C300） → [Inverted Detection and Control in Steering Vectors](https://arxiv.org/abs/2608.02957)（PV-C291） → [Does the Model Use the Feature? Separating Steering from Mechanism in LLMs](https://arxiv.org/abs/2610.07270)（PV-C351） → [From Trait Vectors to Circuits: Tracing Refusal and Sycophancy Through Language Models](https://arxiv.org/abs/2609.22224)（PV-C322）。把探针检测、全局干预、自然范围救援和行为回路拆开检验。
- **表达人格是否改变行动**：[The Personality Illusion: Revealing Dissociation Between Self-Reports & Behavior in LLMs](https://arxiv.org/abs/2509.03730)（PV-C010） → [Persona Vectors in Games: Measuring and Steering Strategies via Activation Vectors](https://arxiv.org/abs/2603.21398)（PV-C092） → [Representational Control over Self-Report & Behavior Coherence in LLM Risk-Taking](https://arxiv.org/abs/2610.04125)（PV-C344） → [Jointly Modeling Preferences and Imperfect Decision-Making in Large Language Models](https://arxiv.org/abs/2610.33651)（PV-C376）。同一trait在自陈、文本措辞和博弈决策上的效果可能不同。
- **情绪是什么，又与人格有什么关系**：[Emotion Concepts and their Function in a Large Language Model](https://arxiv.org/abs/2604.07729)（PV-C003） → [Whether, Not Which: Mechanistic Interpretability Reveals Dissociable Affect Reception and Emotion Categorization in LLMs](https://arxiv.org/abs/2603.22295)（PV-C165） → [Functional Emotions or Situational Contexts? A Discriminating Test from the Mythos Preview System Card](https://arxiv.org/abs/2604.13466)（PV-C146） → [Usage-Modulated Sentiment Representations in Large Language Models](https://arxiv.org/abs/2610.05069)（PV-C348） → [Compositional Literary Primitives in Instruction-Tuned LLMs: Cross-Architectural SAE Features for Self, Style, and Affect](https://arxiv.org/abs/2605.18808)（PV-C206）。比较功能性情绪、去关键词验证、情境解释、语用残差与自我语体；不预设共享一个子空间。

## 待定记录

尚缺相关正文的实质性审阅，引用关系查验不等于主题审阅。保留这些记录以防误删。

| 编号 | 论文 | 待核实内容 |
|---|---|---|
| PV-C095 | [RouteHijack: Routing-Aware Attack on Mixture-of-Experts LLMs](https://arxiv.org/abs/2605.02946) | MoE专家定位攻击：需正文判断是否超出特定越狱应用 |
| PV-C112 | [OffTopicEval: When Large Language Models Enter the Wrong Chat, Almost Always!](https://arxiv.org/abs/2509.26495) | 任务范围约束与身份保持可能相关，摘要仅为离题拒绝；需正文 |
| PV-C157 | [Jinx: Unlimited LLMs for Probing Alignment Failures](https://arxiv.org/abs/2508.08243) | helpful-only模型资源；需看与persona分析或控制的实际关系 |
| PV-C159 | [Explainability of Large Language Models: Opportunities and Challenges toward Generating Trustworthy Explanations](https://arxiv.org/abs/2510.17256) | 广义解释性综述；需确认是否包含可用人格或行为控制分析 |
| PV-C193 | [Frontier AI Risk Management Framework in Practice: A Risk Analysis Technical Report v1.5](https://arxiv.org/abs/2602.14457) | 广泛风险报告含失配与agent记忆演化；相关章节需正文 |
| PV-C235 | [Similarity Field Theory: A Mathematical Framework for Intelligence](https://arxiv.org/abs/2509.18218) | 广义相似度理论与安全概念，需正文确认persona相关实质 |
| PV-C238 | [The Realignment Problem: When Right becomes Wrong in LLMs](https://arxiv.org/abs/2511.02623) | 变动政策的重对齐框架；需正文判断是否有独立行为trait分析 |
| PV-C278 | [AOR-Bench: Do Large Audio Language Models Over-Refuse Pseudo-Harmful Queries?](https://arxiv.org/abs/2606.21147) | 音频过度拒绝benchmark；需查steering是否提供通用洞见 |
| PV-C284 | [LLMs Silently Correct African American English: Auditing and Mitigating Dialect Bias via Activation Steering](https://arxiv.org/abs/2607.06845) | 方言偏见的特定steering应用；需正文判断人格身份联系 |
| PV-C289 | [Unlearning Under Imbalance: Benchmarking Fairness in Multimodal LLM Unlearning](https://arxiv.org/abs/2607.21300) | 多模态遗忘公平性中的偏见steering，需正文判断通用方法联系 |
| PV-C307 | [Role differentiation as ignition of a collective information engine: Structuration in Agent Populations](https://arxiv.org/abs/2609.05442) | 角色分化与身份持续的群体理论；需核对与LLM persona的实质联系 |
| PV-C327 | [CG-Probes: Recovering Guardrail Directions from Patient Query Embeddings](https://arxiv.org/abs/2609.31062) | 患者心理紧迫性查询embedding，需区分语义风险检测与情绪机制 |
| PV-C338 | [From cacophony to hierarchy: a principled framework for assessing AI consciousness](https://arxiv.org/abs/2609.35618) | 广义意识评估层级综述，需正文核实persona或情绪实质 |

## 排除记录

全部未命中persona硬规则。以后若补充材料改变判断，可从工作表恢复。

| 编号 | 论文 | 理由 |
|---|---|---|
| PV-C056 | [Human-like Content Analysis for Generative AI with Language-Grounded Sparse Encoders](https://arxiv.org/abs/2508.18236) | 图像内容分解与物理合理性评估；摘要未建立人格情绪或行为控制联系 |
| PV-C070 | [Activation Steering for Accent-Neutralized Zero-Shot Text-To-Speech](https://arxiv.org/abs/2603.05977) | TTS口音中和与音色保持，未涉及人格情绪或独立通用方法问题 |
| PV-C111 | [Explainable Knowledge Graph Retrieval-Augmented Generation (KG-RAG) with KG-SMILE](https://arxiv.org/abs/2509.03626) | KG-RAG图归因解释，摘要无人格情绪或激活行为控制方法联系 |
| PV-C113 | [Memory Retrieval and Consolidation in Large Language Models through Function Tokens](https://arxiv.org/abs/2510.08203) | function token知识检索和记忆理论，未研究人格情绪或相关干预 |
| PV-C122 | [TADA! Tuning Audio Diffusion Models through Activation Steering](https://arxiv.org/abs/2602.11910) | 音频扩散中的乐器与风格控制，主题不是人格或情绪 |
| PV-C150 | [Task-Focused Memorization for Multimodal Agents](https://arxiv.org/abs/2605.31075) | 视频多模态记忆的任务奖励学习；无相关人格情绪或通用steering问题 |
| PV-C164 | [Inference-Time Toxicity Mitigation in Protein Language Models](https://arxiv.org/abs/2603.04045) | 蛋白质毒性生成的logit控制，毒性不是人格trait |
| PV-C187 | [A Criminology of Machines](https://arxiv.org/abs/2511.02895) | 机器犯罪学与治理理论，摘要未提供人格情绪或相关机制问题 |
| PV-C200 | [Embedding Arithmetic: A Lightweight, Tuning-Free Framework for Post-hoc Bias Mitigation in Text-to-Image Models](https://arxiv.org/abs/2604.18167) | 文本生图人口偏见缓解，无人格情绪且方法目标偏图像语义保持 |
| PV-C218 | [The Sound of Absence: Audio-Language Embedding Models Struggle with Negation](https://arxiv.org/abs/2607.12290) | 音频语言embedding否定识别，steering只是特定修复 |
| PV-C248 | [How to Take a Memorable Picture? Empowering Users with Actionable Feedback](https://arxiv.org/abs/2602.21877) | 图像记忆度摄影建议，steering仅用于特定视觉任务 |
| PV-C276 | [XtrAIn: Training-Guided Occlusion for Feature Attribution](https://arxiv.org/abs/2606.10877) | 图像和乳腺癌特征归因，无相关人格情绪或行为控制联系 |

## 工作约定与复现

- 筛选状态、三档相关性、主类和阅读优先级互相独立。交叉标签是词项辅助，不是自动排除器。
- `method` 和 `research_question` 字段暂留给后续全文笔记；当前逐篇判断在 `decision_reason`，研究方向的问题在分组导航。
- 原始抓取见 `scripts/collect_persona_citations.py`，其保护逻辑禁止覆盖已有快照。
- 逐篇人工决策保存于 `citation_screening_sources/review_decisions.json`，分组起步串保存于 `reading_group_specs.json`。
- `python scripts/render_persona_citation_review.py` 从这些决策重建工作表和导航；若直接修改CSV，请先同步决策源文件，以免重建覆盖。
- 下阶段优先完成13条边界案例、疑似扩展版核对，以及所选方向的全文阅读；更新判断时保留证据位置和版本。
