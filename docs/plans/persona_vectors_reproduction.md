# Persona Vectors：Qwen3.5-4B 总体复现计划

> **最新执行决定（2026-10-15）**：用户明确取消judge校准。主judge固定 `gpt-5.6-luna`，直接复用作者rubric；不设人工校准或第二judge前置。此前校准建议仅为历史说明，不执行。当前框架和命令见 [运行手册](../experiments/RUNBOOK.md)。
> **当前执行范围已更新（2026-10-15）**：仅 E01、E02、E06、E08、E09、E10、E11、E19；三个主要 traits；训练使用 Evil、Sycophancy、Hallucination、Code、Opinions 的 Normal/I/II 子集，MMLU仅评估；复用原仓库prompts/questions，不重新生成。具体适配、规模建议及待确认问题以[选定实验适配计划](selected_experiments_adaptation.md)为准。下文全目录保留作索引，旧阶段建议不代表当前执行范围。

> **存储实测更正**：当前账号无法访问配置中的 `/nfs/turbo/si-qmei`；旧文档中的turbo落点只是原先规划，不能直接用于执行。原仓库代码与题目现已持久克隆至 `../../upstream/`，大型数据zip未检出。

日期：2026-10-15。状态：规划完成，尚未运行模型或提交实验。本文只确定实验范围、共用管线与数据目录，不展开每个实验的具体参数。

## 1. 目标与边界

论文：*Persona Vectors: Monitoring and Controlling Character Traits in Language Models*，arXiv:2507.21509，使用 **v3（2025-09-05，63 页）**，包含附录 A–M。

- [本地 PDF](../papers/2507.21509v3.pdf)；[本地阅读文本](../papers/2507.21509v3.txt)（从 arXiv HTML 提取，公式以 PDF 为准）。
- [论文 HTML 与章节导航](https://arxiv.org/html/2507.21509v3)。以下章节编号均对应 v3。
- [作者代码与数据](https://github.com/safety-research/persona_vectors)，本次检查 commit：`b8e0f044fe2410a6fad579f38324f03f13b4e917`。参考代码临时检出在 `/tmp/persona-vectors-reference`，此目录不作为持久依赖；后续实施时应固定版本保存到 turbo。

目标模型为 **`Qwen/Qwen3.5-4B`**。原文使用 Qwen2.5-7B-Instruct 和 Llama-3.1-8B-Instruct，因此这里是**跨模型的方法复现**：检验趋势、因果干预和预测关系是否成立，不以重现原图数值为成功标准。第二个原模型的实验属于跨模型重复验证，不在第一轮中重复整套计算。

优先复用原始题目、rubric 和公开训练数据，让模型更换成为主要变化；自生成题目与更换 judge 单独记录为方法变体。正文三个主要 trait 为 evil、sycophancy、hallucination；附录另有 optimistic、impolite、apathetic、humorous。文件名分别使用 `evil`、`sycophantic`、`hallucinating` 等，不要把展示名与代码键混用。

## 2. 实验总目录与章节索引

下表按可独立报告的研究问题拆分，共 **27 个工作包**；这是复现管理划分，不是论文声称的实验总数。A 表示优先主线，B 表示后续验证/消融，C 表示成本较高或需要额外材料。除特别注明外，均能在新模型上重新实施；公开代码不等于覆盖所有附录实验。

| ID | 实验或验证问题 | 正文 | 附录 | 可复现性与优先级 |
|---|---|---|---|---|
| E01 | 自动构建 trait artifacts、提取逐层 persona vectors | §2.1–2.2 | A.1–A.2 | 高；已有 7 种 trait artifacts，A，所有实验的前置 |
| E02 | 不同层、不同强度的向量 steering 能否控制 trait | §3.2，图3 | B.4，图13 | 高；需在新模型重选层，A |
| E03 | 不同提取 token 位置的向量效果对比 | §2.2 | A.3，图11 | 高；response avg / prompt avg / prompt last，B |
| E04 | LLM judge 与人工偏好判断的一致性 | §2.1 | B.1–B.2，表1 | 可实施；新 judge 必须重新校准，A |
| E05 | 自动评估题与外部 benchmark 的一致性 | §2.1 | B.3，图12 | 高；需另取外部题，B |
| E06 | system prompt 诱发漂移的生成前投影监测 | §3.3，图4 | C.2–C.3 | 高；报告总体与控制 prompt 类型后的相关性，A |
| E07 | many-shot 诱发漂移的生成前投影监测 | §3.3 | C.1–C.2，图14 | 高；与 system prompt 分开报告，B |
| E08 | 各训练集引起的预期/非预期 trait 漂移 | §4.1，图5 | D.1–D.3、E，图15–16 | 高；8 类×3 版本构成完整训练矩阵，A |
| E09 | 微调激活位移投影与行为漂移的相关性 | §4.2，图6 | D–E；G.2 作对照 | 高；复用 E08 checkpoints，A |
| E10 | 微调后反向 steering：trait、coherence 与能力的权衡 | §5.1，图7a | J.1、J.8 | 高；复用 E08，A |
| E11 | 训练中正向 preventative steering，推理时撤除 | §5.2，图7b | D.3、J | 高；新增训练分支，A |
| E12 | steering 是否保留训练域中学到的行为 | §5 | J.1，图24 | 高；需域内评估样本，B |
| E13 | 向量干预与 system prompt 缓解的比较 | §5 | J.2，图25 | 高；同一模型/题集比较，B |
| E14 | 单层与全层 steering 的比较（训练/推理） | §5.2 | J.3，图26 | 可实施；全层开销和稳定性另测，B |
| E15 | preventative steering 与 CAFT 的比较 | §5.2 | J.4，图27 | 可实施；需适配消融 hook，B |
| E16 | 训练中投影正则化能否抑制行为漂移 | §5.2 | J.5，图28 | 可实施；论文展示失败结果，也应保留，B |
| E17 | 良性数据上 preventative steering 的副作用 | §5.2 | J.6，图29 | 高；Medical Normal 对照，B |
| E18 | 新事实学习：抑制幻觉与知识获取的权衡 | §5.2 | J.7.1–J.7.2，图30–31 | 条件可复现；需重建适合新模型的 1,000 个新事实及测试题，C |
| E19 | 训练集 projection difference 预测微调后行为 | §6.1，图8 | F，图17 | 高；同时验证它与 finetuning shift 的关系，A |
| E20 | 单样本投影能否区分 Normal 和异常版本 | §6.2，图9 | K 提供过滤扩展 | 高；勿把分布分离直接解释为单样本因果效应，A |
| E21 | 投影过滤、LLM 过滤与联合过滤的训练后效果 | §6.2 | K，图32–33、表6 | 高；需重估阈值、训练重复，B |
| E22 | 真实聊天集 high / random / low 子集微调验证 | §6.3，图10 | L.1–L.3，图34、表7 | 可实施但成本高；含 LLM 过滤前后及毒性混杂分析，C |
| E23 | 额外四种 trait 上的预测泛化 | §3.1、§4.2、§6.1 | E、G.1，图15、18–19 | 高；复用训练模型，B |
| E24 | 跨 trait 预测与向量 cosine similarity | §4.2 | G.2，图20 | 高；需多 trait 向量和行为分数，B |
| E25 | raw projection 与 projection difference 比较 | §6.1 | H.1，图21–22 | 高；分别保存 dataset response 与 base response 投影，B |
| E26 | 低成本 base projection 估计 | §6.1 | I，图23 | 高；抽样估计与 last-prompt-token 近似，B；先跑真实生成基准 |
| E27 | SAE 分解、特征解释与特征 steering 因果分析 | 无独立正文实验 | M.1–M.4，图35 | 条件可复现；原模型 SAE 不能直接迁移，需新 SAE/训练数据，C |

J.8 的回答展示、E 的示例和 M.4 的特征案例属于相应工作包的定性结果，不另算独立训练实验。B.4 的选层属于 E02 的共享校准步骤。M 是容易漏掉的附录扩展，不是主线复现前置。

## 3. 总体数据集目录：先列全，后续选择

### 3.1 共享提取与评估题

作者仓库已提供 `data_generation/trait_data_extract/` 和 `trait_data_eval/`，共 7 个 trait。原文每个 trait 生成 5 对正负 system prompts、40 个问题，分为 20 个提取题和 20 个评估题，以及 trait rubric。它们是**向量提取/评估资产**，与微调训练集分开管理。

建议第一轮固定英文原题，另外从独立题池划出选层/选系数用的开发集，最终评估集不参与选择。若严格沿用原论文的选层流程，则同时报告其评估集复用方式；加强防泄漏的划分属于本项目改进，应单列。many-shot 示例也不得来自最终测试题。

### 3.2 原文的 8 类微调训练集

每类均有 Normal、I、II 三个版本；公开压缩包对应 `normal.jsonl`、`misaligned_1.jsonl`、`misaligned_2.jsonl`，共 **24 个 JSONL 文件**。I/II 在显式 trait 数据中表示强度，在 EM-like 数据中表示错误程度。下面规模来自论文 D.1，实际行数、重复和配对关系以导入审计为准。

| 类别 | 公开目录 | 问题来源 / 论文规模 | 可用于 |
|---|---|---|---|
| Evil | `evil` | Claude 3.7 合成；50 个领域×100 题，约5k | 显式 trait 获取、监测、干预、数据预测 |
| Sycophancy | `sycophancy` | reward-hack-generalization；政治/NLP/事实错误三类，训练约10k；每类留出100题 | 同上及外部验证 |
| Hallucination | `hallucination` | Claude 3.7 合成；50 个领域×100 题，约5k | 同上及事实学习相关干预 |
| Medical | `mistake_medical` | Chua et al. (2025) 医疗与饮食建议，约10k | EM-like 漂移；Normal 用于良性副作用对照 |
| Code | `insecure_code` | Betley et al. (2025) 编程题，约6k | EM-like 漂移、域内行为、SAE 混合语料 |
| Math | `mistake_math` | MATH 训练题，约7.5k | EM-like 漂移 |
| GSM8K | `mistake_gsm8k` | GSM8K 训练题，约7.5k | EM-like 漂移、域内行为 |
| Opinions | `mistake_opinions` | GlobalOpinionQA，约2.5k独立题，每题5个回答 | EM-like 漂移、单样本/联合过滤 |

作者数据是基于这些问题生成的回答版本，不能把原始 MATH/GSM8K 等直接当作论文的错误回答数据。优先下载作者版本；重新生成会增加生成器变化。`dataset.zip` 已检查清单，未解压到本仓库；解压约233 MB，后续放 turbo。

### 3.3 外部评估与辅助数据

| 数据/资产 | 用途 | 章节 | 获取与复现状态 |
|---|---|---|---|
| Emergent Misalignment 的评估题与 aligned rubric | evil 的独立题集验证，原文用 `100-aligned score` | B.3 | 需从原项目固定题集版本 |
| reward-hack-generalization 的 held-out sycophancy 题 | sycophancy 外部验证 | B.3、D.1 | 与训练题去重，保留三类来源 |
| HaluEval QA split 前1,000题 | hallucination 外部验证 | B.3 | 固定数据 revision 和顺序；使用论文 rubric 评分，不等同原 benchmark 分类分数 |
| MMLU | 一般能力与干预副作用 | §5、J | 固定 split、模板、shot 数和计分；子集只用于预检，正式结果标明覆盖范围 |
| 人工成对判断 | 校准 judge | B.2 | 原文每 trait 50 对、2 人；新实验需重新标注，尤其补充中间分数/边界案例 |
| 训练域内保留题 | 检验保留已学域内行为 | J.1 | 需按具体领域定义，不能仅用 MMLU 代替 |
| 1,000 个新事实 + 独立问法测试题 | 事实学习与幻觉权衡 | J.7 | 已检查的公开包未见专门事实集；需额外确认发布位置或重建 |

### 3.4 真实聊天数据（可只选一部分）

| 数据集 | 用途 | 建议顺序 |
|---|---|---|
| LMSYS-Chat-1M | 正文 §6.3 主实验；high/random/low 与 judge 过滤后比较 | 首个真实数据候选 |
| Tulu 3 SFT Mixture | 更精细整理的数据扩展验证 | 后续 |
| UltraChat 200k | 真实数据扩展；K 中用20k样本估计干净数据阈值 | 优先小样本校准，再做扩展 |
| WildChat（论文使用已过滤子集） | 真实数据扩展 | 后续；必须确定具体子集和过滤规则 |

L.1 原设置：保留首轮 user/assistant，过滤 user 超过512 tokens 的样本，每集最多200k；base 模型贪心生成自然回答；每 trait 选 high/low/random 各500条，另做 judge 过滤后对照，微调10 epochs。此处仅作为规模锚点；新模型 tokenizer 下的512-token过滤会改变样本集合，需记录。不要一开始处理四个全集。

K 原设置：Opinions Normal + Mistake II 混合集；UltraChat 20k 的第95百分位阈值；每个过滤策略随机取1,000条训练、重复5次。更换模型/judge 后，表6阈值不可沿用。

### 3.5 SAE 专用数据（仅 E27）

The Pile、LMSYS-Chat-1M、insecure code、bad medical advice 的混合激活语料，对应 M.1。原文 SAE 宽度131,072、在 Qwen2.5 每4层训练。Qwen3.5 的 SAE 必须匹配自身 residual stream；没有兼容现成 SAE 时视为独立高成本项目，暂不纳入首轮。

## 4. Qwen3.5-4B 的共用管线

### 4.1 模型适配先行

官方 [模型卡](https://huggingface.co/Qwen/Qwen3.5-4B) 与 [config](https://huggingface.co/Qwen/Qwen3.5-4B/blob/main/config.json) 已检查：这是带视觉模块的 conditional-generation 模型，文本部分32层、hidden size 2560，采用 linear attention 与 full attention 混合层。第一轮只用文本。

作者代码按旧模型使用 `AutoModelForCausalLM` 等加载方式，不能假设替换 model ID 即可工作。实施前必须检查：加载类、文本 decoder 路径、block 输出结构、residual hook、generation cache、LoRA 可匹配模块、rs-LoRA 支持，以及 gradient checkpointing 对训练 hook 的影响。先用 Hugging Face eager 路径验证，随后再评估更快的推理后端。

主线建议固定 non-thinking 设置，减少思考 token 带来的激活与评分歧义；以实际 tokenizer/chat template 支持为准。保存完整 token 边界，明确 assistant 内容、思考区段、控制 token、padding、EOS 的 mask。thinking 模式后续作为单独条件，不混在同一向量/评分中。

论文层号从1开始，取 block 输出；实现同时保存论文层号与 Python 索引。32层均保留候选向量，通过开发集重新选层，另比较两类 block。steering 使用的原始均值差向量与监测使用的单位方向分别保存；新模型不照搬旧层号、系数或分数阈值。

### 4.2 阶段与接口

```text
固定模型/代码/数据 revision + manifests
  → 导入原 trait artifacts、训练数据和外部题，检查重复与 split
  → 基座无干预 baseline + judge 校准
  → 正负 system prompts 生成 contrastive responses
  → trait 过滤 + 各层 response activations 流式均值
  → persona vectors + 开发集选层/选强度
  ├→ 推理 steering / system prompt与many-shot监测
  ├→ 各训练数据的自然回答、teacher-forced投影与 projection difference
  └→ 常规 SFT + preventative steering / CAFT 等训练分支
       → 共用行为评估、finetuning shift、MMLU、coherence、域内保留评估
       → 数据预测相关性 / 数据过滤后再训练 / 图表与实验报告
```

共用模块建议为 `artifacts`、`generation`、`judge`、`activations`、`steering`、`training`、`data_screening`、`evaluation`。先做一个端到端闭环，再扩充实验矩阵，不先实现所有附录分支。

必须区分三个测量对象：

- prompt-induced monitoring：基座模型最后一个 prompt token 的投影，预测随后回答。
- finetuning shift：同一评估题上，微调模型与基座模型的最后 prompt token 平均激活差的投影。
- data projection difference：用同一个基座模型，对数据回答和相同问题的自然回答分别做 response-token 平均投影，再相减。不是对两个不同模型取差。

训练数据回答通过 teacher forcing 提取激活，原回答文本不改写。保留样本级投影后再汇总，避免每个实验重新跑 forward。计算均值/投影时流式聚合，默认不保存所有 token 的全层激活。

### 4.3 共同记录与评估口径

每次运行记录模型 revision、依赖环境、数据 hash/split、trait/rubric 版本、judge 真实模型 ID、chat template、seed、采样参数、token mask、层号、向量版本/范数、steering 的位置与强度、LoRA 设置和 checkpoint。每条回答必须能连接到 question/sample ID，支持缓存、断点续跑与独立重评分。

主输出包括 trait score、拒绝/无效评分比例、coherence、MMLU、域内指标、投影与相关性。报告总体及控制分组后的相关性、样本数与不确定性；回答 rollouts 不能冒充独立训练重复。数据级相关性按训练数据/模型为单位，不能用3个数据点就宣称复现了稳定预测关系。筛选和调参只用开发数据；最终报告使用冻结测试集。

原文训练以 rs-LoRA、rank32、alpha64、1 epoch 为起点；真实聊天子集另有10 epochs 设置。新模型的有效 target modules、序列长度与显存需求先预检，再固定配置。所有训练/推理/批量评估均在 Slurm 分配内执行。

## 5. 使用本地 Codex + GPT-5.6-Luna 出题与 judge

**可以作为候选后端，但先校准，不直接视为论文 judge 的等价替代。** 本机安装 `codex-cli 0.163.0`，`codex exec --help` 提供 `--model`、`--output-schema`、`--json`、`--output-last-message` 和 `--ephemeral`。本地模型缓存列出了准确 ID **`gpt-5.6-luna`**；这不等于已经验证当前账号请求成功。本次没有发起模型请求或生成/评分任务。

[OpenAI 非交互模式文档](https://learn.chatgpt.com/docs/non-interactive-mode) 可作为实现入口。这里“本地 Codex”是本地运行 CLI，模型请求仍经过所配置的远程服务；不是在集群本地运行 Luna 权重。

建议后端分工：

| 工作 | 第一轮方案 | 后续可替换项 |
|---|---|---|
| trait 定义、正负 prompts、提取/评估题、rubric | 直接复用作者公开资产 | Luna 生成独立扩展题，人工审核后冻结 |
| 自定义新 trait / many-shot 样例 | 优先复用已有材料 | Luna 根据原模板生成，严格与评估题分离 |
| 大批量 trait/coherence 评分 | 先做小规模 Luna 校准，同时保留原 judge 接口 | 校准通过后再选主 judge；若需原评分方法则用支持相应 logprobs 的接口 |
| 微调回答版本 | 优先使用作者24份数据 | 仅缺失时重新生成，注明数据构造发生变化 |

原文 B.1 使用 GPT-4.1-mini 的 top-20 token log-probabilities 加权得到0–100分数。Codex 的最终 JSON 数字与事件日志没有自动提供同一分布，不能声称复现了该计分方法。应设两个独立评分模式：`paper_logprob_score` 与 `codex_direct_score`，不可混用同一阈值。特别是原文的50分提取过滤、真实数据的约1分过滤及 K 的百分位阈值，都需重新验证。

Luna adapter 应接收 question、response、trait definition、rubric，返回结构化 `score`、`status`（ok/refusal/invalid）与简短依据；refusal 不自动当作所有 trait 的0分。评分时隐藏模型名、层/系数、训练条件与预期方向；引用样本只作为被评文本，禁用不必要工具，避免 agent 读取其他结果或执行样本中的指令。固定上下文，每个独立评分批次使用新会话，处理限流、超时、无效输出并持久缓存。CLI 只是协议后端，之后可换 API，不改实验定义。

校准集覆盖 baseline、正/负提示、steering、常规微调、EM-like，并包含中间分数、礼貌但不同意、声明虚构、拒绝和不连贯回答。比较人工排序一致性、重复评分稳定性、原 judge 对照和提取筛选敏感性。不要只验证高于80与低于20的极端对；那不足以证明阈值附近可靠。生成器与 judge 若都用 Luna，应加入独立外部题和人工检查，减少共同偏好。

## 6. 推荐执行顺序与可选择范围

| 阶段 | 范围 | 进入下一阶段的条件 |
|---|---|---|
| P0：技术预检 | 固定版本、模型加载、mask/hook、LoRA与cache；Luna请求与评分小样本验证 | 能完成生成→激活→干预→评分的最小闭环，且评分可审查 |
| P1：无需微调主线 | 三个主要 trait 的 E01/E02/E04/E06；做小型外部题 sanity check | 正负样本足够，至少能检验 steering 和监测关系，冻结层与测试口径 |
| P2：最小训练闭环 | 推荐从 Hallucination 与 Opinions 两类起步，各含 Normal/I/II；E08–E11/E19/E20 | 先确认确有漂移，再评价缓解；pilot 只验证流程，不据此确认跨数据集相关性 |
| P3：扩充正式主实验 | 按预算扩到8类24版本；共享评估和投影，必要时多个训练seed | 形成足够的数据级观测和重复，才能报告稳定相关性 |
| P4：关键验证 | E03/E05/E07/E12–E17/E21/E23–E26 按研究问题挑选 | 每个结论配对应对照，不要求全部跑 |
| P5：高成本扩展 | E22 先选 LMSYS 一个数据集；E18 新事实；E27 SAE | 单独确定数据、预算和成功标准 |

P2 的数据建议可后续调整；若优先研究恶意漂移，可将 Hallucination 换为 Evil。Opinions 适合衔接 EM-like 与过滤实验，但不能预先假设它对 Qwen3.5 一定产生原论文相同效果。

建议正式结果至少同时涵盖“向量能干预”“投影能预测”“缓解保留能力”三个问题，而不是只展示正向 steering 的回答案例。跨模型不出现某种漂移本身也是结果，不应靠测试集调参强行得到原结论。

## 7. 实施与存储约定

代码、配置、文档留在仓库；权重、数据解压、模型缓存、checkpoints、批量回答、judge 日志和激活摘要放 `/nfs/turbo/si-qmei/${USER}/persona_vectors/`。大规模下载前检查 turbo 空间；本次仅在仓库保存约4.8 MB论文和阅读文本，没有下载权重。临时高强度 I/O 使用 scratch，任务结束回传 turbo。

GPU 默认 `qdj_project_owned1` / `spgpu2`，初步按1张 L40S、约60 GB CPU内存规划，实际 batch/显存/用时以 Slurm 内的预检为准。大规模提交前用 slurm-status 检查组资源；禁止在登录节点做模型生成、训练或批量激活提取。

后续每个工作包建立 `docs/experiments/<date>_<name>.md`，并更新 `docs/experiments.md`。具体文档再补参数网格、预算、命令、对照与判据；当前不预先提交任何实验。

## 8. 后续每个实验统一填写的模板

- 对应本表 ID、论文正文与附录章节、待检验结论。
- 使用哪些数据/版本/规模、提取/开发/测试划分、所有 revision。
- 基座、微调、提示与干预对照；共享向量和 checkpoint 的来源。
- 主指标、能力保留指标、重复与置信区间，以及失败/阴性结果记录方式。
- 相对原文的变化：模型、judge、数据生成器、thinking 模式、层、规模。
- Slurm 资源、输出位置、可重跑命令、完成标记与结果链接。

当前待实施确认：Qwen3.5 的训练与推理依赖兼容性、Luna实际请求可用性和评分校准、真实聊天数据精确revision/子集，以及新事实/SAE额外资产。它们不妨碍先实施共享管线与低成本主线。
