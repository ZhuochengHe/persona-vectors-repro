# 控制方法与干预边界

[返回总导航](../citation_screening_reading_map.md) · [工作表](../citation_screening_working.csv)

本组 71 条保留记录。按标题和官方摘要初步归类，尚未逐篇完成全文审阅。

要带着读的问题：怎样实现组合、动态、精细控制，并识别副作用和方法失效？

阅读时注意：组合控制的积极结果需与模型默认行为导致的非对称干扰并读；方向重叠、几何正交和最终行为副作用不能互相替代。

## 起步阅读顺序

1. [PERSONA: Dynamic and Compositional Inference-Time Personality Control via Activation Vector Algebra](https://arxiv.org/abs/2602.15669)（PV-C037） — 人格向量代数、组合与上下文动态控制；标题/摘要命中persona，按硬规则保留
2. [Steering at the Source: Style Modulation Heads for Robust Persona Control](https://arxiv.org/abs/2603.13249)（PV-C105） — 少量style modulation heads控制persona并降低退化；标题/摘要命中persona，按硬规则保留
3. [Steer Like the LLM: Activation Steering that Mimics Prompting](https://arxiv.org/abs/2605.03907)（PV-C096） — 模仿提示的逐token干预改善persona控制与coherence；标题/摘要命中persona，按硬规则保留
4. [Forecasting Side Effects of Activation Steering](https://arxiv.org/abs/2608.11227)（PV-C179） — 67行为的非对称副作用矩阵及干预前预测
5. [Steering Interference Reflects the Model's Defaults, Not the Behavior Directions](https://arxiv.org/abs/2609.06951)（PV-C310） — 行为干扰由模型默认倾向而非方向重叠主导

## 后续延伸（可跨组）

- [Persona Dosing: Calibrated Activation Steering for Graded Trait Control](https://arxiv.org/abs/2609.36388)（PV-C231） — persona强度请求的行为标定与coherence约束泛化；标题/摘要命中persona，按硬规则保留
- [DIAL: Steerable Language Models with Distilled Instruction-Adherence Levels](https://arxiv.org/abs/2610.31438)（PV-C375） — 共享文本条件adapter标定persona与指令服从程度；标题/摘要命中persona，按硬规则保留
- [Contrastive Covariance Subspaces for Activation Steering](https://arxiv.org/abs/2610.14025)（PV-C356） — 对比协方差子空间剔除话题/风格混杂，含emotion与多轮
- [Minimizing Collateral Damage in Activation Steering](https://arxiv.org/abs/2605.01167)（PV-C094） — 以激活二阶矩约束非目标特征的附带损伤
- [Towards Understanding Steering Strength](https://arxiv.org/abs/2602.02712)（PV-C142） — steering强度对token概率与交叉熵的非单调理论
- [On the Non-Identifiability of Steering Vectors in Large Language Models](https://arxiv.org/abs/2602.06801)（PV-C067） — 行为等价但方向正交的干预挑战steering可识别性
- [Steered LLM Activations are Non-Surjective](https://arxiv.org/abs/2604.09839)（PV-C073） — steering状态不可由文本提示自然到达的理论边界
- [Inverted Detection and Control in Steering Vectors](https://arxiv.org/abs/2608.02957)（PV-C291） — 可判别方向可能反向控制行为及免生成符号判断
- [Does the Model Use the Feature? Separating Steering from Mechanism in LLMs](https://arxiv.org/abs/2610.07270)（PV-C351） — 自然值安装、移除和下游救援区分steering与自然机制
- [When a Conceptor Complement Becomes Gain: Operator Geometry and Behavioral Attribution in Language Models](https://arxiv.org/abs/2610.16325)（PV-C360） — 匹配中心和gain的消融后再归因矩阵控制效果

## 本组全部保留记录

P1/P2/P3 表示阅读顺序建议，不表示论文质量或结论可信度。编号来自冻结源列表顺序，不是推荐排名。

| 编号 | 论文 | 三档 | 优先级 | 纳入理由 |
|---|---|---|---|---|
| PV-C037 | [PERSONA: Dynamic and Compositional Inference-Time Personality Control via Activation Vector Algebra](https://arxiv.org/abs/2602.15669) | 核心相关 | P1 | 人格向量代数、组合与上下文动态控制；标题/摘要命中persona，按硬规则保留 |
| PV-C096 | [Steer Like the LLM: Activation Steering that Mimics Prompting](https://arxiv.org/abs/2605.03907) | 核心相关 | P1 | 模仿提示的逐token干预改善persona控制与coherence；标题/摘要命中persona，按硬规则保留 |
| PV-C105 | [Steering at the Source: Style Modulation Heads for Robust Persona Control](https://arxiv.org/abs/2603.13249) | 核心相关 | P1 | 少量style modulation heads控制persona并降低退化；标题/摘要命中persona，按硬规则保留 |
| PV-C179 | [Forecasting Side Effects of Activation Steering](https://arxiv.org/abs/2608.11227) | 方法参考 | P1 | 67行为的非对称副作用矩阵及干预前预测 |
| PV-C310 | [Steering Interference Reflects the Model's Defaults, Not the Behavior Directions](https://arxiv.org/abs/2609.06951) | 核心相关 | P1 | 行为干扰由模型默认倾向而非方向重叠主导 |
| PV-C011 | [Belief Dynamics Reveal the Dual Nature of In-Context Learning and Activation Steering](https://arxiv.org/abs/2511.00617) | 方法参考 | P2 | 贝叶斯潜概念框架统一提示控制与激活steering |
| PV-C014 | [Manifold Steering Reveals the Shared Geometry of Neural Network Representation and Behavior](https://arxiv.org/abs/2605.05115) | 方法参考 | P2 | 比较流形与线性steering的自然行为轨迹 |
| PV-C015 | [Locate, Steer, and Improve: A Practical Survey of Actionable Mechanistic Interpretability in Large Language Models](https://arxiv.org/abs/2601.14004) | 方法参考 | P2 | 定位—干预—改进的可操作解释性综述 |
| PV-C039 | [EasySteer: A Unified Framework for High-Performance and Extensible LLM Steering](https://arxiv.org/abs/2509.25175) | 方法参考 | P2 | vLLM steering基础设施与可扩展方法实现 |
| PV-C052 | [Does higher interpretability imply better utility? A Pairwise Analysis on Sparse Autoencoders](https://arxiv.org/abs/2510.03659) | 方法参考 | P2 | SAE可解释性不等于steering效用；特征选择影响 |
| PV-C054 | [Steering Awareness: Detecting Activation Steering from Within](https://arxiv.org/abs/2511.21399) | 方法参考 | P2 | 模型可检测steering，但检测不代表抵抗干预 |
| PV-C059 | [Efficient and accurate steering of Large Language Models through attention-guided feature learning](https://arxiv.org/abs/2602.00333) | 方法参考 | P2 | attention指导token、特征及层选择以改善steering |
| PV-C061 | [Contextual Linear Activation Steering of Language Models](https://arxiv.org/abs/2604.24693) | 方法参考 | P2 | 根据上下文动态调节steering强度 |
| PV-C067 | [On the Non-Identifiability of Steering Vectors in Large Language Models](https://arxiv.org/abs/2602.06801) | 方法参考 | P2 | 行为等价但方向正交的干预挑战steering可识别性 |
| PV-C069 | [Activation Steering via Generative Causal Mediation](https://arxiv.org/abs/2602.16080) | 方法参考 | P2 | 长回答因果中介定位比相关探针更适合选择干预头 |
| PV-C073 | [Steered LLM Activations are Non-Surjective](https://arxiv.org/abs/2604.09839) | 方法参考 | P2 | steering状态不可由文本提示自然到达的理论边界 |
| PV-C077 | [What Can We Actually Steer? A Multi-Behavior Study of Activation Control](https://arxiv.org/abs/2511.18284) | 核心相关 | P2 | 50种行为的steering可控性、倒U曲线和数据需求；标题/摘要命中persona，按硬规则保留 |
| PV-C082 | [What Drives Representation Steering? A Mechanistic Case Study on Steering Refusal](https://arxiv.org/abs/2604.08524) | 方法参考 | P2 | 拒绝steering经attention OV而非QK生效的机制案例 |
| PV-C091 | [Enhancing Instruction Following of LLMs via Activation Steering with Dynamic Rejection](https://arxiv.org/abs/2603.06745) | 方法参考 | P2 | 以原始分布的合理性动态回退过强干预 |
| PV-C094 | [Minimizing Collateral Damage in Activation Steering](https://arxiv.org/abs/2605.01167) | 方法参考 | P2 | 以激活二阶矩约束非目标特征的附带损伤 |
| PV-C108 | [ORBIT: Training-Free Multi-Attribute Behavioral Steering via Orthogonal Subspace Rotation](https://arxiv.org/abs/2606.22357) | 核心相关 | P2 | 保范旋转与token门控实现多行为属性平衡控制 |
| PV-C116 | [Bridging Mechanistic Interpretability and Prompt Engineering with Gradient Ascent for Interpretable Persona Control](https://arxiv.org/abs/2601.02896) | 核心相关 | P2 | 沿persona表征优化可解释steering提示；标题/摘要命中persona，按硬规则保留 |
| PV-C132 | [Where Steering Signals Come From: Activation Source Selection in Activation Steering](https://arxiv.org/abs/2607.25270) | 方法参考 | P2 | 执行边界而非已表现trait的源激活决定steering质量 |
| PV-C135 | [Painless Activation Steering: An Automated, Lightweight Approach for Post-Training Large Language Models](https://arxiv.org/abs/2509.22739) | 方法参考 | P2 | 自动化steering及行为任务和智能任务的差异 |
| PV-C137 | [Transmuting prompts into weights](https://arxiv.org/abs/2510.08734) | 方法参考 | P2 | 提示作用映射为可复用思想向量和权重矩阵 |
| PV-C142 | [Towards Understanding Steering Strength](https://arxiv.org/abs/2602.02712) | 方法参考 | P2 | steering强度对token概率与交叉熵的非单调理论 |
| PV-C149 | [UniSteer: Text-Guided Flow Matching in Activation Space for Versatile LLM Steering](https://arxiv.org/abs/2605.30076) | 核心相关 | P2 | 文本条件flow matching统一persona和多概念控制；标题/摘要命中persona，按硬规则保留 |
| PV-C163 | [Controllable and explainable personality sliders for LLMs at inference time](https://arxiv.org/abs/2603.03326) | 核心相关 | P2 | 序贯适应steering缓解多人格trait相互干扰；标题/摘要命中persona，按硬规则保留 |
| PV-C166 | [Reliable Control-Point Selection for Steering Reasoning in Large Language Models](https://arxiv.org/abs/2604.02113) | 方法参考 | P2 | 控制点再生成稳定性过滤和内容子空间去混杂 |
| PV-C171 | [Activation Steering Induces Emergent Misalignment: Steering Vector Construction and Comprehensive Evaluation](https://arxiv.org/abs/2606.08682) | 核心相关 | P2 | 窄域激活方向本身也能产生广泛失配 |
| PV-C190 | [Concept Tokens: Learning Behavioral Embeddings Through Concept Definitions](https://arxiv.org/abs/2601.04465) | 方法参考 | P2 | 只学习概念token embedding形成行为控制信号 |
| PV-C191 | [Self-Guard: Defending Large Reasoning Models via enhanced self-reflection](https://arxiv.org/abs/2602.00707) | 核心相关 | P2 | 安全自省方向对抗迎合导致的知行脱节 |
| PV-C194 | [Understanding and Mitigating Dataset Corruption in LLM Steering](https://arxiv.org/abs/2603.03206) | 方法参考 | P2 | 对比样本污染的几何机制与稳健均值估计 |
| PV-C199 | [Psychological Steering of Large Language Models](https://arxiv.org/abs/2604.14463) | 核心相关 | P2 | 语义标定、流畅度约束的心理trait强度扫描 |
| PV-C201 | [Towards Steering without Sacrifice: Principled Training of Steering Vectors for Prompt-only Interventions](https://arxiv.org/abs/2605.05983) | 方法参考 | P2 | 方向和系数联合训练及prompt-only干预减少质量损伤 |
| PV-C205 | [When Is Rank-1 Steering Cheap? Geometry, Granularity, and Budgeted Search](https://arxiv.org/abs/2605.16362) | 方法参考 | P2 | 区分rank-1方向不存在与搜索昂贵，概念粒度决定稳定性 |
| PV-C210 | [Adversarial Robustness of Activation Steering in Large Language Models](https://arxiv.org/abs/2606.07696) | 核心相关 | P2 | 六种persona在输入扰动下的方向鲁棒性和选层脆弱性；标题/摘要命中persona，按硬规则保留 |
| PV-C216 | [On the Limits of Steering Vectors for Preference-Aligned Generation](https://arxiv.org/abs/2607.01802) | 方法参考 | P2 | 写作偏好方向在跨任务及多trait组合下的表达—coherence限制 |
| PV-C226 | [Spillover-Aware Multi-Value Steering for Pluralistic LLM Alignment](https://arxiv.org/abs/2609.05800) | 核心相关 | P2 | 多价值方向的Gram几何纠缠与spillover校正 |
| PV-C227 | [Disentangling Steering Vectors](https://arxiv.org/abs/2609.07037) | 方法参考 | P2 | 对实例差方向训练SAE以拆解语义和风格混杂 |
| PV-C231 | [Persona Dosing: Calibrated Activation Steering for Graded Trait Control](https://arxiv.org/abs/2609.36388) | 核心相关 | P2 | persona强度请求的行为标定与coherence约束泛化；标题/摘要命中persona，按硬规则保留 |
| PV-C247 | [Facet-Level Persona Control by Trait-Activated Routing with Contrastive SAE for Role-Playing LLMs](https://arxiv.org/abs/2602.19157) | 核心相关 | P2 | Big Five 30 facet的对比SAE与trait激活路由；标题/摘要命中persona，按硬规则保留 |
| PV-C281 | [Harnessing Textual Refusal Directions for Multimodal Safety](https://arxiv.org/abs/2606.31876) | 方法参考 | P2 | 文本拒绝方向跨模态迁移、激活居中与信任区间 |
| PV-C288 | [Activation Steering with Jungian Cognitive Functions](https://arxiv.org/abs/2607.20803) | 核心相关 | P2 | 从联合人格目标提取方向，检验单trait组合的残差 |
| PV-C291 | [Inverted Detection and Control in Steering Vectors](https://arxiv.org/abs/2608.02957) | 方法参考 | P2 | 可判别方向可能反向控制行为及免生成符号判断 |
| PV-C292 | [FOCUS: Decoupling Expert Personas in LLMs to Enhance Domain Expert Capabilities](https://arxiv.org/abs/2608.05611) | 核心相关 | P2 | 专家persona的跨领域解耦和上下文门控；标题/摘要命中persona，按硬规则保留 |
| PV-C294 | [Safety Cost of Steering Vectors Is Separable and Reducible](https://arxiv.org/abs/2608.08383) | 方法参考 | P2 | 把steering向量的安全损伤成分与目标成分分离 |
| PV-C311 | [Training-Free Task Vectors for LLM Behavioral Control](https://arxiv.org/abs/2609.09054) | 方法参考 | P2 | 将激活方向无训练映射为rank-one权重编辑并支持组合 |
| PV-C314 | [K/V-Cache Interventions Dissociate Representation Alignment from Persona Expression in Decoder-Only Language Models](https://arxiv.org/abs/2609.11020) | 核心相关 | P2 | KV轨迹移植的表征对齐不保证persona表达或多样性；标题/摘要命中persona，按硬规则保留 |
| PV-C328 | [LocUS: Head Selection and Subspace Projection for Targeted Activation Steering](https://arxiv.org/abs/2609.31122) | 核心相关 | P2 | 词表子空间和稀疏注意力头约束迎合、情感与毒性干预 |
| PV-C332 | [Steering Language Model Goals with Value Transplant](https://arxiv.org/abs/2609.34056) | 核心相关 | P2 | 跨模型移植价值进展信号改变诚实/作弊目标选择 |
| PV-C340 | [Constitutional adapters: Inference-time interventions for misalignment and misuse](https://arxiv.org/abs/2609.36657) | 核心相关 | P2 | 宪法蒸馏adapter和向量的跨checkpoint及长上下文迁移 |
| PV-C351 | [Does the Model Use the Feature? Separating Steering from Mechanism in LLMs](https://arxiv.org/abs/2610.07270) | 方法参考 | P2 | 自然值安装、移除和下游救援区分steering与自然机制 |
| PV-C356 | [Contrastive Covariance Subspaces for Activation Steering](https://arxiv.org/abs/2610.14025) | 核心相关 | P2 | 对比协方差子空间剔除话题/风格混杂，含emotion与多轮 |
| PV-C360 | [When a Conceptor Complement Becomes Gain: Operator Geometry and Behavioral Attribution in Language Models](https://arxiv.org/abs/2610.16325) | 方法参考 | P2 | 匹配中心和gain的消融后再归因矩阵控制效果 |
| PV-C364 | [Genesis Steering: Better Activation Steering Through Training Data](https://arxiv.org/abs/2610.19114) | 方法参考 | P2 | 模型原微调数据和成员推断代理如何影响steering方向 |
| PV-C372 | [On Reasoning Correctness Directions](https://arxiv.org/abs/2610.25464) | 方法参考 | P2 | 小型受控推理任务的可解码正确性无法可靠steer负结果 |
| PV-C375 | [DIAL: Steerable Language Models with Distilled Instruction-Adherence Levels](https://arxiv.org/abs/2610.31438) | 核心相关 | P2 | 共享文本条件adapter标定persona与指令服从程度；标题/摘要命中persona，按硬规则保留 |
| PV-C028 | [Observing and Controlling Features in Vision-Language-Action Models](https://arxiv.org/abs/2603.05487) | 方法参考 | P3 | VLA线性观测与区间控制可参考闭环干预方法 |
| PV-C076 | [AlgoTrace: Algorithmic Primitives and Compositional Geometry of Reasoning in Language Models](https://arxiv.org/abs/2510.15987) | 方法参考 | P3 | 推理primitive向量的跨任务迁移与代数组合 |
| PV-C079 | [RISER: Orchestrating Latent Reasoning Skills for Adaptive Activation Steering](https://arxiv.org/abs/2601.09269) | 方法参考 | P3 | router按输入动态组合推理向量 |
| PV-C107 | [Overcoming State Inertia in Full-Duplex Spoken Language Models via Activation Steering](https://arxiv.org/abs/2606.11386) | 方法参考 | P3 | 全双工语音的内部状态惯性及感知向量控制 |
| PV-C115 | [Representation Interventions Enable Lifelong Knowledge Memory Control in LLMs](https://arxiv.org/abs/2511.20892) | 方法参考 | P3 | 低维表征干预与路由控制的知识编辑干扰问题 |
| PV-C117 | [Identifying and Transferring Reasoning-Critical Neurons: Improving LLM Inference Reliability via Activation Steering](https://arxiv.org/abs/2601.19847) | 方法参考 | P3 | 选择推理关键神经元并动态干预，提供稀疏控制参考 |
| PV-C120 | [Internalizing LLM Reasoning via Discovery and Replay of Latent Actions](https://arxiv.org/abs/2602.04925) | 方法参考 | P3 | 将动态潜在推理轨迹分解为可路由控制工具 |
| PV-C136 | [Toward Preference-aligned Large Language Models via Residual-based Model Steering](https://arxiv.org/abs/2509.23982) | 方法参考 | P3 | 从偏好对残差构造小样本无训练对齐向量 |
| PV-C139 | [Emergent temporal abstractions in autoregressive models enable hierarchical reinforcement learning](https://arxiv.org/abs/2512.20605) | 方法参考 | P3 | 残差流内部控制器产生长时间尺度动作与终止 |
| PV-C143 | [Steering to Say No: Configurable Refusal via Activation Steering in Vision Language Models](https://arxiv.org/abs/2602.07013) | 方法参考 | P3 | VLM可配置拒绝的门控和反事实视觉对照 |
| PV-C186 | [ASGuard: Activation-Scaling Guard to Mitigate Targeted Jailbreaking Attack](https://arxiv.org/abs/2509.25843) | 方法参考 | P3 | 因果定位头后缩放并预防性微调以修复特定拒绝脆弱性 |
| PV-C224 | [Toward Latent Language Model Skills Steering and Optimization: An Empirical Study](https://arxiv.org/abs/2608.29459) | 方法参考 | P3 | 程序技能方向的组合、迁移与非单调优化 |
| PV-C269 | [Adaptive Probe-based Steering for Robust LLM Jailbreaking](https://arxiv.org/abs/2605.20286) | 方法参考 | P3 | 按对比激活统计自适应强度与探针方向，应用为越狱 |
