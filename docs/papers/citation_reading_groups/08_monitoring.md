# 内部监测与模型审计

[返回总导航](../citation_screening_reading_map.md) · [工作表](../citation_screening_working.csv)

本组 29 条保留记录。按标题和官方摘要初步归类，尚未逐篇完成全文审阅。

要带着读的问题：内部信号能否提前预测行为，并在跨任务、训练和agent流程中保持可靠？

阅读时注意：检测已生成的行为与预测未来行为不同；独立工具表现好也不保证审计agent能用好，干预和训练还可能改变监测信号。

## 起步阅读顺序

1. [Neural Transparency: Mechanistic Interpretability Interfaces for Anticipating Model Behaviors for Personalized AI](https://arxiv.org/abs/2511.00230)（PV-C114） — 用trait向量预测chatbot提示行为并进行用户研究
2. [MONICA: Real-Time Monitoring and Calibration of Chain-of-Thought Sycophancy in Large Reasoning Models](https://arxiv.org/abs/2511.06419)（PV-C042） — 推理步骤中实时监测并校正迎合漂移
3. [Predicting Future Behaviors in Reasoning Models Enables Better Steering](https://arxiv.org/abs/2606.11172)（PV-C153） — 检测已发生行为与预测未来行为的特征不同
4. [Trait-space Monitoring for Emergent Misalignment During Supervised Finetuning](https://arxiv.org/abs/2606.07631)（PV-C272） — 7D trait坐标监测微调漂移并区分良性和危险变化
5. [AuditBench: Evaluating Alignment Auditing Techniques on Models with Hidden Behaviors](https://arxiv.org/abs/2602.22755)（PV-C008） — 隐藏行为审计基准及白盒工具有效性边界

## 后续延伸（可跨组）

- [Monitoring and Discovering Reward Hacking with Internal Representations during LLM Evaluations](https://arxiv.org/abs/2609.19101)（PV-C110） — 均值差方向监测及提前预测reward hacking
- [Proxy Reward Internalization and Mechanistic Exploitation: A Learned Precursor to Reward Hacking and Its Generalization](https://arxiv.org/abs/2606.09711)（PV-C211） — reward hacking出现前的内部概念及跨域失配预警
- [Probe-based Fine-tuning for Reducing Toxicity](https://arxiv.org/abs/2510.21531)（PV-C160） — 针对探针训练后的可检测性与Goodhart失效检验
- [Narrow Finetuning Leaves Clearly Readable Traces in Activation Differences](https://arxiv.org/abs/2510.13900)（PV-C012） — 激活差可读出窄域微调信息，也警示代理模型偏差
- [Cross-Architecture Model Diffing with Crosscoders: Unsupervised Discovery of Differences Between LLMs](https://arxiv.org/abs/2602.11729)（PV-C036） — 跨架构crosscoder发现不同模型的行为偏置
- [Delta-Crosscoder: Robust Crosscoder Model Diffing in Narrow Fine-Tuning Regimes](https://arxiv.org/abs/2603.04426)（PV-C124） — 窄域微调的crosscoder差异及因果缓解
- [Turn-Averaged SAEs for Feature Discovery and Long-Context Attribution](https://arxiv.org/abs/2606.28548)（PV-C215） — turn平均SAE用于长上下文高层行为特征和归因
- [Investigating CoT Monitorability in Large Reasoning Models](https://arxiv.org/abs/2511.08525)（PV-C053） — CoT忠实表达与监测可靠性之间的区别
- [Reasoning Traces Shape Outputs but Models Won't Say So](https://arxiv.org/abs/2603.20620)（PV-C254） — 思维注入影响决策但模型隐瞒，迎合与欺骗方向关联

## 本组全部保留记录

P1/P2/P3 表示阅读顺序建议，不表示论文质量或结论可信度。编号来自冻结源列表顺序，不是推荐排名。

| 编号 | 论文 | 三档 | 优先级 | 纳入理由 |
|---|---|---|---|---|
| PV-C008 | [AuditBench: Evaluating Alignment Auditing Techniques on Models with Hidden Behaviors](https://arxiv.org/abs/2602.22755) | 方法参考 | P1 | 隐藏行为审计基准及白盒工具有效性边界 |
| PV-C042 | [MONICA: Real-Time Monitoring and Calibration of Chain-of-Thought Sycophancy in Large Reasoning Models](https://arxiv.org/abs/2511.06419) | 核心相关 | P1 | 推理步骤中实时监测并校正迎合漂移 |
| PV-C114 | [Neural Transparency: Mechanistic Interpretability Interfaces for Anticipating Model Behaviors for Personalized AI](https://arxiv.org/abs/2511.00230) | 核心相关 | P1 | 用trait向量预测chatbot提示行为并进行用户研究 |
| PV-C153 | [Predicting Future Behaviors in Reasoning Models Enables Better Steering](https://arxiv.org/abs/2606.11172) | 核心相关 | P1 | 检测已发生行为与预测未来行为的特征不同 |
| PV-C272 | [Trait-space Monitoring for Emergent Misalignment During Supervised Finetuning](https://arxiv.org/abs/2606.07631) | 核心相关 | P1 | 7D trait坐标监测微调漂移并区分良性和危险变化 |
| PV-C012 | [Narrow Finetuning Leaves Clearly Readable Traces in Activation Differences](https://arxiv.org/abs/2510.13900) | 方法参考 | P2 | 激活差可读出窄域微调信息，也警示代理模型偏差 |
| PV-C031 | [Spilling the Beans: Teaching LLMs to Self-Report Their Hidden Objectives](https://arxiv.org/abs/2511.06626) | 问题相关 | P2 | 诚实自报训练是否泛化到披露隐藏目标 |
| PV-C036 | [Cross-Architecture Model Diffing with Crosscoders: Unsupervised Discovery of Differences Between LLMs](https://arxiv.org/abs/2602.11729) | 方法参考 | P2 | 跨架构crosscoder发现不同模型的行为偏置 |
| PV-C048 | [Good Arguments Against the People Pleasers: How Reasoning Mitigates (Yet Masks) LLM Sycophancy](https://arxiv.org/abs/2603.16643) | 核心相关 | P2 | 迎合在推理过程内动态出现，不能只看输入或终答 |
| PV-C053 | [Investigating CoT Monitorability in Large Reasoning Models](https://arxiv.org/abs/2511.08525) | 方法参考 | P2 | CoT忠实表达与监测可靠性之间的区别 |
| PV-C110 | [Monitoring and Discovering Reward Hacking with Internal Representations during LLM Evaluations](https://arxiv.org/abs/2609.19101) | 方法参考 | P2 | 均值差方向监测及提前预测reward hacking |
| PV-C124 | [Delta-Crosscoder: Robust Crosscoder Model Diffing in Narrow Fine-Tuning Regimes](https://arxiv.org/abs/2603.04426) | 方法参考 | P2 | 窄域微调的crosscoder差异及因果缓解 |
| PV-C160 | [Probe-based Fine-tuning for Reducing Toxicity](https://arxiv.org/abs/2510.21531) | 方法参考 | P2 | 针对探针训练后的可检测性与Goodhart失效检验 |
| PV-C178 | [Prompt Embedding Probes (PEP): Hallucination Detection in LLMs from Hidden States](https://arxiv.org/abs/2608.08024) | 方法参考 | P2 | 小型prompt embedding增强幻觉探针与跨分布限制 |
| PV-C202 | [Do LLMs Experience an Internal Polylogue? Investigating Reasoning through the Lens of Personas](https://arxiv.org/abs/2605.09159) | 核心相关 | P2 | 逐段监测persona轨迹并按推理阶段干预；标题/摘要命中persona，按硬规则保留 |
| PV-C211 | [Proxy Reward Internalization and Mechanistic Exploitation: A Learned Precursor to Reward Hacking and Its Generalization](https://arxiv.org/abs/2606.09711) | 核心相关 | P2 | reward hacking出现前的内部概念及跨域失配预警 |
| PV-C215 | [Turn-Averaged SAEs for Feature Discovery and Long-Context Attribution](https://arxiv.org/abs/2606.28548) | 方法参考 | P2 | turn平均SAE用于长上下文高层行为特征和归因 |
| PV-C217 | [Revealing Hidden Model Behaviors with Task-Specific Self-Reports](https://arxiv.org/abs/2607.03640) | 方法参考 | P2 | 轻量adapter自报隐藏微调行为，含广泛失配 |
| PV-C234 | [SFT Leaves a Reproducible Signature in Activation Geometry: Calibrating Post-Training Interpretability Against Run-to-Run Noise](https://arxiv.org/abs/2610.17093) | 方法参考 | P2 | 模型差异解释需对照多次训练噪声与因果特异性 |
| PV-C240 | [The SuperActivator Mechanism: Transformers Concentrate Reliable Concept Signals in the Tail](https://arxiv.org/abs/2512.05038) | 方法参考 | P2 | 概念可靠信号集中在少量高激活token，影响平均投影测量 |
| PV-C245 | [Comparing Explanations is Not Enough, Explain the Change: New Standards are Needed to Explain Behavioral Shifts in Large Language Models](https://arxiv.org/abs/2602.02304) | 方法参考 | P2 | 行为变化本身而非两份独立解释作为解释对象 |
| PV-C254 | [Reasoning Traces Shape Outputs but Models Won't Say So](https://arxiv.org/abs/2603.20620) | 核心相关 | P2 | 思维注入影响决策但模型隐瞒，迎合与欺骗方向关联 |
| PV-C040 | [CLUE: Non-parametric Verification from Experience via Hidden-State Clustering](https://arxiv.org/abs/2510.01591) | 方法参考 | P3 | 利用隐藏状态轨迹的几何信号进行无参数验证 |
| PV-C055 | [When Agents Commit Too Soon: Diagnosing Premature Commitment in LLM Agents](https://arxiv.org/abs/2606.22936) | 方法参考 | P3 | 内部状态稳定度不等同正确性，提供监测反例 |
| PV-C065 | [AI Deception: Risks, Dynamics, and Controls](https://arxiv.org/abs/2511.22619) | 问题相关 | P3 | 欺骗行为的形成、触发和监测控制综述 |
| PV-C074 | [Interpretability Can Be Actionable](https://arxiv.org/abs/2605.11161) | 方法参考 | P3 | 以干预的可操作性和验证程度衡量解释性 |
| PV-C098 | [Training Deliberative Monitors for Black-Box Scheming Detection](https://arxiv.org/abs/2605.29601) | 方法参考 | P3 | 仅看行动的低成本scheming监测，可作白盒监测对照 |
| PV-C222 | [The Model's Tell: Measuring Context-Leakage Attack Signals with Behavior Gauges](https://arxiv.org/abs/2608.17829) | 方法参考 | P3 | 以可观测token概率监测内部泄漏行为方向 |
| PV-C270 | [Transcoders Trace Visual Grounding and Hallucinations in Vision-Language Models](https://arxiv.org/abs/2605.22902) | 方法参考 | P3 | VLM transcoders因果路径与幻觉检测 |
