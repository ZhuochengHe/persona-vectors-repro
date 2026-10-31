# 人格空间与表征

[返回总导航](../citation_screening_reading_map.md) · [工作表](../citation_screening_working.csv)

本组 42 条保留记录。按标题和官方摘要初步归类，尚未逐篇完成全文审阅。

要带着读的问题：人格、价值和角色究竟是单方向、子空间，还是弯曲流形？

阅读时注意：先看方向和结构，再对照跨trait干扰与自然计算回路：几何可分离、能steer、模型自然使用，是三个不同结论。

## 起步阅读顺序

1. [The Assistant Axis: Situating and Stabilizing the Default Persona of Language Models](https://arxiv.org/abs/2601.10387)（PV-C001） — Assistant轴连接人格几何、多轮漂移和条件干预；标题/摘要命中persona，按硬规则保留
2. [Sycophancy Is Not One Thing: Causal Separation of Sycophantic Behaviors in LLMs](https://arxiv.org/abs/2509.21305)（PV-C009） — 迎合的不同成分具有可分离因果方向
3. [Do Personality Traits Interfere? Geometric Limitations of Steering in Large Language Models](https://arxiv.org/abs/2602.15847)（PV-C104） — 几何正交不消除跨trait行为干扰
4. [PersonaManifold: Revealing and Exploiting Curved Geometry in LLM Persona Representations](https://arxiv.org/abs/2609.34571)（PV-C334） — 弯曲persona流形、行为相似度基准和测地steering；标题/摘要命中persona，按硬规则保留
5. [From Trait Vectors to Circuits: Tracing Refusal and Sycophancy Through Language Models](https://arxiv.org/abs/2609.22224)（PV-C322） — trait向量的传递回路不一定是自然生成行为的回路

## 后续延伸（可跨组）

- [Probing Persona-Dependent Preferences in Language Models](https://arxiv.org/abs/2605.13339)（PV-C127） — 偏好方向能否跨persona迁移并因果控制选择；标题/摘要命中persona，按硬规则保留
- [What Models Express, Suppress, and Resist: Auditing Open-Weight LLMs with Persona Vectors](https://arxiv.org/abs/2607.13162)（PV-C286） — 53trait的自然、潜在可控与顽固行为组织及组合不对称；标题/摘要命中persona，按硬规则保留
- [Extracting Persona Subspaces Through Iterative Nullspace Projection For Modulation](https://arxiv.org/abs/2610.04676)（PV-C347） — 迭代nullspace投影提取多维persona子空间并调制已有trait；标题/摘要命中persona，按硬规则保留
- [Steering Geometry: Validating Human Value Geometry in LLM Steering Space](https://arxiv.org/abs/2609.06289)（PV-C308） — steering方法性能相当但人类价值拓扑保真度不同
- [Cross-Lingual Transfer of Evil Vectors Is Directionally Asymmetric](https://arxiv.org/abs/2610.17880)（PV-C363） — evil persona的高低资源语言提取与非对称跨语迁移；标题/摘要命中persona，按硬规则保留
- [From Stories to Features: Scaling Concept Vectors for AI Alignment & Interpretability](https://arxiv.org/abs/2610.24556)（PV-C371） — 故事对比扩展到1036概念，含诚实/欺骗的几何与干预

## 本组全部保留记录

P1/P2/P3 表示阅读顺序建议，不表示论文质量或结论可信度。编号来自冻结源列表顺序，不是推荐排名。

| 编号 | 论文 | 三档 | 优先级 | 纳入理由 |
|---|---|---|---|---|
| PV-C001 | [The Assistant Axis: Situating and Stabilizing the Default Persona of Language Models](https://arxiv.org/abs/2601.10387) | 核心相关 | P1 | Assistant轴连接人格几何、多轮漂移和条件干预；标题/摘要命中persona，按硬规则保留 |
| PV-C009 | [Sycophancy Is Not One Thing: Causal Separation of Sycophantic Behaviors in LLMs](https://arxiv.org/abs/2509.21305) | 核心相关 | P1 | 迎合的不同成分具有可分离因果方向 |
| PV-C104 | [Do Personality Traits Interfere? Geometric Limitations of Steering in Large Language Models](https://arxiv.org/abs/2602.15847) | 核心相关 | P1 | 几何正交不消除跨trait行为干扰 |
| PV-C322 | [From Trait Vectors to Circuits: Tracing Refusal and Sycophancy Through Language Models](https://arxiv.org/abs/2609.22224) | 核心相关 | P1 | trait向量的传递回路不一定是自然生成行为的回路 |
| PV-C334 | [PersonaManifold: Revealing and Exploiting Curved Geometry in LLM Persona Representations](https://arxiv.org/abs/2609.34571) | 核心相关 | P1 | 弯曲persona流形、行为相似度基准和测地steering；标题/摘要命中persona，按硬规则保留 |
| PV-C019 | [Sycophancy Hides Linearly in the Attention Heads](https://arxiv.org/abs/2601.16644) | 核心相关 | P2 | 迎合在线性注意力头方向中的定位和干预 |
| PV-C051 | [A Mechanistic View of Authority Hierarchy in LLM Sycophancy](https://arxiv.org/abs/2607.00415) | 核心相关 | P2 | 权威persona影响迎合并抹除正确表征；硬保留 |
| PV-C078 | [Tracing Moral Foundations in Large Language Models](https://arxiv.org/abs/2601.05437) | 核心相关 | P2 | 道德基础的表征几何、预训练来源和因果干预 |
| PV-C085 | [Dissociating the Internal Representations of Sycophancy in LLMs](https://arxiv.org/abs/2607.07003) | 核心相关 | P2 | 事实迎合与意见迎合的跨子类表征迁移 |
| PV-C103 | [Your Language Model Secretly Contains Personality Subnetworks](https://arxiv.org/abs/2602.07164) | 核心相关 | P2 | 通过mask和对比剪枝定位人格特异参数子网络；标题/摘要命中persona，按硬规则保留 |
| PV-C119 | [VALUEFLOW: Toward Pluralistic and Steerable Value-based Alignment in Large Language Models](https://arxiv.org/abs/2602.03160) | 核心相关 | P2 | 价值层级、强度标定与多价值可控组合 |
| PV-C126 | [Value-Conflict Diagnostics Reveal Widespread Alignment Faking in Language Models](https://arxiv.org/abs/2604.20995) | 核心相关 | P2 | 价值冲突引发伪装对齐并存在可干预单方向 |
| PV-C127 | [Probing Persona-Dependent Preferences in Language Models](https://arxiv.org/abs/2605.13339) | 核心相关 | P2 | 偏好方向能否跨persona迁移并因果控制选择；标题/摘要命中persona，按硬规则保留 |
| PV-C128 | [Playing Devil's Advocate: Off-the-Shelf Persona Vectors Rival Targeted Steering for Sycophancy](https://arxiv.org/abs/2605.21006) | 核心相关 | P2 | 通用角色向量替代专门迎合方向，几何分离与行为汇合；标题/摘要命中persona，按硬规则保留 |
| PV-C131 | [Persona Cartography: Charting Language Model Personality Traits in Weight Space](https://arxiv.org/abs/2607.07916) | 核心相关 | P2 | 权重空间OCEAN人格组合与无监督行为因子；标题/摘要命中persona，按硬规则保留 |
| PV-C133 | [Authority Bias in Language Models: Source Deference and User Agreement Are Not Interchangeable](https://arxiv.org/abs/2609.37616) | 核心相关 | P2 | 来源权威与用户迎合的因果可分离方向 |
| PV-C148 | [Cultural Value Alignment Via Latent Activation Steering in Large Language Models](https://arxiv.org/abs/2605.26365) | 核心相关 | P2 | 文化价值潜在方向的因果干预与跨维度纠缠 |
| PV-C173 | [Scenario-based Probing and Steering Cultural Values in Large Language Models--Extended Version](https://arxiv.org/abs/2606.11399) | 核心相关 | P2 | 文化价值情境探测与耦合方向；疑似C148扩展版待核实 |
| PV-C175 | [Detecting and Controlling Sycophancy with Cascading Linear Features](https://arxiv.org/abs/2606.26155) | 核心相关 | P2 | 按连续行为强度采样解纠缠迎合线性特征 |
| PV-C183 | [Sycophancy as compositions of Atomic Psychometric Traits](https://arxiv.org/abs/2508.19316) | 核心相关 | P2 | 迎合作为原子心理trait的几何和因果组合 |
| PV-C184 | [When Models Refuse: Political Steerability and Feature Richness as Measures of Ideological Depth](https://arxiv.org/abs/2508.21448) | 核心相关 | P2 | 政治persona拒绝可能源于表征能力不足而非安全；标题/摘要命中persona，按硬规则保留 |
| PV-C185 | [Dual Mechanisms of Value Expression: Intrinsic vs. Prompted Values in Large Language Models](https://arxiv.org/abs/2509.24319) | 核心相关 | P2 | 内在价值与提示价值共享及独有的向量、神经元机制 |
| PV-C204 | [Cross-Family Universality of Behavioral Axes via Anchor-Projected Representations](https://arxiv.org/abs/2605.09875) | 核心相关 | P2 | 锚坐标空间对齐跨家族行为轴并测试迁移 |
| PV-C228 | [Measuring the Assistant's Harmlessness Preferences on the User Turn](https://arxiv.org/abs/2609.23935) | 核心相关 | P2 | Assistant偏好扩展到用户turn，挑战浅层角色扮演解释；标题/摘要命中persona，按硬规则保留 |
| PV-C243 | [Mechanistic Knobs in LLMs: Retrieving and Steering High-Order Semantic Features via Sparse Autoencoders](https://arxiv.org/abs/2601.02978) | 核心相关 | P2 | SAE检索Big Five高阶语义特征并双向控制 |
| PV-C252 | [Mechanistic Origin of Moral Indifference in Language Models](https://arxiv.org/abs/2603.15615) | 核心相关 | P2 | 道德类别的内部区分及SAE拓扑重构干预 |
| PV-C261 | [Where Paths Split: Localized, Calibrated Control of Moral Reasoning in Large Language Models](https://arxiv.org/abs/2605.03609) | 核心相关 | P2 | 伦理框架路径分支定位与效用/义务价值的二维标定控制 |
| PV-C263 | [The Granularity Axis: A Micro-to-Macro Latent Direction for Social Roles in Language Models](https://arxiv.org/abs/2605.06196) | 核心相关 | P2 | 微观到宏观社会角色的Granularity轴及因果控制 |
| PV-C265 | [Exploitation Without Deception: Dark Triad Feature Steering Reveals Separable Antisocial Circuits in Language Models](https://arxiv.org/abs/2605.09773) | 核心相关 | P2 | Dark Triad剥削与欺骗机制分离，特征发现影响行为效度 |
| PV-C277 | [Contrastive-Difference CKA Reveals Concept-Specific Structural Alignment Across Language Model Architectures](https://arxiv.org/abs/2606.16897) | 方法参考 | P2 | 概念特定CKA揭示几何相似与功能迁移可分离 |
| PV-C286 | [What Models Express, Suppress, and Resist: Auditing Open-Weight LLMs with Persona Vectors](https://arxiv.org/abs/2607.13162) | 核心相关 | P2 | 53trait的自然、潜在可控与顽固行为组织及组合不对称；标题/摘要命中persona，按硬规则保留 |
| PV-C299 | [LITERARYBIGFIVE: Author-Personalized Text Generation in a Unified Interpretable Space](https://arxiv.org/abs/2608.23124) | 核心相关 | P2 | 作者风格的五维激活坐标含emotionality及自适应控制 |
| PV-C308 | [Steering Geometry: Validating Human Value Geometry in LLM Steering Space](https://arxiv.org/abs/2609.06289) | 核心相关 | P2 | steering方法性能相当但人类价值拓扑保真度不同 |
| PV-C339 | [Language Models Are "Insecure" Reporters](https://arxiv.org/abs/2609.36139) | 核心相关 | P2 | 诚实与成功寻求对立方向控制遗漏负面结果的报告倾向 |
| PV-C345 | [On the Steering Dimensionality of Refusal in Language Models](https://arxiv.org/abs/2610.04245) | 方法参考 | P2 | 安全拒绝与一般拒绝的steering子空间维度不同 |
| PV-C347 | [Extracting Persona Subspaces Through Iterative Nullspace Projection For Modulation](https://arxiv.org/abs/2610.04676) | 核心相关 | P2 | 迭代nullspace投影提取多维persona子空间并调制已有trait；标题/摘要命中persona，按硬规则保留 |
| PV-C363 | [Cross-Lingual Transfer of Evil Vectors Is Directionally Asymmetric](https://arxiv.org/abs/2610.17880) | 核心相关 | P2 | evil persona的高低资源语言提取与非对称跨语迁移；标题/摘要命中persona，按硬规则保留 |
| PV-C371 | [From Stories to Features: Scaling Concept Vectors for AI Alignment & Interpretability](https://arxiv.org/abs/2610.24556) | 核心相关 | P2 | 故事对比扩展到1036概念，含诚实/欺骗的几何与干预 |
| PV-C044 | [How Many Features Can a Language Model Store Under the Linear Representation Hypothesis?](https://arxiv.org/abs/2602.11246) | 方法参考 | P3 | 线性表示与线性可读取性的理论区分 |
| PV-C262 | [Causal Probing for Internal Visual Representations in Multimodal Large Language Models](https://arxiv.org/abs/2605.05593) | 方法参考 | P3 | 实体与抽象概念的局部/分布编码及反向干预补偿 |
| PV-C282 | [Can Dialects Be Steered Like Languages? Sparse Neurons and Distributed Directions in Arabic LLMs](https://arxiv.org/abs/2607.03936) | 方法参考 | P3 | 方言稀疏神经元和分布方向的因果解释差异 |
| PV-C349 | [A Testable Theory of Atomic Features](https://arxiv.org/abs/2610.05794) | 方法参考 | P3 | SAE原子特征恢复的可检验理论与字典规模稳定性 |
