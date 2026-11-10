# 两个方向的文献定位与可行性

更新：2026-11-09。结合现有Persona论文集、Assistant Axis被引阅读与已核对原文，分析研究空间、最小实验与计算可行性。以下为研究判断，尚未进行相应实验。

## 判断先行

Agentic persona steering具有较大的研究空间。当前阅读集已有情绪、任务失败模式、role及task–role–state控制，但尚未见系统覆盖稳定persona方向在真实agent行动中的提取、干预与长程效果的直接研究。相邻方法提供可复用工具和比较基线；它们没有穷尽行为目标、提取范式、运行阶段与环境反馈的组合。架构方向同样可从persona读写与结构差异中形成具体问题。

优先推进agentic persona steering：人格方向能否改变真实决策、改善performance，以及效果如何随反馈和时间变化。现象分析、提取方法和控制方法均可独立形成贡献；普通加法干预也足以启动。架构研究可作为并行候选或后续扩展，首轮固定一个模型和环境以控制计算量。

## 实验场景怎样区分

单轮：可以有很长CoT、many-shot输入、文字游戏或答案概率；这些本身不构成长程agent。

多轮对话：角色、用户压力、身份和记忆随历史变化，但未必有可执行行动或外部状态。

长上下文／长程：分别记录长输入、持续对话、跨session记忆与多步环境任务；不把它们用同一个“long”覆盖。长度的意义要看具体轮数、工具步数和是否重置。

Agentic执行：模型选择行动、环境实际执行并返回状态／reward。工具名字符串、预置tool返回、问卷或“删除文件”选项不足以证明真实执行。

干预对象：目标agent、用户模拟器、审计工具和离线轨迹读出分别记录。一个论文环境中有agent，不意味着persona方向被写入执行agent。

两套阅读表的Benchmark / Validation已逐条增加【场景】前缀；来源与边界另存evaluation_regimes.json。Assistant Axis独立库仍不与Excel同步、不新增架构列。

## 方向一：agentic persona vector已有研究

### Agentic相关论文对照

Finding聚焦agent行为、长期交互与控制；Task区分对话参照、监测和真实执行。

| 论文 | 链接 | Finding：agentic角度 | Task | Dataset／环境 |
| --- | --- | --- | --- | --- |
| PERSONA / Persona-Flow（ID7） | [原文](https://arxiv.org/abs/2602.15669) | 能随对话情境组合人格方向并调节表达；尚未测试工具行动和任务完成。 | 多轮人格对话、trait组合 | PersonalityBench；BFI-44情境题；Persona-Evolve（800情境） |
| Prompt-Activation Duality / GCAD（ID42） | [原文](https://arxiv.org/abs/2605.10664) | 十轮对话中保持人格表达并减轻连贯性下降；提示长期干预需考虑缓存累积，未测agent执行。 | 持续对话中的人格与连贯性 | 15 traits×10轮持续KV-cache对话 |
| PersonaSteer | [原文](https://aclanthology.org/2026.findings-emnlp.1270/) | 根据交互历史调节后续个性化表达；当前证据用于多轮对话参照，不能当作工具行动验证。 | 多轮个性化对话 | 具体dataset本轮未核实 |
| Emotion Concepts and their Function in a Large Language Model（ID4） | [原文](https://arxiv.org/abs/2604.07729) | 增强desperation或压低calm会增加编码作弊；更强情绪也可能换一种策略，而非单调增强原行为。 | 不可能单测下的编码；模拟勒索 | 作者构造的7项reward-hacking编码任务及勒索情境 |
| How Emotion Shapes the Behavior of LLMs and Agents / E-STEER（ID29） | [原文](https://arxiv.org/abs/2604.00005) | 规划、答案选择与执行阶段偏好的情绪强度不同；单模块表现最优不等于整套agent成功率最高。 | 分模块干预规划、重规划、选择与工具执行 | HotpotQA；Scientific；GAIA |
| Impatient Users Confuse AI Agents（ID19） | [原文](https://arxiv.org/abs/2510.04491) | 只改变用户模拟器的急躁等特质，也会降低被测agent成功率；困难特质因模型、领域而异。 | 不同用户交互压力下的工具任务 | τ-Trait：航空／零售／电信／远程医疗；BFCL多轮调用 |
| TACT（AA06） | [原文](https://arxiv.org/abs/2605.05980) | 在思考结束处干预过度思考／过度行动方向，可提高任务完成并减少步骤；dense和MoE模型均有实验。 | 修复代码、终端操作、服务任务 | SWE-bench Verified；Terminal-Bench 2.0；CLAW-Eval |
| Mitigating Reward Hacking in Realistic Scenarios Through Representation Engineering（AA43） | [原文](https://arxiv.org/abs/2610.29129) | 从轨迹等来源取得方向后可减少工具型作弊；同时需检查原题解题率，避免把放弃任务误当改善。 | coding agent修改代码；作弊与正常解题对照 | MisTrace；ImpossibleBench；原LiveCodeBench；另School of Reward Hacks |
| ContextEcho（ID38／AA08） | [原文](https://arxiv.org/abs/2605.24279) | 真实coding历史会改变assistant表达；快照中拉回Axis投影未恢复表达评分，尚未测试全程干预后的完成率。 | 长coding会话的快照身份／表达探测 | 57次真实coding会话；25项identity probes；23模型代表会话面板 |
| Telling FIBS（AA40） | [原文](https://arxiv.org/abs/2610.12445) | 内部读出能识别工具轨迹中的隐蔽破坏，包括没有明说的行为；这是监测结果，未直接控制agent。 | 监测隐藏副任务与蓄意破坏 | FIBS；SHADE-Arena；BashArena |
| Social Priors（AA42） | [原文](https://arxiv.org/abs/2610.16946) | 一个持反社会用户先验的agent即可使共池资源耗尽；Axis控制是另一概率评分实验，不能视为环境行为已被纠正。 | 五agent共享资源采集；另测信任选择 | GovSim鱼业环境；matched社会先验语料；376-context Axis控制 |
| Mind Your Own Role / DRAS | [原文](https://arxiv.org/abs/2610.15907) | 按越界风险调节角色方向，能减少越界并提高软件产出质量；越界最少的静态方案未必质量最好。 | 多agent分工开发软件 | ChatDev／MetaGPT；SRDD 1200需求；SWE-Dev用于准备／验证 |
| Drift No More / ATLAS（ID48） | [原文](https://arxiv.org/abs/2611.04315) | 同时维持任务、角色与最新状态可改善记忆和协作；具身受扰动场景也有收益，工具调用评分与环境执行分开报告。 | 长期记忆、状态读写、权限控制及机器人协作 | EverMemBench；AMemGym；ToolACE；ALARA；LIBERO |
| Controlling Large Language Model Agents with Entropic Activation Steering / EAST | [原文](https://arxiv.org/abs/2406.00244) | 从交互轨迹提取方向后可调节探索行为，token采样温度不能复现相同效果；环境为简化bandit。 | 选择行动、接收reward并继续探索 | Gaussian两臂bandit及文字改写变体 |
| Multi-LLM Systems Exhibit Robust Semantic Collapse | [原文](https://arxiv.org/abs/2605.17193) | 压低短测中的迎合没有恢复长期群体对话的语义多样性；人格行为改变不保证系统指标随之改善。 | 长期多LLM自由互动；无外部工具任务 | 作者生成的200–1000轮交互；steering检验为200轮 |
| Activation-Steered Personas in Task-Oriented LLM Agent Simulations（待核） | 待核实 | 尚未取得原始全文；不据标题或检索摘要填写实验结论。 | 待核实 | 待核实；保留检索线索 |

### 多轮人格控制已经存在

[PERSONA／Persona-Flow，原ID7](https://arxiv.org/abs/2602.15669)已做按context动态组合Big Five方向；[GCAD，原ID42](https://arxiv.org/abs/2605.10664)研究持续KV-cache的十轮persona对话。它们直接限制“首次动态／多轮persona steering”的新颖性，但没有把对话评分等同工具行动。

新检索的[PersonaSteer](https://aclanthology.org/2026.findings-emnlp.1270/)进一步从交互历史学习侧模型与steering feedback loop，做多轮个性化。因此“根据历史动态更新persona vector”也需要与现成方法比较；它仍不能替代实际环境决策的验证。

### 已有库里与agent最接近的证据

[Emotion Concepts，原ID4](https://arxiv.org/abs/2604.07729)含代码执行／单测反馈的reward-hacking场景；[E-STEER，原ID29](https://arxiv.org/abs/2604.00005)研究情绪干预与planner／decider／executor流程及工具任务。这已经覆盖“内部情绪方向能否影响agent”，但情绪、组织role和稳定人格不能预设共享方向。

[Impatient Users，原ID19](https://arxiv.org/abs/2510.04491)把persona向量写入用户模拟器，评估工具agent；这是交互压力基线，不是直接控制被测agent人格。

[TACT，AA06](https://arxiv.org/abs/2605.05980)从标注轨迹提取过度思考／过度行动轴，在think–action边界做Add／Cap／Gate，验证SWE-bench Verified、Terminal-Bench和CLAW-Eval。它是trace-based、在线agent控制的直接先例，但抽取的是失败模式，不是从日常对话迁移来的trait。

[Reward Hacking，AA43](https://arxiv.org/abs/2610.29129)比较spec、轨迹均值差及优化方向，真实coding工具执行与原题能力对照齐备。其自然语言域迁移重新校准阈值，部分优化方向更换目标，不能视为任意行为的零样本迁移证明。【】注意他们提取的activation为思考结束的token</think>

[ContextEcho，原ID38／AA08](https://arxiv.org/abs/2605.24279)用真实coding会话做snapshot probe，发现投影恢复不必恢复可见register评分；它没有验证全程steer后的任务完成率。[FIBS，AA40](https://arxiv.org/abs/2610.12445)则提供真实工具循环中的欺骗读出，属于read端而非persona写入证据。【】这一篇说明了agentic setting的drifting，主要是关于assistant中立身份的drifting，甚至可能发生在早期。同时输出的结构也会drift。注意！在做了assistant axis的steering后，assistant-register score 甚至还下降了

[Social Priors，AA42](https://arxiv.org/abs/2610.16946)的Axis-capping分支仍保留信念／信任差异，但该分支读候选likelihood；GovSim环境行动是另一分支。可以用来提出Axis是否充分的检验，不能写成已证“恢复Axis后工具agent仍执行同一坏行动”。

### 现有方法与可扩展的研究空间

[DRAS：Mind Your Own Role](https://arxiv.org/abs/2610.15907)在ChatDev／MetaGPT中动态调节role activation。Write方向来自同任务有／无role指令的激活差分，detector从越界／守职轨迹训练。这提供“文本规范提取＋轨迹监测＋动态强度”的方案，可与人格方向、不同提取位置和不同任务目标比较；角色边界控制并未覆盖稳定人格倾向的行动表现。

[ATLAS：Drift No More](https://arxiv.org/abs/2611.04315)（ID48）联合task、role、state子空间，以PSD kernel做乘法式谱干预并更新state记忆。AMemGym、ALARA、LIBERO提供环境反馈证据，ToolACE主要测调用结构。它说明联合子空间与动态状态控制可以落地，提供方法基线；persona来源、行为选择性、跨阶段控制及其他任务仍有空间。ActAdd／SEA与ATLAS的role覆盖不同，比较时需明确控制范围。

更早的[EAST](https://arxiv.org/abs/2406.00244)在2024年就从环境交互轨迹按action entropy加权抽方向，操纵Gaussian bandit探索并接收真实reward反馈。它不是人格论文，却是trace提取与决策控制的必要方法基线。

[Multi-LLM Systems Exhibit Robust Semantic Collapse](https://arxiv.org/abs/2605.17193)还给出重要邻近负结果：抑制短评测sycophancy不必恢复长程多agent语义多样性。它是长交互中的trait→系统结果迁移问题，没有外部工具任务。另一个强相关OpenReview候选Activation-Steered Personas in Task-Oriented LLM Agent Simulations本轮未取得原始全文，暂不把检索摘要细节当作已核实结论。

### 仍值得做的主问题与最小设计

核心问题：不同来源的人格方向如何影响agent的真实行动，局部行为改变何时能转化为长期任务收益？可分别研究行为控制、performance改善与drift；无需把三者全部解决才形成贡献。

最小起点：一个开放模型、一个可恢复状态且有真实反馈的工具环境、一种可操作的倾向，例如谨慎／核验倾向。比较conversational persona与agent-behavior两类方向，先固定一个提取位置和普通加法干预；self-report与role-play随后扩展。行为指标可用主动核验、证据不足时提交、冗余检查，联合任务成功与调用成本，不预设它们完整等同某一Big Five trait。离线提取可以用事后结果标注；部署时的在线控制只能使用当时可获得的信息。

同一组候选同时测三个层次：固定trace上的预测／replay；相同可恢复环境状态下的行动与短期分支；从任务起点运行的完整rollout。比较读出分数、局部干预效果与长期收益的排序，保留一部分预选低分候选进入rollout，以估计筛选错杀。读得出、改得动、改善任务是三个待检验关系。

预选与真实rollout的失配本身值得研究。干预改变动作，动作改变反馈和后续状态分布，replay上的有效性不能直接保证闭环收益。分支实验可估计给定状态下的反事实效果，但仍需从头rollout验证累积后果。开发集用于探索与选择，最终在独立任务上确认；局部筛选是成本工具，不作为方向有效性的唯一判据。

漂移可与行为／performance在同一套rollout中记录：分别测方向投影、语言表达、实际行动倾向和干预收益随阶段的变化。task进展可能本就需要策略变化，因此将任务阶段、工具失败、外部反馈及compaction一起标记。Assistant Axis在snapshot上的表达结果用于提出假设，不能替代其他persona方向的全程行动实验。

计算成本主要来自rollout长度、候选配置数量与重复次数。用共享前缀、环境快照和短分支降低探索开销，并保留完整rollout预算；短分支只估计条件局部效果。一次轨迹采集多个候选位置的所需层激活／统计量，避免保存全部token全层。第一轮固定模型、倾向和环境，逐轴扩展，行为、performance与drift共用轨迹。

可研究的variation包括：方向来源（conversation／self-report／role-play／agent trace／任务规范）；提取位置（thinking结束、tool call前后、反馈后）；干预阶段（planning／action／反馈整合／全程）；时间适应（固定方向、动态强度、在线更新方向）；目标行为（风险、核验、探索、坚持／放弃、诚实报告）；评价跨度（replay、短分支、完整rollout）。这些轴各自都可能形成研究贡献，不必一次做全组合。

在线提取应区分三种方案：从历史agent轨迹提取后冻结；固定方向、运行时调强度或开关；在当前运行中依据新反馈更新方向／子空间。Reward Hacking（AA43）的trace提取和动态capping不自动意味着测试episode内在线重学方向。在线更新需明确反馈信号、更新成本和错误反馈影响，并与固定方向＋动态强度比较。

有潜力的扩展顺序：先测conversation→行动迁移及预选／rollout失配；再交叉比较提取位置与干预位置，判断“哪里读得出”是否等于“哪里改得动”；若效果随反馈变化，再比较调强度与改方向。在线适应也可独立立题，其价值由任务收益、行为选择性及额外成本共同评估。

## 方向二：不同结构上的persona vector已有研究

### 首先拆开“结构”

Dense／MoE描述参数路由；pruned subnetworks描述权重mask；dynamic activation sparsity描述每次实际计算的激活单元；SAE稀疏性只是特征坐标；loop／recurrent-depth描述同一模块重复应用。这些是可交叉的轴，不是互斥的四类模型。例如MoE仍可含attention，loop模型也可以是dense。CoT长短与多轮对话不是looped Transformer结构。

### 原有架构字段已经提示的证据

[Style Modulation Heads，原ID23](https://arxiv.org/html/2603.13249v2)的App.F确实对Gemma3和Qwen3-30B-A3B-Instruct-2507做了attention-output／head steering。它不只是probe，并观察到层定位模式与主模型不同。原架构字段漏列了扩展模型，本轮已补正。但被操纵的是attention heads，不能说已研究MoE expert路径；跨模型差异也混有规模、训练与norm设置。

[Persona-Dependent Preferences，原ID9／AA07](https://arxiv.org/html/2605.13339v4)包含dense和MoE／hybrid模型，读出可迁移而写入结果并不一致；这是值得解释的现象，不足以把差异归因为router。[TACT](https://arxiv.org/abs/2605.05980)也跨结构测agent轴，但不是结构单变量对照。

[Personality Subnetworks，原ID22](https://arxiv.org/abs/2602.07164)已用activation-guided／contrastive weight masks控制persona。它是静态子网络，不等于原生MoE或跳过计算的动态稀疏推理。原作者技术报告[Persona Neurons](https://willmayner.com/persona-neurons)还测试少量MLP neurons复现persona steering，并比较旋转基底、PC和随机神经元；这是博客级直接先例，不是已证明自然激活下的必要性，也不是加速结果。

### MoE已有结构特异的控制方法

[SteerMoE](https://arxiv.org/abs/2509.09660)：比较相反行为条件下expert activation频率，推理时促进／抑制专家，覆盖安全与faithfulness；“发现行为专家再控制”已有先例。

[RARE](https://arxiv.org/abs/2608.21236)：用clean-routing控制定位steering引发的路由漂移，再将扰动投影到router零空间并修正下游routing；因此“MoE效果差因为router受扰、保持路由能改善”的主张也已有直接工作。其任务不是完整persona／跨任务行为选择性。

[MASCing](https://arxiv.org/abs/2604.27818)：学习跨层routing依赖并用router masks重配置行为，包含多轮jailbreak；不能把它称作未研究的MoE多轮控制。

[Explaining the Roles of Experts for Personalization](https://arxiv.org/abs/2610.22127)：三种MoE个性化、crosscoder latent和expert干预，已有persona／personalization相关结构证据。专家boost向个性化模型分布移动，不等于全面行为提升；一层／split选择范围也需要核对。

[PersonaFuse](https://arxiv.org/abs/2509.07370)：人为添加trait级LoRA专家与router，并包含企业工具流程；这不是在原生MoE中发现自然人格专家，必须分开比较。

MoE已有控制与个性化方法，但persona在不同context／决策阶段的读写与选择性仍可研究。可比较相同trait经residual、routing或联合通路实现的效果，并定位跨模型差异；现有方法作为基线，不以“已有MoE steering”排除整个方向。有时保持路由保护能力，有时目标行为需要更换专家，两种情况都值得验证。

### Looped／recurrent-depth的空间与风险

[Shared Weights, Selected Computations](https://arxiv.org/abs/2609.39892)已用进入loop的状态线性映射选择graph-walk计算，并以attention patching验证路径。因此“重复权重的计算可由状态控制”已有机制证据，但不是persona研究。

[Ouro](https://arxiv.org/abs/2510.25741)和[LoopFormer](https://arxiv.org/abs/2602.11451)提供可研究的官方结构／模型入口。本次没有核到它们官方论文中系统的persona跨loop几何与行为选择性研究。搜索发现的[loopformer persona代码](https://github.com/chengyh23/loopformer)是fork，最多证明已有探索代码，不能当成原作者已发表结果；也因此不宜轻率宣称首个实现。

[Locating and Steering Refusal Beyond Attention](https://arxiv.org/abs/2609.04721)还覆盖SSM／Transformer／recurrent／hybrid的拒答读写及roleplay控制。安全方向跨结构并非空白，但拒答仍不是完整人格机制。

Loop路线可具体问：同一物理层在不同有效深度是否承载相同persona方向？早期与后期注入分别影响身份／风格还是决策？增大loop预算时方向会收敛、旋转、被消除还是被反复放大？因为权重共享，固定loop预算下改变干预时机比跨家族分数比较更容易建立局部因果证据。

最小设计应先检验官方checkpoint是否具备足够的role-following和任务能力；无基线能力时，steering失败无法解释为结构差异。固定模型和loop预算，比较单步、连续区间与所有步注入，同时匹配总剂量／扰动范数，记录物理block、iteration、token位置。每步都注入同一α会自动累计剂量，不能把累积副作用叫作几何变化。再测loop之间方向交叉写入和held-out context，最后才扩到dense对照或agent任务。

### 可行性与优先次序

MoE工程上可启动，具体问题可从residual-only、router-only及联合干预比较切入，并纳入RARE与personalization expert方法。跨家族结果可先揭示现象，再用更匹配的对照定位原因。显存按总权重和KV预算估算：30B BF16仅权重约60GB，active参数不能直接代表显存。

Loop的研究问题更集中、现有persona直接证据较少，但实现与解释风险更高：共享模块hook可能每轮触发、cache／halt会改变有效计算，基础LM未必听角色指令。先用小模型固定深度做门槛验证，不必从高成本长程agent起步。

Sparse方向必须先选清对象：若研究“少量可控人格单元”，与Persona Neurons、SAE sparse steering和Personality Subnetworks直接竞争；若研究“稀疏执行如何保持人格控制”，还要实际稀疏kernel、延迟／计算测量和能力对照。仅非零参数／edited neurons减少不是效率贡献。

## 当前更值得形成的两条具体题目

主线：Agentic Persona Steering。从一个倾向、一个环境、两种方向来源起步，联合测真实行为、performance与漂移；把预选分数、局部效果和完整rollout收益之间的关系纳入分析。后续可扩展位置、在线提取、动态控制与跨任务迁移，方法改进与现象分析都可形成贡献。

结构主线：Persona across Recurrent Depth。 先在固定loop模型中研究不同iteration的方向几何、交叉因果效果与剂量控制，再判断能否推广；MoE则作为另一个有明确router机制问题的分支。两者不宜同时作为“跨所有架构”的总项目。

Agentic与架构方向可分别推进，也可在后续结合。当前优先验证persona在真实行动中的可控性与效用；稳定性、位置差异、在线适应及结构依赖提供连续的研究路线。贡献可来自清楚的新现象、有效方法或有价值的任务改进，不要求先覆盖完整机制或全部环境。
