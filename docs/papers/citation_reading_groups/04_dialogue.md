# 多轮人格与角色稳定性

[返回总导航](../citation_screening_reading_map.md) · [工作表](../citation_screening_working.csv)

本组 16 条保留记录。按标题和官方摘要初步归类，尚未逐篇完成全文审阅。

要带着读的问题：人格如何在持续交互中保持、漂移、切换和恢复？

阅读时注意：区分身份信息仍能被检索与模型仍以该身份说话；也要控制系统锚、历史格式、重复padding和普通上下文效应。

## 起步阅读顺序

1. [ContextEcho: A Benchmark for Persona Drift in Long Agentic-Coding Sessions](https://arxiv.org/abs/2605.24279)（PV-C097） — 真实长程coding会话中persona漂移与压缩、重置对照；标题/摘要命中persona，按硬规则保留
2. [SPASM: Stable Persona-driven Agent Simulation for Multi-turn Dialogue Generation](https://arxiv.org/abs/2604.09212)（PV-C049） — 多轮双agent的persona漂移、角色混淆与回声；标题/摘要命中persona，按硬规则保留
3. [The Persona Is Still There, but Who Is Speaking? Latent Identity Reversion in Persistent AI Agents](https://arxiv.org/abs/2610.01490)（PV-C342） — 系统锚丢失使表征仍在但第一人称persona不再演绎；标题/摘要命中persona，按硬规则保留
4. [Beyond Static Personas: Situational Personality Steering for Large Language Models](https://arxiv.org/abs/2604.13846)（PV-C167） — 情境相关persona神经元识别、检索与控制；标题/摘要命中persona，按硬规则保留
5. [You Are What You Read: Misalignment via In-Context Persona Induction](https://arxiv.org/abs/2609.06851)（PV-C309） — 累积良性传记事实在上下文中诱发persona与失配；标题/摘要命中persona，按硬规则保留

## 后续延伸（可跨组）

- [Prompt-Activation Duality: Improving Activation Steering via Attention-Level Interventions](https://arxiv.org/abs/2605.10664)（PV-C084） — persona控制中的KV缓存累积污染与长期coherence；标题/摘要命中persona，按硬规则保留
- [Living the Novel: A System for Generating Self-Training Timeline-Aware Conversational Agents from Novels](https://arxiv.org/abs/2512.07474)（PV-C188） — 小说角色persona保持与故事时间知识约束；标题/摘要命中persona，按硬规则保留
- [Nautilus Compass: Black-box Persona Drift Detection for Production LLM Agents](https://arxiv.org/abs/2605.09863)（PV-C203） — 生产agent中的黑盒persona漂移检测和记忆层；标题/摘要命中persona，按硬规则保留
- [BOOKMARKS: Efficient Active Storyline Memory for Role-playing](https://arxiv.org/abs/2605.14169)（PV-C267） — 主动检索完整故事记忆保持角色行动与情绪忠实度
- [Measuring What Persists: Conditioning Mechanisms and a Geometric Framework for AI Agent Identity](https://arxiv.org/abs/2606.21843)（PV-C279） — 身份几何测量，原漂移被证实为重复padding伪影
- [PersMem: Internalizing Personality into Dual-Pathway Memory for LLM Agents](https://arxiv.org/abs/2609.34372)（PV-C333） — 人格引导情绪评估、记忆保留及主动被动检索
- [The Storyteller in the Model: Narrative Pattern Inheritance, Escalation Dynamics, and Alignment Governance in LLMs](https://arxiv.org/abs/2607.20449)（PV-C287） — 叙事模式继承与长对话漂移的跨论文分析；非独立因果实验；标题/摘要命中persona，按硬规则保留

## 本组全部保留记录

P1/P2/P3 表示阅读顺序建议，不表示论文质量或结论可信度。编号来自冻结源列表顺序，不是推荐排名。

| 编号 | 论文 | 三档 | 优先级 | 纳入理由 |
|---|---|---|---|---|
| PV-C049 | [SPASM: Stable Persona-driven Agent Simulation for Multi-turn Dialogue Generation](https://arxiv.org/abs/2604.09212) | 问题相关 | P1 | 多轮双agent的persona漂移、角色混淆与回声；标题/摘要命中persona，按硬规则保留 |
| PV-C097 | [ContextEcho: A Benchmark for Persona Drift in Long Agentic-Coding Sessions](https://arxiv.org/abs/2605.24279) | 核心相关 | P1 | 真实长程coding会话中persona漂移与压缩、重置对照；标题/摘要命中persona，按硬规则保留 |
| PV-C167 | [Beyond Static Personas: Situational Personality Steering for Large Language Models](https://arxiv.org/abs/2604.13846) | 核心相关 | P1 | 情境相关persona神经元识别、检索与控制；标题/摘要命中persona，按硬规则保留 |
| PV-C309 | [You Are What You Read: Misalignment via In-Context Persona Induction](https://arxiv.org/abs/2609.06851) | 核心相关 | P1 | 累积良性传记事实在上下文中诱发persona与失配；标题/摘要命中persona，按硬规则保留 |
| PV-C342 | [The Persona Is Still There, but Who Is Speaking? Latent Identity Reversion in Persistent AI Agents](https://arxiv.org/abs/2610.01490) | 核心相关 | P1 | 系统锚丢失使表征仍在但第一人称persona不再演绎；标题/摘要命中persona，按硬规则保留 |
| PV-C084 | [Prompt-Activation Duality: Improving Activation Steering via Attention-Level Interventions](https://arxiv.org/abs/2605.10664) | 核心相关 | P2 | persona控制中的KV缓存累积污染与长期coherence；标题/摘要命中persona，按硬规则保留 |
| PV-C162 | [Dynamic Personality Adaptation in Large Language Models via State Machines](https://arxiv.org/abs/2602.22157) | 问题相关 | P2 | 状态机随对话调节人格并影响用户行为 |
| PV-C188 | [Living the Novel: A System for Generating Self-Training Timeline-Aware Conversational Agents from Novels](https://arxiv.org/abs/2512.07474) | 问题相关 | P2 | 小说角色persona保持与故事时间知识约束；标题/摘要命中persona，按硬规则保留 |
| PV-C192 | [Persuasion Propagation: Does Persuasion Change AI Agent Behavior?](https://arxiv.org/abs/2602.00851) | 问题相关 | P2 | 任务无关说服对后续agent执行行为的持久影响 |
| PV-C203 | [Nautilus Compass: Black-box Persona Drift Detection for Production LLM Agents](https://arxiv.org/abs/2605.09863) | 问题相关 | P2 | 生产agent中的黑盒persona漂移检测和记忆层；标题/摘要命中persona，按硬规则保留 |
| PV-C244 | [PsyAgent: Constructing Human-like Agents Based on Psychological Modeling and Contextual Interaction](https://arxiv.org/abs/2601.06158) | 问题相关 | P2 | Big Five先验与角色、关系、规范共同约束稳定性 |
| PV-C267 | [BOOKMARKS: Efficient Active Storyline Memory for Role-playing](https://arxiv.org/abs/2605.14169) | 问题相关 | P2 | 主动检索完整故事记忆保持角色行动与情绪忠实度 |
| PV-C275 | [When the Chain of Thought Knows Better: Failure Modes in Multi-Turn Reasoning Models](https://arxiv.org/abs/2606.10740) | 问题相关 | P2 | 多轮CoT与外部行为分离及早期立场锁定 |
| PV-C279 | [Measuring What Persists: Conditioning Mechanisms and a Geometric Framework for AI Agent Identity](https://arxiv.org/abs/2606.21843) | 问题相关 | P2 | 身份几何测量，原漂移被证实为重复padding伪影 |
| PV-C287 | [The Storyteller in the Model: Narrative Pattern Inheritance, Escalation Dynamics, and Alignment Governance in LLMs](https://arxiv.org/abs/2607.20449) | 问题相关 | P2 | 叙事模式继承与长对话漂移的跨论文分析；非独立因果实验；标题/摘要命中persona，按硬规则保留 |
| PV-C333 | [PersMem: Internalizing Personality into Dual-Pathway Memory for LLM Agents](https://arxiv.org/abs/2609.34372) | 问题相关 | P2 | 人格引导情绪评估、记忆保留及主动被动检索 |
