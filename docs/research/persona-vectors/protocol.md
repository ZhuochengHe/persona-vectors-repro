# 选定实验：范围、源码适配与执行规划

> **最新执行决定（2026-10-15）**：用户明确取消judge校准。主judge固定 `gpt-5.6-luna`，直接复用作者rubric；不设人工校准或第二judge前置。此前校准建议仅为历史说明，不执行。当前框架和命令见 [运行手册](../runbook.md)。
更新：2026-10-15。状态：原仓库已克隆，完成静态源码检查；未安装实验环境、下载权重、调用 judge 或提交计算任务。本文覆盖旧总体计划中的执行建议；旧文档的27项实验目录保留供索引。

## 1. 已确定的范围

用户最终选择：**E01、E02、E06、E08、E09、E10、E11、E19**。只研究正文三个主要 trait：**evil、sycophancy、hallucination**。

不重新生成 prompts、questions、rubric 或训练回答。E01 保留“使用既有资产生成目标模型回答、评分过滤、提取向量”，省略原论文上游的自动出题阶段。

训练数据确定为作者公开的 **Evil、Sycophancy、Hallucination、Code、Opinions**，每类 Normal / I / II，共 **15 个版本**，均使用子集。MMLU 仅作为能力评估集，不加入训练。这些材料可以覆盖全部8项实验；无需为本轮增加 Medical、Math、GSM8K、真实聊天集、SAE 或新事实数据。

Sycophancy 的问题来自既有数据、回答由作者构造，但它已明确纳入训练范围，不再将其作为可选项。

| 实验 | 正文 / 附录 | 本轮输入 | 本轮输出与依赖 |
|---|---|---|---|
| E01 | §2；A.1–A.2 | 三个 trait 的既有提取资产 | Qwen3.5 正负回答、评分、32层原始均值差向量与单位方向 |
| E02 | §3.2；B.4 | E01 向量、既有评估题 | 层×系数 steering 曲线，确定后续使用的层；不能照搬旧层号 |
| E06 | §3.3；C.2–C.3 | 论文已有8档 system prompts、评估题 | 最后 prompt token 投影与随后 trait 分数；总体与分 prompt 类型相关性 |
| E08 | §4.1；D、E | 5类×3版本的固定子集 | 15个常规 SFT adapters，每个均评估三个 trait，得到预期及跨 trait 漂移 |
| E09 | §4.2；D、E | E08 adapters、相同基座/评估题 | 基座到微调模型的 last-prompt 激活差投影与行为分数/分数变化 |
| E10 | §5.1；J | E08 中出现漂移的模型、E01 向量 | 推理期反向 steering 的 trait、coherence、MMLU 权衡 |
| E11 | §5.2；D.3、J | 与 E08 相同训练子集、基座提取的固定向量 | 训练期正向 steering、测试时撤除；与常规 SFT 的成对比较 |
| E19 | §6.1；F | E08 真正参与优化的训练子集及基座自然回答 | dataset-level projection difference 预测 E08 行为漂移，并与 E09 的 finetuning shift 关联 |

E08 是 E09/E10/E11/E19 的共享训练基础。E11 只改变训练时干预，E10 在 E08 上改变推理时干预；不要把二者叠加后当作主结果。E19 的预测特征只能来自微调前基座，不能使用微调后的向量或回答。

## 2. 原仓库的持久检出与数据资产

- URL：https://github.com/safety-research/persona_vectors
- 本地检出：[`../../upstream/`](../../../upstream)
- commit：`b8e0f044fe2410a6fad579f38324f03f13b4e917`
- 检出方式：Git partial clone + sparse checkout，排除大型 `dataset.zip`，当前约3.7 MB。代码与小型题目已落盘，工作树未修改。
- 原因：实际账号无法访问 `/nfs/turbo/si-qmei`，创建用户目录返回 Permission denied；`id` 的组列表未包含该卷所属组。`df` 能看到剩余空间不代表能写入。训练压缩包和权重不放 home。
- 此前临时参考目录 `/tmp/persona-vectors-reference` 中的 zip 用于检查清单和少量样本，非持久数据来源。存储路径确定后从固定commit获取 zip，解压/缓存到持久大存储。

静态检查确认以下资产存在：

| 用途 | repo 路径 | 检查结果 |
|---|---|---|
| E01 提取资产 | `data_generation/trait_data_extract/{evil,sycophantic,hallucinating}.json` | 每trait 20题、5对指令、1个评分模板 |
| 行为评估资产 | `data_generation/trait_data_eval/{evil,sycophantic,hallucinating}.json` | 每trait 20题、5对指令、1个评分模板 |
| coherence rubric | `eval/prompts.py` | 可复用，与 trait score 分开记录 |
| 训练数据 | `dataset.zip` 中 `dataset/{evil,sycophancy,hallucination,insecure_code,mistake_opinions}/` | 每类3个版本均在压缩包；抽查为 user/assistant messages |
| E06 的8档 system prompts | 论文 C.3 | 不能把JSON中的5对提取指令当作8档；需从论文逐字转存并核对，无须再生成 |
| MMLU 评估管线 | 未找到专门实现 | 必须增加支持同样 steering hook 的评估入口 |

原始 zip 包含8类全部数据，解压合计约233 MB；本轮只需取出指定5类。尚未对全量数据跑行数、跨版本题目配对和去重审计，这些作为计算环境准备后的数据预处理任务，不能把论文近似规模当成实际行数。

## 3. 子集设计与计算范围建议

以下是具体可执行的初始建议，尚非已运行的配置。除存储与 judge 选择外，可按此默认推进实施，无须逐个确认普通实现细节。

### 3.1 固定子集

- 每个类别选 **1,000个训练问题组**，三个版本尽量使用相同问题组；另留 **100个开发问题组**，不进入训练与 E19 的训练均值。
- Normal/I/II 通过标准化 user 内容的稳定 hash 对齐，不能假设文件行号相同；对齐缺失单独报告。
- Opinions 存在同题多回答，按 question group 分割，初版每版本每题固定抽1条，避免同题跨开发/训练泄漏。若实际审计发现不足1,100个共同问题组，缩小规模并记录，不靠重复填满。
- 同一训练数据版本的子集在普通 SFT、E11、所有训练seed中保持一致。数据抽样seed与训练seed分开。
- 先用200训练题/版本完成小规模流程验证，再使用固定1,000题子集。1 epoch 子集训练可能不产生明显漂移；阴性结果保留，若增加训练暴露量，应对整组对照一致调整，不针对最终测试集挑选。
- E19 对实际训练的全部1,000题计算投影差，不能用另一个随机子集或包含开发题的数据均值代替。每题的基座自然回答跨三个数据版本复用，前提是实际渲染后的 prompt 完全一致。

### 3.2 题目与评分预算

既有每trait 20个提取题全部保留。E01 原设置为20题×5对指令×正负×10 rollouts，即每trait 2,000条、三个trait共6,000条回答；流程预检先用较少rollouts。无须新增题目。

建议将既有20个评估题按固定seed分成 **10题开发 / 10题最终测试**，提取题不参与最终行为评估。E02 使用开发题选层/强度，E06及后续行为主结果使用最终测试题；每题10 rollouts。只有10个测试题，统计时以问题聚类报告不确定性，不能把100个rollouts当作100个独立问题。分割文件冻结并公开，后续若改成原文20题全集口径应单独报告。

E02 先在32个block输出上扫描一个统一正向强度，再在候选层扩展正/负/零系数。零系数也走相同生成后端。可在开发集依据 coherence 约束选定强度范围，测试集只测冻结条件；原始向量范数与实际注入范数同时报告。

E06 使用 C.3 的8档提示，每trait全部跑；在生成开始前单独提取 prompt 激活。除总体相关性外，报告控制 system prompt 类别后的关系；不因总体相关性高就认定能预测细微变化。

MMLU 建议固定 **0-shot、按57个subject分层抽取共约1,000道test题**，计分使用同一模板下候选选项的条件概率，公开样本ID。不得称为完整 MMLU 分数。所有 checkpoint 和 steering 条件共用该子集；coefficient只在开发trait/coherence数据选，不用MMLU test调参。检查选项token化并使用一致的完整选项似然口径。

### 3.3 训练分支与规模上限

E08 基准矩阵为15次训练/seed。先seed0；正式关键对照建议增加seed1、2，其他训练seed作为预算扩展。每个adapter在三种trait上评估，不仅评估训练目标trait。

E11 建议分两步：

1. 对三个显式trait数据的II版本，各用对应向量做单层正向训练干预，比较小型系数网格与普通SFT；基座向量保持冻结。
2. 在Code II与Opinions II上，每次单独干预一个确实发生漂移的trait，扩到训练强度/Normal控制。所有分支从同一基座重新初始化相同seed的adapter。

E11 第一阶段建议每配置3个非零正向系数。若Code与Opinions三个trait都要干预，合计最多9个“数据×trait”组合×3系数＝27次新增训练/seed；**这不是15个数据集都乘3个trait再乘系数的全笛卡尔积**。普通SFT作零系数对照。Normal良性控制按开发阶段选定的各trait单个系数加入，另计训练数。

E10 可以直接在E08 checkpoint上扫反向系数，无须重训；主图可选上述9个组合中的有漂移者，选择规则在看最终测试分数前冻结。无漂移项列在总表，不把它们悄悄删除。E11 最终代表系数由开发数据选择；如果都不能恢复baseline，完整报告未成功，不据此无限扩大网格。

E09/E19 共用15个常规SFT观测/seed。三个版本和不同类别彼此相关，不能当作15个独立来源；报告按类别区分的散点、总体相关性、按类别聚类的不确定性。只有5类时跨领域泛化证据有限，不声称严格证明对任意新领域有效。多个seed不能虚增独立数据集数。

## 4. 源码适配清单

静态源码发现如下；本轮只更新规划，不改作者实现。建议保留 `upstream/` 原样，在外层 `src/`、`configs/`、`scripts/` 加适配层与实验入口，固定来源commit。

| 模块与证据 | 当前行为/风险 | 本轮适配 | 关联实验 |
|---|---|---|---|
| `requirements.txt` | Transformers4.52.3、Unsloth2025.5.9、vLLM0.8.5 等旧版固定依赖 | 创建独立环境，选支持Qwen3.5的版本并冻结；不直接安装整套旧requirements；先 HF+PEFT，暂不强制Unsloth/vLLM | 全部 |
| `utils.py:7`、`training.py:167`、`eval/model_utils.py:42` | 训练依赖FastLanguageModel，推理/合并依赖AutoModelForCausalLM | 共用模型adapter，显式选择文本或conditional-generation加载类；PEFT合并/卸载后验证模型结构；冻结视觉部分 | 全部 |
| `generate_vec.py:14` | 从顶层config读层数，收集hidden_states；未显式禁用autograd | 从text_config取参数；`eval`/`inference_mode`；流式累积block输出，不留全token激活 | E01/E09/E19 |
| `generate_vec.py:40` | 正负CSV按行索引共同过滤；正分>=50、负分<50，且两边coherence>=50 | 用trait/question/instruction/rollout显式键对齐；空集合报错；保留原repo筛选模式并记录。与论文文字的独立正负过滤、>50存在细微差别，勿默默混用 | E01 |
| `activation_steer.py:53`、`training.py:60` | 推测层路径；训练找不到hook会打印而非终止 | 用已验证text decoder层列表；检查shape/device/dtype/32个block；hook失败立即中止；PEFT包裹前后均验证 | E02/E10/E11 |
| `activation_steer.py:75` | `response`只改当前forward最后一个位置，`prompt`用seq_len==1判断decode | 明确定义生成的prefill末位与decode位置；训练teacher forcing时不能复用此response逻辑；显式mask与cache阶段区分 | E02/E10/E11 |
| `eval/eval_persona.py:240–261` | coef==0用vLLM，非零用HF；n_per_question控制temperature是否为0 | 全条件走同一HF路径；seed/temperature/rollouts独立配置，序列token与截断状态持久保存 | E01/E02/E06/E08/E10 |
| `sft.py:11,40` | assistant-only loss通过分隔符猜测；模板后额外追加EOS；Qwen3.5有thinking边界 | 明确生成和训练均non-thinking；构造精确assistant loss mask，检查实际label token；避免重复EOS，记录截断比例 | E08/E11 |
| `training.py:226` | 默认随机10%行级split，未显式传split seed | 使用外部固定question-group train/dev manifests，三个版本共享划分 | E08/E11/E19 |
| `training.py:44,133` | 正向向量注入当前整段序列；1-based层映射至block索引 | 默认保留作者all-token训练干预，与推理response范围区分；保持可微、冻结向量；检查重算hook和移除后的推理 | E11 |
| `config.py` / `judge.py` | import时强制要求OPENAI_API_KEY和HF_TOKEN，即使任务不需要judge | 凭据按后端惰性初始化；公共模型下载不强制HF token；不读取或输出密钥值 | 全部 |
| `judge.py` | 固定Chat Completions单token logprobs，无法直接接Codex文本 | 新增独立judge协议、缓存/并发/失败重试；区分原评分与Luna直接分数，保留trait/coherence rubrics | 全部行为评估 |
| `eval/cal_projection.py:29,80` | 计算单回答投影、原地写回数据，未完整实现跨版本分析 | 外置结果表，显式base/adapter身份；增加last-prompt shift、配对自然回答差值、数据级汇总与相关性报告 | E06/E09/E19 |
| 仓库缺少实验编排/完整MMLU实现 | 手工脚本固定旧模型和层，无法一次复现所选矩阵 | 配置驱动DAG、稳定run ID、断点续跑、MMLU hook评估、Slurm脚本和完成标记 | 全部 |

### 4.1 新模型特有的细节

已检查 [Qwen3.5-4B 官方模型卡](https://huggingface.co/Qwen/Qwen3.5-4B) 和 [Transformers Qwen3.5实现](https://github.com/huggingface/transformers/blob/683b721971417b3b2c64fba9001f525607547e5a/src/transformers/models/qwen3_5/modeling_qwen3_5.py)。这些是静态依据，实际环境尚未加载模型。

模型文本部分32层、hidden size2560，混合linear/full attention。完整条件生成模型的候选层路径为 `model.language_model.layers`；文本CausalLM实现则可为 `model.layers`。PEFT再包裹后路径会改变，不能硬编码唯一字符串；文本专用加载是否能正确读取该checkpoint须实际验证，不把它当作已经成立的结论。

重要风险是“最后一层hidden_states”等价性：源码有最终norm，通用hidden_states收集与block输出不应不经验证直接混用。所有向量、投影、steering统一取**第ℓ个block输出、最终norm之前**；blockℓ对应Python索引ℓ−1，embedding不当成一个候选层。以同次forward的hook输出检查一致性。

训练优先BF16 rs-LoRA，rank32/alpha64/lr1e-5，起点为原论文参数。原target_modules以旧attention命名为基础，不完整覆盖Gated DeltaNet。先枚举实际模块，只训练文本层，显式记录linear/full attention各匹配哪些LoRA模块及参数量；不能静默只适配部分层并称与旧LoRA设置等价。初版不把量化、不同内核和更换优化器混在同一个消融中。

生成、E06 prompt投影、E09 shift、E19 teacher forcing均用完全一致的non-thinking chat template。保存token IDs与mask，检查prompt-only与prompt+answer边界，拒绝空回答/全padding均值产生NaN。基座自然回答在评分前先落盘，后续judge可独立重跑，不占用GPU等待远程评分。

E11 训练正向添加undesired向量，推理移除；不要把训练符号写成抑制方向。普通SFT和预防训练使用相同初始化、数据顺序、有效batch和暴露量，视觉模块冻结。对gradient checkpointing重算是否保持相同hook、对梯度是否能正常传播，需在Slurm内的小步训练中验证。

## 5. 验证顺序与完成条件

1. **存储与环境**：确定可写持久大存储，锁模型revision/依赖，准备日志与数据manifest；不用登录节点加载模型。
2. **模型适配预检**：基座无干预和零系数结果一致；hook能测得注入差；32层输出形状正确；移除hook恢复；mask与assistant-only labels可人工审查。
3. **E01/E02**：生成和judge解耦；每trait报告有效正负样本量及被过滤原因；开发集选层、向量符号与coherence检查后冻结。
4. **E06**：将论文C.3原提示转存为文件并核对；跑投影与回答关系，保存prompt分组。
5. **E08 pilot → 正式子集**：先常规SFT；检查确有训练更新、loss与labels正常、checkpoint可重载；再完成15份矩阵。
6. **E09/E19**：共享基座prompt投影与自然回答缓存；验证单位向量归一化、样本配对及训练数据覆盖；先输出15点散点与数据表，再算相关性。
7. **E10/E11**：仅在共享基线建立后追加干预；主指标必须同时包含trait、coherence、MMLU，报告副作用和失败条件。

所有重计算在 `qdj_project_owned1 / spgpu2` 的Slurm分配中执行；提交前检查资源。初步按1张L40S、约60 GB CPU内存规划，batch和时限由预检确定。后续实验遵循 `docs/experiments.md` 与独立详情文档约定，本轮尚无实验结果。

## 6. 最新存储与 judge 决定

用户已选定 `gpt-5.6-luna` 为主judge。已实测两个个人scratch目录可写，qdj根fileset余量8.08 TiB、engin根fileset余量88.45 TiB；建议活动实验放qdj owned1个人目录。scratch可支持实施，但长期归档仍需持久存储。

以下保留原先问题的背景，judge选择已经解决；可写活动存储已经找到，未确定的是长期归档位置。

## 7. 当前实施决定与待预检项

主judge已确定为GPT-5.6-Luna，并按用户指示取消校准；直接使用作者rubric与固定过滤阈值。活动数据、环境和adapter使用qdj owned1个人scratch；长期归档路径后续落实，不阻塞框架实现。

已完成框架代码与8份实验策略，见[运行手册](../runbook.md)。尚未安装专用模型环境、下载权重、运行真实Luna请求或训练；这些属于后续预检与实验执行。配置固定每类每版本1000训练+100开发问题组，提供200题pilot；评估题10开发/10测试。

需要实际预检的技术问题仍包括Qwen3.5加载与模板、DeltaNet LoRA目标、cache/gradient checkpointing，以及模型是否产生足够的训练漂移。代码检查不能替代这些实际验证。
