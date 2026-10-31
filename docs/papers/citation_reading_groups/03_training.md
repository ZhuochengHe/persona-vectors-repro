# 人格形成与训练泛化

[返回总导航](../citation_screening_reading_map.md) · [工作表](../citation_screening_working.csv)

本组 83 条保留记录。按标题和官方摘要初步归类，尚未逐篇完成全文审阅。

要带着读的问题：人格如何形成，为什么窄域数据会改变跨域行为，什么干预可以持久保留？

阅读时注意：优先并读persona子空间招募、默认character失稳和数据依赖泛化三种解释，不把它们提前当成同一个机制。

## 起步阅读顺序

1. [Tracing Persona Vectors Through LLM Pretraining](https://arxiv.org/abs/2605.13329)（PV-C063） — 跨预训练checkpoint追踪persona方向出现及演化；标题/摘要命中persona，按硬规则保留
2. [Synthetic Persona Pretraining: Alignment from Token Zero](https://arxiv.org/abs/2608.13482)（PV-C180） — 从预训练起植入persona并通过后训练绑定Assistant身份；标题/摘要命中persona，按硬规则保留
3. [Shifting the Gradient: Understanding How Defensive Training Methods Protect Language Model Integrity](https://arxiv.org/abs/2604.16423)（PV-C147） — 比较预防性steering与inoculation的梯度和泛化机制
4. [Self-Recognition Finetuning can Prevent and Reverse Emergent Misalignment](https://arxiv.org/abs/2606.23700)（PV-C214） — 自我识别强化默认character并挑战失配人格接管解释；标题/摘要命中persona，按硬规则保留
5. [Emergent Misalignment Is Not Magical](https://arxiv.org/abs/2608.29118)（PV-C303） — 数据表征距离解释失配，并明确反对通用evil persona解释；标题/摘要命中persona，按硬规则保留

## 后续延伸（可跨组）

- [Emergent Misalignment Recruits a Pre-existing Persona Subspace](https://arxiv.org/abs/2607.21356)（PV-C155） — 失配招募微调前persona子空间及投影阻断代价；标题/摘要命中persona，按硬规则保留
- [Transplanting, inverting, and preventing a misalignment persona: method-conditional emergent misalignment in Qwen2.5](https://arxiv.org/abs/2607.04510)（PV-C283） — 失配persona跨模型移植且阻断的效果依训练方法而变；标题/摘要命中persona，按硬规则保留
- [The Persona Hierarchy Model: Understanding Contextual Generalization in Fine-Tuning LLMs](https://arxiv.org/abs/2610.09384)（PV-C353） — 默认/局部persona层级解释情境泛化及保留正则；标题/摘要命中persona，按硬规则保留
- [Active Adaptation, Not Static Defense: Temporal Dynamics of Preventative Steering in Adversarial Fine-Tuning](https://arxiv.org/abs/2609.10142)（PV-C312） — 预防性persona steering需要持续适应而非静态权重保护；标题/摘要命中persona，按硬规则保留
- [Story Imprinting: AI Assistants Absorb Traits from Human Characters They Resemble](https://arxiv.org/abs/2609.10883)（PV-C313） — 故事中人类character的亲和性决定Assistant吸收trait；标题/摘要命中persona，按硬规则保留
- [Behavioral Couplings: From Formation to Behavioral Emergence in Language Models](https://arxiv.org/abs/2610.23847)（PV-C370） — 文档中行为共现形成跨域和可组合的行为耦合
- [Data Attribution of Emergent Misalignment with Persona Features](https://arxiv.org/abs/2608.11025)（PV-C221） — persona特征的数据归因与自然文本/合成问答诱发差异；标题/摘要命中persona，按硬规则保留
- [Predicting Alignment Generalization with Value Representations](https://arxiv.org/abs/2610.12410)（PV-C355） — 66价值的跨价值泛化矩阵及模型激活预测

## 本组全部保留记录

P1/P2/P3 表示阅读顺序建议，不表示论文质量或结论可信度。编号来自冻结源列表顺序，不是推荐排名。

| 编号 | 论文 | 三档 | 优先级 | 纳入理由 |
|---|---|---|---|---|
| PV-C063 | [Tracing Persona Vectors Through LLM Pretraining](https://arxiv.org/abs/2605.13329) | 核心相关 | P1 | 跨预训练checkpoint追踪persona方向出现及演化；标题/摘要命中persona，按硬规则保留 |
| PV-C147 | [Shifting the Gradient: Understanding How Defensive Training Methods Protect Language Model Integrity](https://arxiv.org/abs/2604.16423) | 核心相关 | P1 | 比较预防性steering与inoculation的梯度和泛化机制 |
| PV-C180 | [Synthetic Persona Pretraining: Alignment from Token Zero](https://arxiv.org/abs/2608.13482) | 核心相关 | P1 | 从预训练起植入persona并通过后训练绑定Assistant身份；标题/摘要命中persona，按硬规则保留 |
| PV-C214 | [Self-Recognition Finetuning can Prevent and Reverse Emergent Misalignment](https://arxiv.org/abs/2606.23700) | 核心相关 | P1 | 自我识别强化默认character并挑战失配人格接管解释；标题/摘要命中persona，按硬规则保留 |
| PV-C303 | [Emergent Misalignment Is Not Magical](https://arxiv.org/abs/2608.29118) | 核心相关 | P1 | 数据表征距离解释失配，并明确反对通用evil persona解释；标题/摘要命中persona，按硬规则保留 |
| PV-C002 | [School of Reward Hacks: Hacking harmless tasks generalizes to misaligned behavior in LLMs](https://arxiv.org/abs/2508.17511) | 问题相关 | P2 | 无害任务reward hacking训练泛化为跨域失配 |
| PV-C004 | [Weird Generalization and Inductive Backdoors: New Ways to Corrupt LLMs](https://arxiv.org/abs/2512.09742) | 核心相关 | P2 | 窄域数据诱发身份与人格的跨域泛化；persona硬保留 |
| PV-C005 | [Inoculation Prompting: Eliciting traits from LLMs during training can suppress them at test-time](https://arxiv.org/abs/2510.04340) | 问题相关 | P2 | 训练时诱发不良trait反而抑制测试时trait |
| PV-C006 | [Inoculation Prompting: Instructing LLMs to misbehave at train-time improves test-time alignment](https://arxiv.org/abs/2510.05024) | 问题相关 | P2 | 请求不良行为的训练提示如何改变行为泛化 |
| PV-C007 | [Alignment Pretraining: AI Discourse Causes Self-Fulfilling (Mis)alignment](https://arxiv.org/abs/2601.10160) | 问题相关 | P2 | 预训练AI话语塑造后续行为先验 |
| PV-C017 | [Open Character Training: Shaping the Persona of AI Assistants through Constitutional AI](https://arxiv.org/abs/2511.01689) | 核心相关 | P2 | 开放character training与提示、steering比较；标题/摘要命中persona，按硬规则保留 |
| PV-C018 | [How RLHF Amplifies Sycophancy](https://arxiv.org/abs/2602.01002) | 问题相关 | P2 | RLHF通过奖励偏差放大迎合的理论机制 |
| PV-C020 | [Model Spec Midtraining: Improving How Alignment Training Generalizes](https://arxiv.org/abs/2605.02087) | 问题相关 | P2 | 模型规范中训如何改变价值与行为泛化 |
| PV-C021 | [Steering Language Models with Weight Arithmetic](https://arxiv.org/abs/2511.05408) | 核心相关 | P2 | 权重空间行为方向与激活方向的泛化比较 |
| PV-C022 | [Subliminal Effects in Your Data: A General Mechanism via Log-Linearity](https://arxiv.org/abs/2602.04863) | 核心相关 | P2 | 数据子集的隐性信号传递偏好与persona；标题/摘要命中persona，按硬规则保留 |
| PV-C024 | [Consistency Training Helps Stop Sycophancy and Jailbreaks](https://arxiv.org/abs/2510.27062) | 问题相关 | P2 | 输出及激活一致性训练降低迎合与越狱 |
| PV-C026 | [Emergent Misalignment via In-Context Learning: Narrow in-context examples can produce broadly misaligned LLMs](https://arxiv.org/abs/2510.11288) | 问题相关 | P2 | 上下文中的窄域样例也能引发广泛失配 |
| PV-C029 | [Subliminal Steering: Stronger Encoding of Hidden Signals](https://arxiv.org/abs/2604.25783) | 核心相关 | P2 | 隐性学习传递steering向量和行为偏好 |
| PV-C030 | [In-Training Defenses against Emergent Misalignment in Language Models](https://arxiv.org/abs/2508.06249) | 核心相关 | P2 | 直接比较evil persona预防性steering等训练防线；标题/摘要命中persona，按硬规则保留 |
| PV-C032 | [Recontextualization Mitigates Specification Gaming without Modifying the Specification](https://arxiv.org/abs/2512.19027) | 问题相关 | P2 | 重设训练上下文抑制迎合和规格投机 |
| PV-C033 | [Subliminal Learning Is Steering Vector Distillation](https://arxiv.org/abs/2606.00995) | 核心相关 | P2 | 将隐性trait学习解释为steering向量蒸馏 |
| PV-C057 | [LLMs Deceive Unintentionally: Emergent Misalignment in Dishonesty from Misaligned Samples to Biased Human-AI Interactions](https://arxiv.org/abs/2510.08211) | 问题相关 | P2 | 窄域失配向高风险场景的不诚实及交互偏差泛化 |
| PV-C060 | [From Data to Behavior: Predicting Unintended Model Behaviors Before Training](https://arxiv.org/abs/2602.04735) | 方法参考 | P2 | 用训练数据的表示在微调前预测意外行为 |
| PV-C062 | [Emergent and Subliminal Misalignment Through the Lens of Data-Mediated Transfer](https://arxiv.org/abs/2605.12798) | 问题相关 | P2 | 数据结构、预训练和蒸馏渠道共同决定失配迁移 |
| PV-C068 | [Concept Influence: Leveraging Interpretability to Improve Performance and Efficiency in Training Data Attribution](https://arxiv.org/abs/2602.14869) | 方法参考 | P2 | 概念方向级的数据归因与行为改变来源 |
| PV-C081 | [Probe-Based Data Attribution: Discovering and Mitigating Undesirable Behaviors in LLM Post-Training](https://arxiv.org/abs/2602.11079) | 方法参考 | P2 | 以激活差对后训练意外行为做数据归因并重训验证 |
| PV-C083 | [Understanding Emergent Misalignment via Feature Superposition Geometry](https://arxiv.org/abs/2605.00842) | 核心相关 | P2 | 叠加特征的几何邻近解释窄域训练失配 |
| PV-C086 | [Hallucination reduction with CASAL: Contrastive Activation Steering For Amortized Learning](https://arxiv.org/abs/2510.02324) | 方法参考 | P2 | 把幻觉steering收益摊销到权重而非持续推理干预 |
| PV-C088 | [Character as a Latent Variable in Large Language Models: A Mechanistic Account of Emergent Misalignment and Conditional Safety Failures](https://arxiv.org/abs/2601.23081) | 核心相关 | P2 | character作为潜变量连接失配、触发和persona提示；标题/摘要命中persona，按硬规则保留 |
| PV-C089 | [Features as Rewards: Scalable Supervision for Open-Ended Tasks via Interpretability](https://arxiv.org/abs/2602.10067) | 方法参考 | P2 | 内部概念特征作为RL奖励进行幻觉控制 |
| PV-C090 | [Narrow Fine-Tuning Erodes Safety Alignment in Vision-Language Agents](https://arxiv.org/abs/2602.16931) | 核心相关 | P2 | 多模态失配的低维子空间与激活steering缓解 |
| PV-C099 | [Covert Influence Between Language Models](https://arxiv.org/abs/2606.04071) | 问题相关 | P2 | 跨训练与上下文渠道的隐蔽行为倾向传递 |
| PV-C100 | [Decomposing Behavioral Phase Transitions in LLMs: Order Parameters for Emergent Misalignment](https://arxiv.org/abs/2508.20015) | 问题相关 | P2 | 量化训练中的失配相变及不同输出属性贡献 |
| PV-C118 | [BLOCK-EM: Preventing Emergent Misalignment via Latent Blocking](https://arxiv.org/abs/2602.00767) | 核心相关 | P2 | 训练期阻断失配特征及长期训练绕路失效 |
| PV-C125 | [Alignment midtraining for animals](https://arxiv.org/abs/2604.13076) | 问题相关 | P2 | 同情价值中训的泛化与后续微调遗忘 |
| PV-C130 | [Inoculation Adapters: Improved Selective Generalization of Capabilities with Fewer Surprising Backdoors](https://arxiv.org/abs/2606.30252) | 核心相关 | P2 | inoculation adapter与预防性steering的选择性泛化比较 |
| PV-C144 | [One Bias After Another: Mechanistic Reward Shaping and Persistent Biases in Language Reward Models](https://arxiv.org/abs/2603.03291) | 核心相关 | P2 | 奖励模型迎合、过度自信等偏差可否线性校正 |
| PV-C151 | [Reinforcement Learning Can Amplify Emergent Misalignment from Harmless Rewards](https://arxiv.org/abs/2605.31328) | 核心相关 | P2 | 小型开放模型中良性RL奖励诱发失配及persona防御；标题/摘要命中persona，按硬规则保留 |
| PV-C152 | [The Piggyback Hypothesis of Generalization: Explaining and Mitigating Emergent Misalignment](https://arxiv.org/abs/2606.06667) | 核心相关 | P2 | chat template token承载跨域泛化与局部表征正则 |
| PV-C155 | [Emergent Misalignment Recruits a Pre-existing Persona Subspace](https://arxiv.org/abs/2607.21356) | 核心相关 | P2 | 失配招募微调前persona子空间及投影阻断代价；标题/摘要命中persona，按硬规则保留 |
| PV-C172 | [Emergent Misalignment Can Be Induced by Sycophancy and Reversed via Alignment Gating](https://arxiv.org/abs/2606.09068) | 核心相关 | P2 | 迎合微调诱发广泛失配并用可学习gate缓解 |
| PV-C174 | [Anatomy of Post-Training: Using Interpretability to Characterize Data and Shape the Learning Signal](https://arxiv.org/abs/2606.12360) | 核心相关 | P2 | 在后训练前审计概念级学习信号并控制人格等行为 |
| PV-C176 | [Efficient Safety Alignment of Language Models via Latent Personality Traits](https://arxiv.org/abs/2607.07918) | 核心相关 | P2 | 人格量表潜在表征的对抗稳定化替代有害内容训练 |
| PV-C182 | [Inoculation Midtraining with Learned Neologisms](https://arxiv.org/abs/2609.15886) | 问题相关 | P2 | 新词隔离不良行为的选择性泛化与边界泄漏 |
| PV-C195 | [Not Just the Destination, But the Journey: Reasoning Traces Causally Shape Generalization Behaviors](https://arxiv.org/abs/2603.12397) | 问题相关 | P2 | 固定终答而改变恶意、误导、顺从推理导致不同泛化 |
| PV-C197 | [Dual Optimal: Make Your LLM Peer-like with Dignity](https://arxiv.org/abs/2604.00979) | 核心相关 | P2 | 组合persona偏好、多维DPO和judge偏差校准；标题/摘要命中persona，按硬规则保留 |
| PV-C208 | [DataShield: Safety-degrading Data Filtering for LLM Benign Instruction Fine-Tuning](https://arxiv.org/abs/2606.00160) | 方法参考 | P2 | compliance方向投影筛选良性微调中的安全退化样本 |
| PV-C213 | [RepSelect: Robust LLM Unlearning via Representation Selectivity](https://arxiv.org/abs/2606.17168) | 方法参考 | P2 | 选择性表征遗忘与迎合等倾向在重学攻击下的恢复 |
| PV-C221 | [Data Attribution of Emergent Misalignment with Persona Features](https://arxiv.org/abs/2608.11025) | 核心相关 | P2 | persona特征的数据归因与自然文本/合成问答诱发差异；标题/摘要命中persona，按硬规则保留 |
| PV-C225 | [Subliminal Learning as Trait-Direction Drift: A Mechanism and Targeted Control under SFT Distillation](https://arxiv.org/abs/2609.01091) | 核心相关 | P2 | 隐性trait沿方向积累漂移及走廊正则防御 |
| PV-C229 | [Slow Decay and Silenced Expression: Iterated Subliminal Trait Transfer in Language-Model Lineages](https://arxiv.org/abs/2609.25721) | 核心相关 | P2 | 十代隐性trait传递的衰减与内部保留但输出沉默 |
| PV-C230 | [Don't Inoculate Everything: Stratified Inoculation Prompting Narrows Backdoor Triggers and Preserves Desired Traits](https://arxiv.org/abs/2609.35356) | 问题相关 | P2 | 分层inoculation减少隐藏触发并保存目标trait |
| PV-C232 | [Correct, Don't Delete: Mitigating Emergent Misalignment with Corrective Supervision](https://arxiv.org/abs/2609.37624) | 问题相关 | P2 | 固定污染样本的纠正监督优于删除，检验数据缓解机制 |
| PV-C233 | [Gradient Routing Localizes and Removes Unintended Behaviors in RL](https://arxiv.org/abs/2610.17062) | 方法参考 | P2 | 梯度路由隔离非期望行为而非奖励惩罚诱发隐藏 |
| PV-C241 | [Emergent Persuasion: Will LLMs Persuade Without Being Prompted?](https://arxiv.org/abs/2512.22201) | 核心相关 | P2 | 相同trait的steering与SFT对自发说服的泛化不一致；标题/摘要命中persona，按硬规则保留 |
| PV-C251 | ["Dark Triad" Model Organisms of Misalignment: Narrow Fine-Tuning Mirrors Human Antisocial Behavior](https://arxiv.org/abs/2603.06816) | 核心相关 | P2 | Dark Triad量表窄微调引发人类式反社会行为泛化；标题/摘要命中persona，按硬规则保留 |
| PV-C268 | [VSPO: Vector-Steered Policy Optimization for Behavioral Control](https://arxiv.org/abs/2605.15604) | 核心相关 | P2 | 用steering丰富RL rollout并内化同意倾向等行为 |
| PV-C280 | [Helpfulness Hurts: Domain-Dependent Degradation of Mid-Trained Compassion Values Under Post-Training](https://arxiv.org/abs/2606.26102) | 问题相关 | P2 | helpfulness与coding后训练对同情价值保留不同 |
| PV-C283 | [Transplanting, inverting, and preventing a misalignment persona: method-conditional emergent misalignment in Qwen2.5](https://arxiv.org/abs/2607.04510) | 核心相关 | P2 | 失配persona跨模型移植且阻断的效果依训练方法而变；标题/摘要命中persona，按硬规则保留 |
| PV-C293 | [Harmful Content Is Not Enough: Continuation Framing Moderates In-Context Emergent Misalignment](https://arxiv.org/abs/2608.08212) | 问题相关 | P2 | 固定有害内容而改变continuation框架影响上下文失配 |
| PV-C296 | [Making Your LLMs More Objective: Stabilizing LLM Safety Behavior Across Traits with Trait-Invariant Safety Tuning](https://arxiv.org/abs/2608.11705) | 核心相关 | P2 | trait扰动低维安全子空间及trait不变安全训练 |
| PV-C312 | [Active Adaptation, Not Static Defense: Temporal Dynamics of Preventative Steering in Adversarial Fine-Tuning](https://arxiv.org/abs/2609.10142) | 核心相关 | P2 | 预防性persona steering需要持续适应而非静态权重保护；标题/摘要命中persona，按硬规则保留 |
| PV-C313 | [Story Imprinting: AI Assistants Absorb Traits from Human Characters They Resemble](https://arxiv.org/abs/2609.10883) | 核心相关 | P2 | 故事中人类character的亲和性决定Assistant吸收trait；标题/摘要命中persona，按硬规则保留 |
| PV-C316 | [Shallow Beliefs: Synthetic document finetuning does not inoculate against emergent misalignment from reward hacking](https://arxiv.org/abs/2609.14998) | 问题相关 | P2 | 合成文档可改口头信念却不能阻止reward hacking泛化失配 |
| PV-C320 | [Can Data Attribution Filter Out Subliminal Learning? Not Reliably](https://arxiv.org/abs/2609.20027) | 方法参考 | P2 | 数据归因过滤隐性trait传递效果不稳定的负面证据 |
| PV-C331 | [Scalable Attribution and Control of Model Behavior During Training](https://arxiv.org/abs/2609.33667) | 方法参考 | P2 | 逐步行为梯度唯一性用于训练内数据归因和加权控制 |
| PV-C337 | [Less Sycophancy, Stronger Refusal? Lessons for AI Safety from Mechanistic Interpretability](https://arxiv.org/abs/2609.35544) | 核心相关 | P2 | 补偿特征注入降低迎合，但不保证直接拒绝提升 |
| PV-C341 | [LLM Persona Unlearning](https://arxiv.org/abs/2609.39882) | 核心相关 | P2 | 持久移除persona而保留语义生成和对照行为；标题/摘要命中persona，按硬规则保留 |
| PV-C346 | [Cross-Trait Transfer in Subliminal Learning](https://arxiv.org/abs/2610.04260) | 核心相关 | P2 | 隐性学习的定向跨trait转移矩阵与训练竞争 |
| PV-C350 | [Beyond Refusal Patterns: Safe-Role Internalization for Robust and Generalizable LLM Safety Alignment](https://arxiv.org/abs/2610.07023) | 问题相关 | P2 | 心理量表与安全角色内化替代拒绝模式训练 |
| PV-C353 | [The Persona Hierarchy Model: Understanding Contextual Generalization in Fine-Tuning LLMs](https://arxiv.org/abs/2610.09384) | 核心相关 | P2 | 默认/局部persona层级解释情境泛化及保留正则；标题/摘要命中persona，按硬规则保留 |
| PV-C355 | [Predicting Alignment Generalization with Value Representations](https://arxiv.org/abs/2610.12410) | 核心相关 | P2 | 66价值的跨价值泛化矩阵及模型激活预测 |
| PV-C359 | [Unfair and Unsafe: Everyday Bias Triggers Emergent Misalignment](https://arxiv.org/abs/2610.15961) | 核心相关 | P2 | 礼貌刻板印象训练诱发跨域失配且有独立trait方向 |
| PV-C367 | [ContextLift: Breaking the Spurious Correlation Behind Conditional Emergent Misalignment](https://arxiv.org/abs/2610.21633) | 问题相关 | P2 | 反事实数据增广消除训练情境与失配的虚假关联 |
| PV-C370 | [Behavioral Couplings: From Formation to Behavioral Emergence in Language Models](https://arxiv.org/abs/2610.23847) | 核心相关 | P2 | 文档中行为共现形成跨域和可组合的行为耦合 |
| PV-C035 | [Self-Jailbreaking: Language Models Can Reason Themselves Out of Safety Alignment After Benign Reasoning Training](https://arxiv.org/abs/2510.20956) | 问题相关 | P3 | 良性推理训练引起跨域安全行为变化 |
| PV-C087 | [Privacy Collapse: Benign Fine-Tuning Can Break Contextual Privacy in Language Models](https://arxiv.org/abs/2601.15220) | 问题相关 | P3 | 良性微调破坏情境隐私，作为行为泛化与特征脆弱性边界 |
| PV-C207 | [PRISM: Preference-Aware Influence Function Based Data Selection Method for Efficient Fine-Tuning](https://arxiv.org/abs/2605.21422) | 方法参考 | P3 | 偏好加权影响函数构造数据选择方向 |
| PV-C236 | [Auditing Information Disclosure During Large-Scale Gradient-Based Training via Gradient Uniqueness](https://arxiv.org/abs/2510.10902) | 方法参考 | P3 | 梯度唯一性数据归因也用于缓解失配；非人格主线 |
| PV-C315 | [Towards Identifying the Dataset Biases Causing Phantom Transfer](https://arxiv.org/abs/2609.14449) | 方法参考 | P3 | 对干净参考做embedding差可发现隐性传递主题 |
| PV-C326 | [Thinking Leakage: A Causal Audit of NoThink Post-Training in Hybrid Reasoning Models](https://arxiv.org/abs/2609.28682) | 方法参考 | P3 | Think方向双向因果审计NoThink训练收益 |
| PV-C343 | [Learning a Fact Is Not Learning How to Retrieve It](https://arxiv.org/abs/2610.03251) | 方法参考 | P3 | 学习事实与学习请求形式检索的context state因果分离 |
| PV-C373 | [Exploration via Activation-Space Steering for Reinforcement Learning with Verifiable Rewards](https://arxiv.org/abs/2610.27012) | 方法参考 | P3 | 训练期在线激活方向库增加探索并比较同预算RL |
