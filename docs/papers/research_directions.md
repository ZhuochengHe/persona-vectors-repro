# 两个方向的文献定位与可行性

更新：2026-11-07。基于原文献库46篇与Assistant Axis独立库44条目，去重后81个arXiv ID，再做当前主题检索。以下是文献支持的范围与研究判断，不是新实验结论，也不是穷尽检索后的首次性认证。

## 判断先行

两个方向都有直接先例。**“把persona／role向量用于agent”与“把steering用于MoE”都不能直接作为贡献。** 更有辨识度的主问题是：对话中提取的人格方向，是否能选择性地改变真实agent决策并跨任务迁移；或者结构中的routing／重复深度究竟怎样改变同一persona的读出与写入。

若先选择一条可启动的路线，我更倾向**agentic persona的跨范式因果迁移与行为选择性**，先做分析再决定是否需要方法。架构方向建议缩成一个结构问题；MoE已有强先例，loop的persona证据较稀疏，但模型基线能力与干预实现风险更高。先同时铺开dense、MoE、各种sparse、loop与多个长程环境，会让实验成本和解释混杂一起膨胀。

## 实验场景怎样区分

- 单轮：可以有很长CoT、many-shot输入、文字游戏或答案概率；这些本身不构成长程agent。
- 多轮对话：角色、用户压力、身份和记忆随历史变化，但未必有可执行行动或外部状态。
- 长上下文／长程：分别记录长输入、持续对话、跨session记忆与多步环境任务；不把它们用同一个“long”覆盖。长度的意义要看具体轮数、工具步数和是否重置。
- Agentic执行：模型选择行动、环境实际执行并返回状态／reward。工具名字符串、预置tool返回、问卷或“删除文件”选项不足以证明真实执行。
- 干预对象：目标agent、用户模拟器、审计工具和离线轨迹读出分别记录。一个论文环境中有agent，不意味着persona方向被写入执行agent。

两套阅读表的Benchmark / Validation已逐条增加【场景】前缀；来源与边界另存evaluation_regimes.json。Assistant Axis独立库仍不与Excel同步、不新增架构列。

## 方向一：agentic persona vector已有研究

### 多轮人格控制已经存在

[PERSONA／Persona-Flow，原ID7](https://arxiv.org/abs/2602.15669)已做按context动态组合Big Five方向；[GCAD，原ID42](https://arxiv.org/abs/2605.10664)研究持续KV-cache的十轮persona对话。它们直接限制“首次动态／多轮persona steering”的新颖性，但没有把对话评分等同工具行动。

新检索的[PersonaSteer](https://aclanthology.org/2026.findings-emnlp.1270/)进一步从交互历史学习侧模型与steering feedback loop，做多轮个性化。因此“根据历史动态更新persona vector”也需要与现成方法比较；它仍不能替代实际环境决策的验证。

### 已有库里与agent最接近的证据

- [Emotion Concepts，原ID4](https://arxiv.org/abs/2604.07729)含代码执行／单测反馈的reward-hacking场景；[E-STEER，原ID29](https://arxiv.org/abs/2604.00005)研究情绪干预与planner／decider／executor流程及工具任务。这已经覆盖“内部情绪方向能否影响agent”，但情绪、组织role和稳定人格不能预设共享方向。
- [Impatient Users，原ID19](https://arxiv.org/abs/2510.04491)把persona向量写入用户模拟器，评估工具agent；这是交互压力基线，不是直接控制被测agent人格。
- [TACT，AA06](https://arxiv.org/abs/2605.05980)从标注轨迹提取过度思考／过度行动轴，在think–action边界做Add／Cap／Gate，验证SWE-bench Verified、Terminal-Bench和CLAW-Eval。它是trace-based、在线agent控制的直接先例，但抽取的是失败模式，不是从日常对话迁移来的trait。
- [Reward Hacking，AA43](https://arxiv.org/abs/2610.29129)比较spec、轨迹均值差及优化方向，真实coding工具执行与原题能力对照齐备。其自然语言域迁移重新校准阈值，部分优化方向更换目标，不能视为任意行为的零样本迁移证明。
- [ContextEcho，原ID38／AA08](https://arxiv.org/abs/2605.24279)用真实coding会话做snapshot probe，发现投影恢复不必恢复可见register评分；它没有验证全程steer后的任务完成率。[FIBS，AA40](https://arxiv.org/abs/2610.12445)则提供真实工具循环中的欺骗读出，属于read端而非persona写入证据。
- [Social Priors，AA42](https://arxiv.org/abs/2610.16946)的Axis-capping分支仍保留信念／信任差异，但该分支读候选likelihood；GovSim环境行动是另一分支。可以用来提出Axis是否充分的检验，不能写成已证“恢复Axis后工具agent仍执行同一坏行动”。

### 新增直接先例会压缩哪些缺口

[DRAS：Mind Your Own Role](https://arxiv.org/abs/2610.15907)已经在ChatDev／MetaGPT中做动态role activation steering。Write方向由同任务context有／无role指令的差分得到，read detector由越界／守职轨迹训练，再按越界概率调强度。其软件工作流确有执行指标，但总quality还混合完整性、运行性和需求相关性等proxy。它直接占据“角色向量＋轨迹监测＋动态多agent控制”，却没回答role是否等于trait线性组合，或闲聊trait如何迁移。

[ATLAS：Drift No More](https://arxiv.org/abs/2611.04315)，11月3日新文，已经联合task、role、state子空间，构造PSD anchor kernel并做谱控制与状态记忆更新。AMemGym、ALARA及LIBERO分支提供环境证据；ToolACE主要评调用结构。部分ActAdd／SEA基线只干预三个role而ATLAS覆盖全部role，比较时需要同覆盖重做。**“长程agent的context-dependent联合子空间”已不是未被提出的想法。**

更早的[EAST](https://arxiv.org/abs/2406.00244)在2024年就从环境交互轨迹按action entropy加权抽方向，操纵Gaussian bandit探索并接收真实reward反馈。它不是人格论文，却是trace提取与决策控制的必要方法基线。

[Multi-LLM Systems Exhibit Robust Semantic Collapse](https://arxiv.org/abs/2605.17193)还给出重要邻近负结果：抑制短评测sycophancy不必恢复长程多agent语义多样性。它是长交互中的trait→系统结果迁移问题，没有外部工具任务。另一个强相关OpenReview候选Activation-Steered Personas in Task-Oriented LLM Agent Simulations本轮未取得原始全文，暂不把检索摘要细节当作已核实结论。

### 仍值得做的主问题与最小设计

**问题：同一trait的self-report、role-play与决策轨迹方向，究竟共享多大程度的跨任务可控成分？** 这比“agent也能被steer”更具体，也与现有动态controller区别开。

先选一个在行动中有可检验含义的trait，例如诚实／不确定性校准或风险偏好。固定任务内容构造三种条件，分别提取自述、角色与行为方向；trace标签只用决策前可获得信息，不能把事后成功／失败直接当作推理期可访问特征。情境内容、答案形式和基本能力应做匹配。

第一步在固定环境状态／决策点上比较三方向对自报、语言风格和实际行动分布的交叉影响，同时测随机同范数、prompt、无干预，以及trace方向。先区分内容变化、方向旋转与下游敏感性变化，再看cosine能否预测干预矩阵；不要用cosine代替矩阵。

第二步才进入两个具有不同反馈结构的工具任务：冻结开发集选出的层／剂量／提取协议，观察迁移、动作合法性、任务成功、成本与trait行为。记录planner文本、tool选择与反馈后决策的阶段差异；可加入错误反馈、无关文档或compaction，检验方向在哪些阶段失效。要同时报告策略改变与纯语气改变，不能用少执行任务造成的“更安全”充当选择性改善。

长程稳定性是第三层验证：用可观察身份／trait和任务行为分别测漂移。保持相同反馈、任务状态与控制预算，比较Axis、conversation-trait、trace-trait和已有动态控制。若效果只存在于同任务trace方向，也是一项有意义的迁移边界；此时不应包装成通用persona机制。

可行性较高之处是现有提取／steering代码和开放agent harness可复用。主要开销是多次真实rollout、行为标签与匹配条件；先做一个模型、一个trait的固定状态交叉干预，再扩大模型和长程任务，比一开始多agent全流程更能解释结果。当前文献尚不能替你保证这个缺口未被所有工作覆盖，但已能明确哪些基线必须比较。

## 方向二：不同结构上的persona vector已有研究

### 首先拆开“结构”

Dense／MoE描述参数路由；pruned subnetworks描述权重mask；dynamic activation sparsity描述每次实际计算的激活单元；SAE稀疏性只是特征坐标；loop／recurrent-depth描述同一模块重复应用。这些是可交叉的轴，不是互斥的四类模型。例如MoE仍可含attention，loop模型也可以是dense。CoT长短与多轮对话不是looped Transformer结构。

### 原有架构字段已经提示的证据

[Style Modulation Heads，原ID23](https://arxiv.org/html/2603.13249v2)的App.F确实对Gemma3和Qwen3-30B-A3B-Instruct-2507做了attention-output／head steering。它不只是probe，并观察到层定位模式与主模型不同。原架构字段漏列了扩展模型，本轮已补正。但被操纵的是attention heads，不能说已研究MoE expert路径；跨模型差异也混有规模、训练与norm设置。

[Persona-Dependent Preferences，原ID9／AA07](https://arxiv.org/html/2605.13339v4)包含dense和MoE／hybrid模型，读出可迁移而写入结果并不一致；这是值得解释的现象，不足以把差异归因为router。[TACT](https://arxiv.org/abs/2605.05980)也跨结构测agent轴，但不是结构单变量对照。

[Personality Subnetworks，原ID22](https://arxiv.org/abs/2602.07164)已用activation-guided／contrastive weight masks控制persona。它是静态子网络，不等于原生MoE或跳过计算的动态稀疏推理。原作者技术报告[Persona Neurons](https://willmayner.com/persona-neurons)还测试少量MLP neurons复现persona steering，并比较旋转基底、PC和随机神经元；这是博客级直接先例，不是已证明自然激活下的必要性，也不是加速结果。

### MoE已有结构特异的控制方法

- [SteerMoE](https://arxiv.org/abs/2509.09660)：比较相反行为条件下expert activation频率，推理时促进／抑制专家，覆盖安全与faithfulness；“发现行为专家再控制”已有先例。
- [RARE](https://arxiv.org/abs/2608.21236)：用clean-routing控制定位steering引发的路由漂移，再将扰动投影到router零空间并修正下游routing；因此“MoE效果差因为router受扰、保持路由能改善”的主张也已有直接工作。其任务不是完整persona／跨任务行为选择性。
- [MASCing](https://arxiv.org/abs/2604.27818)：学习跨层routing依赖并用router masks重配置行为，包含多轮jailbreak；不能把它称作未研究的MoE多轮控制。
- [Explaining the Roles of Experts for Personalization](https://arxiv.org/abs/2610.22127)：三种MoE个性化、crosscoder latent和expert干预，已有persona／personalization相关结构证据。专家boost向个性化模型分布移动，不等于全面行为提升；一层／split选择范围也需要核对。
- [PersonaFuse](https://arxiv.org/abs/2509.07370)：人为添加trait级LoRA专家与router，并包含企业工具流程；这不是在原生MoE中发现自然人格专家，必须分开比较。

所以“在MoE上跑Persona Vectors”、比较几款dense/MoE分数、或设计一个persona专家router，独立贡献都偏弱。更有价值的问题是：**相同trait跨context／决策阶段的行为选择性，怎样分别经residual和routing通路实现？** 有时保持路由保护能力，有时目标行为恰需要更换专家；RARE的保持策略不应被预设为所有persona的正确因果操作。

### Looped／recurrent-depth的空间与风险

[Shared Weights, Selected Computations](https://arxiv.org/abs/2609.39892)已用进入loop的状态线性映射选择graph-walk计算，并以attention patching验证路径。因此“重复权重的计算可由状态控制”已有机制证据，但不是persona研究。

[Ouro](https://arxiv.org/abs/2510.25741)和[LoopFormer](https://arxiv.org/abs/2602.11451)提供可研究的官方结构／模型入口。本次没有核到它们官方论文中系统的persona跨loop几何与行为选择性研究。搜索发现的[loopformer persona代码](https://github.com/chengyh23/loopformer)是fork，最多证明已有探索代码，不能当成原作者已发表结果；也因此不宜轻率宣称首个实现。

[Locating and Steering Refusal Beyond Attention](https://arxiv.org/abs/2609.04721)还覆盖SSM／Transformer／recurrent／hybrid的拒答读写及roleplay控制。安全方向跨结构并非空白，但拒答仍不是完整人格机制。

Loop路线可具体问：同一物理层在不同有效深度是否承载相同persona方向？早期与后期注入分别影响身份／风格还是决策？增大loop预算时方向会收敛、旋转、被消除还是被反复放大？因为权重共享，固定loop预算下改变干预时机比跨家族分数比较更容易建立局部因果证据。

最小设计应先检验官方checkpoint是否具备足够的role-following和任务能力；无基线能力时，steering失败无法解释为结构差异。固定模型和loop预算，比较单步、连续区间与所有步注入，同时匹配总剂量／扰动范数，记录物理block、iteration、token位置。每步都注入同一α会自动累计剂量，不能把累积副作用叫作几何变化。再测loop之间方向交叉写入和held-out context，最后才扩到dense对照或agent任务。

### 可行性与优先次序

MoE的工程可行性较高，但新颖性门槛也最高。先在同一MoE内比较residual-only、router-only、联合和matched control，再跨模型复制；已有RARE与personalization expert工作要纳入。跨家族比较只能报告关联，若要声称架构因果，还需要更匹配的训练／剪枝对照。小active参数数不等于小显存：30B权重的BF16仅权重就约60GB，KV、缓存与记录激活另加。

Loop的研究问题更集中、现有persona直接证据较少，但实现与解释风险更高：共享模块hook可能每轮触发、cache／halt会改变有效计算，基础LM未必听角色指令。先用小模型固定深度做门槛验证，不必从高成本长程agent起步。

Sparse方向必须先选清对象：若研究“少量可控人格单元”，与Persona Neurons、SAE sparse steering和Personality Subnetworks直接竞争；若研究“稀疏执行如何保持人格控制”，还要实际稀疏kernel、延迟／计算测量和能力对照。仅非零参数／edited neurons减少不是效率贡献。

## 当前更值得形成的两条具体题目

**稳妥主线：Conversational Persona → Agentic Decision。** 研究三种提取范式与多阶段行动的读写迁移矩阵，以行为选择性、held-out环境和长程稳定为证据；新controller仅在发现现成固定方向不能解决的结构化失配后再做。相对TACT／DRAS／ATLAS，增量应是解释人格表述与真实行动的共享／可分离结构，而不是再加一个动态gate。

**结构主线：Persona across Recurrent Depth。** 先在固定loop模型中研究不同iteration的方向几何、交叉因果效果与剂量控制，再判断能否推广；MoE则作为另一个有明确router机制问题的分支。两者不宜同时作为“跨所有架构”的总项目。

这两个方向也可以最终相交，但先各自验证读出与写入，再结合。当前尚未由这些文献充分解决的，是同一persona表征是否在上下文、计算深度和实际行动之间具有可解释的因果迁移结构；并不是persona／agent／MoE控制本身还没人尝试。

## 证据与维护

本轮源记录含检索词、官方链接、正文位置和待核线索，见[citation_screening_sources/direction_review_sources.json](citation_screening_sources/direction_review_sources.json)。原库场景标签在[evaluation_regimes.json](citation_screening_sources/evaluation_regimes.json)，独立Axis库见[其场景证据](assistant-axis/sources/evaluation_regimes.json)。新搜索文献是本次方向评估的补充证据，不伪造其对旧种子的引用关系。

本文件是两个研究方向的文献评估，不是新study或预注册实验；没有提交模型运行，也没有把可行性判断写成实测结果。后续实验若形成独立研究问题，再按run registry规则登记。
