# Persona Vectors：高价值精选阅读

更新：2026-10-30。第二轮已将351篇主题相关记录压缩为30篇主阅读清单：A档10篇先读，B档20篇按方向读。

[精选CSV](citation_screening_shortlist.csv) · [完整工作表](citation_screening_working.csv) · [第二轮全部去向](citation_screening_round2_audit.csv) · [规则基准](citation_screening_rules.md) · [第一轮宽口径导航](citation_screening_reading_map.md)

## 这轮怎样筛

第一轮把“相关”当成了保留条件，不能直接当精读推荐。这轮优先具体的新问题、新机制、重要反例和可复用的研究范式，并用署名机构、公司参与及会议作辅助信号。纯应用迁移、外围综述和相近方法框架优先延后。即使来自名校或已中顶会，也不自动入选。

- 所有30篇仍来自原文的376条直接被引快照，没有主题搜索补入其他论文。
- 对43篇候选核查官方HTML署名及贡献／讨论／局限片段；不是43篇全文方法审计。30篇入选，13篇重点候选延后，其余308篇第一轮保留记录未进一步作贡献高低定论。
- 精选中11篇已由官方会议录核实主会。其他按公司报告、作者自报、workshop记录或未核实标注；未把在审或workshop写成顶会主会。
- persona命中仍留在总清单，不能自动进入精选。未入选不等于已证明无贡献。
- 排名和入选判断属于本轮编辑判断；“限制／阅读提醒”可能是作者明确局限，也可能是据证据范围提出的核对点，不是论文质量评分。

## 先读这10篇

按下列顺序形成问题地图，再决定深入哪个方向；不需要一次读完后面的20篇。

| 顺序 | 论文 | 机构／发表信号 | 为什么先读 |
|---|---|---|---|
| 1 | [The Assistant Axis: Situating and Stabilizing the Default Persona of Language Models](https://arxiv.org/abs/2601.10387)（PV-C001） | [Anthropic；Oxford；MATS](https://arxiv.org/html/2601.10387)；[ICML 2026 主会](https://proceedings.mlr.press/v306/lu26g.html) | 把默认Assistant定位为人格空间的主轴，并研究自然对话漂移和条件性稳定。 |
| 2 | [Emotion Concepts and their Function in a Large Language Model](https://arxiv.org/abs/2604.07729)（PV-C003） | [Anthropic](https://arxiv.org/html/2604.07729)；[Anthropic研究报告；主会未核实](https://www.anthropic.com/research/emotion-concepts-function) | 将情绪从输出语气推进到内部概念的跨情境表征和因果行为作用。 |
| 3 | [The Personality Illusion: Revealing Dissociation Between Self-Reports & Behavior in LLMs](https://arxiv.org/abs/2509.03730)（PV-C010） | [Caltech；UIUC；Cambridge](https://arxiv.org/html/2509.03730)；[ICML 2026 主会](https://proceedings.mlr.press/v306/han26n.html) | 直接挑战人格问卷分数可代表实际行为的默认假设。 |
| 4 | [Open Character Training: Shaping the Persona of AI Assistants through Constitutional AI](https://arxiv.org/abs/2511.01689)（PV-C017） | [Cambridge；AI2；Anthropic；MATS](https://arxiv.org/html/2511.01689)；预印本；主会未核实 | 开放character training及训练数据、模型和揭示偏好评估，给出提示/steering之外的路线。 |
| 5 | [PERSONA: Dynamic and Compositional Inference-Time Personality Control via Activation Vector Algebra](https://arxiv.org/abs/2602.15669)（PV-C037） | [哈尔滨工业大学；香港大学](https://arxiv.org/html/2602.15669)；[ICLR 2026 主会](https://proceedings.iclr.cc/paper_files/paper/2026/hash/f66ce276436c4cd151535b03841ac713-Abstract-Conference.html) | 把人格控制组织为trait向量代数和上下文动态组合，提供可复用范式。 |
| 6 | [Tracing Persona Vectors Through LLM Pretraining](https://arxiv.org/abs/2605.13329)（PV-C063） | [EPFL](https://arxiv.org/html/2605.13329)；预印本；主会未核实 | 沿预训练checkpoint追踪persona方向，回答它何时出现及怎样演化。 |
| 7 | [Probing Persona-Dependent Preferences in Language Models](https://arxiv.org/abs/2605.13339)（PV-C127） | [ETH Zürich；EPFL；MATS；Eleos AI Research](https://arxiv.org/html/2605.13339)；[NeurIPS接收：arXiv作者自报，未独立确认](https://arxiv.org/abs/2605.13339) | 检验不同persona是否共享偏好机制，以revealed choice及跨persona因果迁移连接人格和决策。 |
| 8 | [Manifold Steering Reveals the Shared Geometry of Neural Network Representation and Behavior](https://arxiv.org/abs/2605.05115)（PV-C014） | [Goodfire；Stanford；UCL；Harvard等](https://arxiv.org/html/2605.05115)；预印本；主会未核实 | 同时研究表征流形和行为流形，把steering从找方向改为尊重几何。 |
| 9 | [Reasoning Models Generate Societies of Thought](https://arxiv.org/abs/2601.10825)（PV-C043） | [Google；University of Chicago；Santa Fe Institute](https://arxiv.org/html/2601.10825)；预印本；主会未核实 | 把推理中的多视角、冲突和社会情绪角色作为性能来源，连接persona与reasoning。 |
| 10 | [Representational Control over Self-Report & Behavior Coherence in LLM Risk-Taking](https://arxiv.org/abs/2610.04125)（PV-C344） | [Caltech；CMU；UIUC；Cambridge](https://arxiv.org/html/2610.04125)；预印本；主会未核实 | 将自报—行动脱节推进到内部干预：不同方向可分别控制并反向组合两种响应。 |

## 按方向读精选30篇

A/B不是质量等级：A适合先建立问题地图，B适合进入专题后再读。

### 人格空间与起源（6篇）

人格是什么结构，又从什么时候出现？

| 论文 | 机构／发表 | 独立贡献 | 限制／阅读提醒 |
|---|---|---|---|
| **A** [The Assistant Axis: Situating and Stabilizing the Default Persona of Language Models](https://arxiv.org/abs/2601.10387)（PV-C001） | [Anthropic；Oxford；MATS](https://arxiv.org/html/2601.10387)；[ICML 2026 主会](https://proceedings.mlr.press/v306/lu26g.html) | 把默认Assistant定位为人格空间的主轴，并研究自然对话漂移和条件性稳定。 | 三种开放dense非推理设置；角色覆盖和模糊行为评分仍有限。 |
| **A** [Tracing Persona Vectors Through LLM Pretraining](https://arxiv.org/abs/2605.13329)（PV-C063） | [EPFL](https://arxiv.org/html/2605.13329)；预印本；主会未核实 | 沿预训练checkpoint追踪persona方向，回答它何时出现及怎样演化。 | 主要为OLMo-3和Apertus；不同提取策略揭示不同trait侧面。 |
| **A** [Manifold Steering Reveals the Shared Geometry of Neural Network Representation and Behavior](https://arxiv.org/abs/2605.05115)（PV-C014） | [Goodfire；Stanford；UCL；Harvard等](https://arxiv.org/html/2605.05115)；预印本；主会未核实 | 同时研究表征流形和行为流形，把steering从找方向改为尊重几何。 | 关键实验为几何可定义的简化任务，不能直接当作复杂persona有效性的证明。 |
| **B** [Your Language Model Secretly Contains Personality Subnetworks](https://arxiv.org/abs/2602.07164)（PV-C103） | [Northwestern；University of Tulsa；University of Arizona](https://arxiv.org/html/2602.07164)；[ICLR 2026 主会](https://proceedings.iclr.cc/paper_files/paper/2026/hash/9b2086bc4a12c3a8e80105635fd95f66-Abstract-Conference.html) | 用对比剪枝寻找预存persona子网络，为人格提供方向之外的参数结构视角。 | 能隔离可控子网络不等于找到唯一自然人格回路，需关注独立行为验证。 |
| **B** [VALUEFLOW: Toward Pluralistic and Steerable Value-based Alignment in Large Language Models](https://arxiv.org/abs/2602.03160)（PV-C119） | [首尔大学](https://arxiv.org/html/2602.03160)；[ICML 2026 主会；Oral仅arXiv自报](https://proceedings.mlr.press/v306/kim26r.html) | 把价值的层级结构、强度标定和多价值组合接成统一研究框架。 | 评估依赖选定价值理论及强度锚；代表的是价值控制而非所有persona机制。 |
| **B** [Synthetic Persona Pretraining: Alignment from Token Zero](https://arxiv.org/abs/2608.13482)（PV-C180） | [EPFL；University of Toronto；Northeastern等](https://arxiv.org/html/2608.13482)；[主会未核实；有NeurIPS workshop记录](https://openreview.net/search?content=authors&group=all&sort=cdate%3Adesc&source=forum&term=~Julian_Minder1) | 从token zero塑造persona，再绑定Assistant身份，提出区别于纯后训练的对齐路线。 | 实验规模低于frontier；persona binding会被持续训练和abliteration削弱。 |

### 情绪与心理表征（3篇）

情绪是否只是表达语气，还是有独立行为作用？

| 论文 | 机构／发表 | 独立贡献 | 限制／阅读提醒 |
|---|---|---|---|
| **A** [Emotion Concepts and their Function in a Large Language Model](https://arxiv.org/abs/2604.07729)（PV-C003） | [Anthropic](https://arxiv.org/html/2604.07729)；[Anthropic研究报告；主会未核实](https://www.anthropic.com/research/emotion-concepts-function) | 将情绪从输出语气推进到内部概念的跨情境表征和因果行为作用。 | 主要研究Claude Sonnet 4.5；线性探针可能遗漏角色绑定和非线性结构。 |
| **B** [How Emotion Shapes the Behavior of LLMs and Agents: A Mechanistic Study](https://arxiv.org/abs/2604.00005)（PV-C196） | [北京航空航天大学；NTU Singapore](https://arxiv.org/html/2604.00005)；预印本；主会未核实 | 用VAD情绪表征干预同时研究推理、安全和多步agent行动。 | VAD维度并非严格独立；任务进行中的动态情绪尚未充分建模。 |
| **B** [Usage-Modulated Sentiment Representations in Large Language Models](https://arxiv.org/abs/2610.05069)（PV-C348） | [William & Mary](https://arxiv.org/html/2610.05069)；[EMNLP 2026 主会](https://aclanthology.org/2026.emnlp-main.356/) | 固定事件内容后分离情感极性与语气／受众残差，超越单一sentiment轴。 | 生成干预的重点在Llama；推广到持续情绪状态需另证，会议版作者名与arXiv有差异。 |

### 人格、偏好与行动（4篇）

测到人格之后，是否真正改变了选择和行动？

| 论文 | 机构／发表 | 独立贡献 | 限制／阅读提醒 |
|---|---|---|---|
| **A** [The Personality Illusion: Revealing Dissociation Between Self-Reports & Behavior in LLMs](https://arxiv.org/abs/2509.03730)（PV-C010） | [Caltech；UIUC；Cambridge](https://arxiv.org/html/2509.03730)；[ICML 2026 主会](https://proceedings.mlr.press/v306/han26n.html) | 直接挑战人格问卷分数可代表实际行为的默认假设。 | 结果依赖所选心理量表和行为任务；不能把自报失效推广为所有人格表征不存在。 |
| **A** [Probing Persona-Dependent Preferences in Language Models](https://arxiv.org/abs/2605.13339)（PV-C127） | [ETH Zürich；EPFL；MATS；Eleos AI Research](https://arxiv.org/html/2605.13339)；[NeurIPS接收：arXiv作者自报，未独立确认](https://arxiv.org/abs/2605.13339) | 检验不同persona是否共享偏好机制，以revealed choice及跨persona因果迁移连接人格和决策。 | steering因果结果只在Gemma展示；权重级persona与Qwen MoE迁移不稳定。 |
| **A** [Representational Control over Self-Report & Behavior Coherence in LLM Risk-Taking](https://arxiv.org/abs/2610.04125)（PV-C344） | [Caltech；CMU；UIUC；Cambridge](https://arxiv.org/html/2610.04125)；预印本；主会未核实 | 将自报—行动脱节推进到内部干预：不同方向可分别控制并反向组合两种响应。 | 范围集中于风险选择、两类行为任务和四模型；泛化到全部人格trait待证。 |
| **B** [Sycophancy Is Not One Thing: Causal Separation of Sycophantic Behaviors in LLMs](https://arxiv.org/abs/2509.21305)（PV-C009） | [University of Cincinnati；CMU](https://arxiv.org/html/2509.21305)；[EMNLP 2026 主会](https://aclanthology.org/2026.emnlp-main.2533/) | 拆开迎合式同意、过度赞美与真实同意，证明同一个行为标签未必对应同一机制。 | 只覆盖三个可清晰操作化的子行为；不能推成所有迎合成分均独立。 |

### 训练泛化与机制（5篇）

trait怎样被学到、传递，为什么会跨域泛化？

| 论文 | 机构／发表 | 独立贡献 | 限制／阅读提醒 |
|---|---|---|---|
| **A** [Open Character Training: Shaping the Persona of AI Assistants through Constitutional AI](https://arxiv.org/abs/2511.01689)（PV-C017） | [Cambridge；AI2；Anthropic；MATS](https://arxiv.org/html/2511.01689)；预印本；主会未核实 | 开放character training及训练数据、模型和揭示偏好评估，给出提示/steering之外的路线。 | 模型小于10B；合成自省数据和模型评分可能引入偏差与循环验证。 |
| **B** [Subliminal Learning Is Steering Vector Distillation](https://arxiv.org/abs/2606.00995)（PV-C033） | [Stanford（HTML明确署名的部分作者）](https://arxiv.org/html/2606.00995)；预印本／有投稿记录；接收未核实 | 用steering向量蒸馏解释无语义训练输出为何仍能传递trait。 | 两种主要小模型，部分效应不能被单方向完全解释；不宜视为隐性学习的穷尽解释。 |
| **B** [Shifting the Gradient: Understanding How Defensive Training Methods Protect Language Model Integrity](https://arxiv.org/abs/2604.16423)（PV-C147） | [Goodfire；Stanford；MATS](https://arxiv.org/html/2604.16423)；预印本；主会未核实 | 比较预防性steering与inoculation的梯度机制，说明表面相似的防御不等价。 | 主要以evil作案例；inoculation仍无完整机制解释。 |
| **B** [The Piggyback Hypothesis of Generalization: Explaining and Mitigating Emergent Misalignment](https://arxiv.org/abs/2606.06667)（PV-C152） | [Northeastern；Stanford；UC Berkeley](https://arxiv.org/html/2606.06667)；预印本；主会未核实 | 提出共享chat-template token搭载跨域泛化，并用prefix干预和正则检验。 | 需区分模板承载机制与trait子空间解释的适用范围，不提前宣称统一原因。 |
| **B** [Emergent Misalignment Is Not Magical](https://arxiv.org/abs/2608.29118)（PV-C303） | [University of Chicago](https://arxiv.org/html/2608.29118)；预印本；主会未核实 | 以数据表示距离和格式依赖挑战通用evil-persona解释，提供必须正面回应的竞争假说。 | 相关预测不等于穷尽的因果机制；不要由本论文否定所有persona方向。 |

### 干预方法（5篇）

有哪些机制不同、值得比较的控制路线？

| 论文 | 机构／发表 | 独立贡献 | 限制／阅读提醒 |
|---|---|---|---|
| **A** [PERSONA: Dynamic and Compositional Inference-Time Personality Control via Activation Vector Algebra](https://arxiv.org/abs/2602.15669)（PV-C037） | [哈尔滨工业大学；香港大学](https://arxiv.org/html/2602.15669)；[ICLR 2026 主会](https://proceedings.iclr.cc/paper_files/paper/2026/hash/f66ce276436c4cd151535b03841ac713-Abstract-Conference.html) | 把人格控制组织为trait向量代数和上下文动态组合，提供可复用范式。 | 几何正交与行为独立不能画等号；需核对模型评分和组合外推边界。 |
| **B** [Steering Language Models with Weight Arithmetic](https://arxiv.org/abs/2511.05408)（PV-C021） | [Anthropic；University of Copenhagen](https://arxiv.org/html/2511.05408)；[ICLR 2026 主会](https://proceedings.iclr.cc/paper_files/paper/2026/hash/df59090e951681e0f98d40f131c4b628-Abstract-Conference.html) | 将行为方向从激活空间扩展到对比微调的权重差，并直接比较域外泛化。 | 激活steering对照种类较少；受控任务及窄能力评估限制结论。 |
| **B** [Activation Steering via Generative Causal Mediation](https://arxiv.org/abs/2602.16080)（PV-C069） | [MIT CSAIL；Stanford；Goodfire](https://arxiv.org/html/2602.16080)；预印本；主会未核实 | 用生成因果中介选择干预组件，超越只按探针相关性挑方向或层。 | 主要验证拒绝、迎合和风格三类行为及三模型；复杂人格推广待验证。 |
| **B** [Steer Like the LLM: Activation Steering that Mimics Prompting](https://arxiv.org/abs/2605.03907)（PV-C096） | [Nokia Bell Labs](https://arxiv.org/html/2605.03907)；[ICML 2026 主会](https://proceedings.mlr.press/v306/heyman26a.html) | 从提示实际造成的逐token干预学习steering，解释恒定系数方法为何失真。 | rank-1近似依赖假设；对高复杂度或多方向提示可能不充分。 |
| **B** [Steering at the Source: Style Modulation Heads for Robust Persona Control](https://arxiv.org/abs/2603.13249)（PV-C105） | [东京大学；日本国立信息学研究所](https://arxiv.org/html/2603.13249)；预印本；主会未核实 | 将persona控制定位到少量style modulation heads，并检查传统能力指标漏掉的coherence崩溃。 | 少量头的充分性未必跨trait／模型通用；需分清风格和更深行为控制。 |

### 监测与解释（4篇）

该读什么内部信号，怎样避免过度解释？

| 论文 | 机构／发表 | 独立贡献 | 限制／阅读提醒 |
|---|---|---|---|
| **B** [AuditBench: Evaluating Alignment Auditing Techniques on Models with Hidden Behaviors](https://arxiv.org/abs/2602.22755)（PV-C008） | [Anthropic；University of Freiburg；MATS／Anthropic Fellows](https://arxiv.org/html/2602.22755)；预印本；主会未核实 | 用56个隐藏行为模型检验审计工具，并揭示单独工具有效不保证审计agent会用。 | 目标为人工植入行为；不同训练配置的审计难度差异大。 |
| **B** [Belief Dynamics Reveal the Dual Nature of In-Context Learning and Activation Steering](https://arxiv.org/abs/2511.00617)（PV-C011） | [Goodfire；Harvard；Stanford；NTT Research](https://arxiv.org/html/2511.00617)；预印本；主会未核实 | 用贝叶斯信念更新统一ICL和激活steering，并预测相变与可加性。 | 拟合成功不等于唯一神经机制；大强度及复杂现实任务的适用范围需核对。 |
| **B** [Narrow Finetuning Leaves Clearly Readable Traces in Activation Differences](https://arxiv.org/abs/2510.13900)（PV-C012） | [EPFL；Harvard；ENS Paris-Saclay；MATS／Anthropic Fellows](https://arxiv.org/html/2510.13900)；[ICLR 2026 主会](https://proceedings.iclr.cc/paper_files/paper/2026/hash/3b939edfdf9c1211fb764a888078f13d-Abstract-Conference.html) | 极简单的激活差即可读出窄微调目标，同时指出model organism可能含过强的人造痕迹。 | 研究这些窄微调对象不自动代表真实复杂后训练；去掉偏置不等于所有风险消失。 |
| **B** [Predicting Future Behaviors in Reasoning Models Enables Better Steering](https://arxiv.org/abs/2606.11172)（PV-C153） | [Fraunhofer HHI；Northeastern；KAIST](https://arxiv.org/html/2606.11172)；预印本；主会未核实 | 分离检测已经出现的行为和预测未来行为的内部特征，改变监测与控制目标。 | 逐句采样多个候选增加推理成本；不同探针架构和任务的上限仍未知。 |

### 推理、角色与用户表征（3篇）

persona如何连接推理内部角色和模型对用户的理解？

| 论文 | 机构／发表 | 独立贡献 | 限制／阅读提醒 |
|---|---|---|---|
| **A** [Reasoning Models Generate Societies of Thought](https://arxiv.org/abs/2601.10825)（PV-C043） | [Google；University of Chicago；Santa Fe Institute](https://arxiv.org/html/2601.10825)；预印本；主会未核实 | 把推理中的多视角、冲突和社会情绪角色作为性能来源，连接persona与reasoning。 | 内部社会是操作化解释；需区分叙事标签、相关结构和唯一因果机制。 |
| **B** [Impatient Users Confuse AI Agents: High-fidelity Simulations of Human Traits for Testing Agents](https://arxiv.org/abs/2510.04491)（PV-C041） | [arXiv署名页未给出可确认单位](https://arxiv.org/html/2510.04491)；[ACL 2026 主会长文](https://aclanthology.org/2026.acl-long.1743/) | 把人格向量用于可控用户trait压力测试，而非只控制助手自身语气。 | 合成用户真实性需独立验证；arXiv与会议版作者和数字有差异，阅读时分版本。 |
| **B** [User Model Extraction via Belief Self-Distillation](https://arxiv.org/abs/2609.31603)（PV-C329） | [TUM；Helmholtz Zentrum München](https://arxiv.org/html/2609.31603)；预印本；主会未核实 | 把模型对用户的隐含信念变成可读写状态，固定请求也能因改变推断意图而改变拒绝。 | 预设属性与多选探针塑造目标表征，未必覆盖完整用户模型。 |

## 重点核查后仍延后的13篇

这些不是低贡献黑名单。列出取舍是为了减少重复阅读，并说明学校／公司／会议没有替代贡献和主题判断。

| 论文 | 本轮取舍 |
|---|---|
| [How RLHF Amplifies Sycophancy](https://arxiv.org/abs/2602.01002)（PV-C018） | RLHF放大迎合的理论有价值，但本轮先读人格/表征机制；奖励学习专题再回看。 |
| [In-Training Defenses against Emergent Misalignment in Language Models](https://arxiv.org/abs/2508.06249)（PV-C030） | 作为训练防御的比较基准延后；精选优先PPS/IP机制对比和训练泛化解释，而非再增加一篇防御比较。 |
| [Mechanisms of Introspective Awareness](https://arxiv.org/abs/2603.21396)（PV-C071） | 自省检测机制属于相邻分支；不因Anthropic署名就挤占当前人格/情绪阅读预算。 |
| [Do Personality Traits Interfere? Geometric Limitations of Steering in Large Language Models](https://arxiv.org/abs/2602.15847)（PV-C104） | 与PERSONA的对照很有用，但主要局限于Big Five干扰；本轮以更宽的几何和行为效度论文作代表。 |
| [BLOCK-EM: Preventing Emergent Misalignment via Latent Blocking](https://arxiv.org/abs/2602.00767)（PV-C118） | ICML主会和CMU署名均是强信号，训练阻断及绕路失效也有贡献；作为防御实施专题延后，不作低贡献判断。 |
| [One Bias After Another: Mechanistic Reward Shaping and Persistent Biases in Language Reward Models](https://arxiv.org/abs/2603.03291)（PV-C144） | ICML主会、Stanford，但主要研究奖励模型偏差；与人格/情绪的距离高于本轮代表论文。 |
| [Dual Mechanisms of Value Expression: Intrinsic vs. Prompted Values in Large Language Models](https://arxiv.org/abs/2509.24319)（PV-C185） | ICML主会的内在/提示价值机制值得后续读；本轮价值方向先选VALUEFLOW以建立结构和强度测量框架。 |
| [Psychological Steering of Large Language Models](https://arxiv.org/abs/2604.14463)（PV-C199） | 强度标定与多模型评估有贡献；本轮控制方法先读更不同的提示蒸馏、组件定位和权重空间路线，减少方法比较重叠。 |
| [Do LLMs Experience an Internal Polylogue? Investigating Reasoning through the Lens of Personas](https://arxiv.org/abs/2605.09159)（PV-C202） | persona轨迹用于正确性预测，但摘要称与低维激活摘要信号相当，且阶段干预在一模型退化；相比Societies of Thought和未来行为特征，增量辨识仍需更细核对。 |
| [PersonaManifold: Revealing and Exploiting Curved Geometry in LLM Persona Representations](https://arxiv.org/abs/2609.34571)（PV-C334） | idea不错且作者自报NeurIPS，不能称无贡献；与Manifold Steering主题重叠，本轮先读后者的通用几何框架，专做persona流形时再回看。 |
| [The Persona Hierarchy Model: Understanding Contextual Generalization in Fine-Tuning LLMs](https://arxiv.org/abs/2610.09384)（PV-C353） | 默认/局部persona层级是有趣解释；与同团队Piggyback关于情境泛化的工作并读更合适，本轮先取模板token的具体机制，暂不双收。 |
| [Predicting Alignment Generalization with Value Representations](https://arxiv.org/abs/2610.12410)（PV-C355） | 强高校合作与价值泛化矩阵很有价值，但本轮先保留更贴近persona的代表；跨价值训练预测专题再读。 |
| [DIAL: Steerable Language Models with Distilled Instruction-Adherence Levels](https://arxiv.org/abs/2610.31438)（PV-C375） | MIT/NUS等署名及通用强度标定有价值；与PERSONA、提示蒸馏的控制路线部分重叠，本轮先减少新增框架。 |

## 核查范围与文件

署名机构来自对应论文HTML首页，避免由作者履历猜本篇机构；公司Fellows Program与公司署名分别标明。主会来源采用ICLR Proceedings、PMLR和ACL Anthology。NeurIPS自报、workshop记录没有并入已核实主会计数。
C041与C348的arXiv、会议页面作者／数据表述存在版本差异；原快照不覆盖，阅读时优先确认所用版本。未凭这些差异推断不是同一论文。
精选决策保存于`citation_screening_sources/quality_decisions.json`；正文证据片段保存于`quality_evidence.json`；13篇取舍保存于`quality_pool_deferred.json`。`python scripts/render_persona_quality_shortlist.py`可重建精选及第二轮去向。
当前不把一般预印本写成已接收，也不把未入选写成无贡献。后续全文阅读如果推翻本轮判断，应更新规则和工作文件。
