# is-hil-sql-pilot：9B 模型在 HiL-Bench SQL 上的可行性与激活采集

状态：**实现完成（2026-11-16），smoke 运行中**；20 题子集尚未提交。实现细节与已核实项见下方"实现记录"。假设与变体目录见 [overview](../overview.md)。

## 目标

1. 判断小模型在 HiL-Bench SQL 公开集上是否可用（任务成功率、提问行为是否退化）。
2. 采集所有层、多个位置的决策点激活，供后续离线比较提取方式、读取方式和选层，不必重跑 rollout。
3. 给出 H1（可读出）、H2（识别 vs 行动）的初步证据。

本 study 先跑子集。闭环 steering 不在首轮；单步扫描与闭环确认在采集结果出来后作为新的证据小节加入本文件。

## 已定的决定（2026-11-16）

| 项 | 决定 |
|---|---|
| 采集范围 | 全部层、全部六个位置、全部标签都采集 |
| 规模 | 先跑子集（见"规模"），全量是否跑在回顾后决定 |
| 可行性指标 | 子集跑完后计算并与用户一起回顾、确认门槛；首轮不预设通过线 |
| 模拟用户 | Claude Code 中最便宜的模型（Haiku），通过 headless CLI 调用 |
| 模型 | Qwen3.5-9B，thinking 开启；备选 Qwen3-8B |
| 闭环判定（2026-11-16 用户决定） | 宽松 rubric（`simulator.py` 的 `LENIENT_RUBRIC`）。理由：官方 prompt + Haiku 只接受 32% 的 registry 示例问题（见 smoke 校准）。官方 rubric 保留用于离线重判。分数标为"HiL SQL（Claude 宽松判定）" |
| 步数上限（同上） | 100，与官方 SQL agent 一致 |
| 第一轮条件（同上） | 先观察 9B 行为：20 题 × {blocked_ask（官方 prompt）、blocked_ask_prompted（官方 prompt + 提问指令段 `ASK_PROMPT_PARAGRAPH`）、fullinfo_ask（过度提问对照）} × 1 seed = 60 个 unit（unit = 一条完整轨迹）。no-ask 条件、部分放回、等长无关文本都推后。blocked 的两个条件都做 full-info 配对前向 |
| HiL 的定位（同上） | 倾向作为验证集而非提取集：方向优先在更干净的成对数据（When2Call、QuestBench、CLARITI）上提取，在 HiL 上检验读（投影是否在 blocker 暴露时升高、得到 resolution 后下降）与写（注入后是否提问）。渐进式 blocker 适合之后做按步门控的动态 steering |
| 环境（同上） | 独立环境 `${PV_WORK}/venv-is`（Python 3.12，`scripts/bootstrap_info_seeking.slurm`），torch／transformers 与项目锁定版本相同，加 fla 0.5.2 与 causal-conv1d 1.7.0；运行时若快速 kernel 未绑定则直接报错（`require_fast_kernels`）。共享的 venv／venv-fast 不改动 |

模型选择理由：两者 bf16 都能放进单张 L40S（48 GB）。选 Qwen3.5-9B 是因为仓库现有流程（模板、hook、EOS、preflight）已在同系列 Qwen3.5-4B 上验证，且能力预期更强，更可能离开任务成功率的地板。代价是与文献的可比性：HiL-Bench 的小模型结果是 Qwen3-32B，CLARITI 是 Qwen3-8B。若 9B 的工具调用格式在 preflight 中不稳定，换 Qwen3-8B 并在此记录。待核实：9B 的 revision、层数、hidden size、thinking 模板与 `</think>` token、推荐采样参数。

## 数据与环境

- HiL-Bench SQL 公开集 100 题，SQLite，工具：业务逻辑检索、schema 探索、SQL 执行、`ask_human`。来源、哈希与偏差见"实现记录"。数据许可：HF 数据卡与仓库都未写明，仍未核实。
- 外部检出与数据在 `${PV_WORK}/external/`、`${PV_WORK}/data/hil-bench-sql/`，不放 home。

## 模拟用户（Claude Haiku）

- **Claude 只做分类，不写回答**：输入为官方判定 prompt（blocker ID、描述、示例问题，不含 resolution），输出 blocker key 或 null；环境原样返回 registry 中的 resolution 或 "irrelevant question"。
- 官方判定很严：例如自动拒绝"定义型"问题（只引用题面术语）和"我假设 X，对吗"型问题，要求 95% 置信；它同时要求"展示已做的分析"与"不得包含背景或假设"，两条互相冲突。闭环先用官方严格版；`simulator.py` 已带宽松 rubric（`LENIENT_RUBRIC`），用于离线重判同一批问题。是否让闭环也用宽松版，由用户在子集回顾时决定。
- 缓存键为（rubric、模型、effort、完整 prompt）的哈希；每次记录解析后的模型 ID、费用、耗时、解析方式。
- 报告口径：分数标为"HiL SQL（Claude 判定）"，不称官方分数。子集跑完后人工抽查约 50 个（问题、判定）对，报告一致率。

## 实现记录（2026-11-16）

代码：`src/info_seeking/`（official、data、env、sql_worker、simulator、agent、trajectory、probe_analysis），入口 `scripts/hil_sql_pilot.py`（stage：prepare／init／preflight／run／summarize／probe），作业 `scripts/hil_sql_pilot.slurm`，配置 `configs/info-seeking-hil-sql.json`，合成测试 `tests/test_info_seeking.py`。

**官方来源（全部钉 SHA-256，见 `official.py` 的 `PINNED_FILES`；文件留在 `${PV_WORK}/external/`，不复制进仓库，因为上游仓库没有顶层许可）**

| 来源 | 用途 |
|---|---|
| `hilbenchauthors/hil-bench` commit `c5a656e4` | SWE-agent 工具 config（函数 schema）、Qwen ask 配置的 system／instance／observation／格式错误模板、full-info jinja 模板 `problem_full_info.jinja2` |
| HF `ScaleAI/hil-bench` parquet（sha `260c245b…`） | 100 道 SQL 题的问题、business info、ground truth、blocker registry；数据库与 schema CSV 从 HF bucket `hil-bench-sql-artifacts` 按题下载（全量 19.8 GB，只下子集） |
| ECR 镜像 ask-human 层 `server.py` | 判定 prompt 逐字使用（AST 解析 f-string 重建，不执行该文件）；`irrelevant question`、`can't answer (perhaps transient hiccup)`、每个 blocker 最多回答 2 次、少于 3 字符直接判 irrelevant |
| ECR 主镜像 `sql_server.py`、`business_info_server.py` | execute_sql 只读、200 行 CSV 截断、非 SELECT 返回 `Error: non-SELECT query`；business info 用 all-MiniLM-L6-v2、top 5、按 database_name 过滤 |
| Harbor `test_verify.py` | 通过判定直接导入官方 `compare_pandas_outputs` 与只读执行（哈希校验后导入） |

**与官方设置的差异（报告时必须标注）**

- 模拟用户：Claude Haiku（解析为 `claude-haiku-5-5`），论文为 Llama-3.3-70B、temperature 0.05。CLI 无法设温度；`--effort low`；隔离参数为无工具、`--strict-mcp-config`、`--setting-sources ""`、空临时 cwd、自定 system prompt。`--bare` 会跳过登录凭据，不可用；本机的 managed CLAUDE.md 无法关闭，判定上下文里会带上这段 HPC 策略文本（约 2k token，与任务无关）。
- 判定 JSON：官方 null 示例带尾逗号（`"blocker_key": null,`），官方解析器遇到会返回 CANT_ANSWER。我们容错解析（去尾逗号、正则兜底），每次记录 `parse_mode`，可事后统计。仍无法解析时不重问，直接 CANT_ANSWER（与官方一致，只有 CLI／网络失败才重试）；合法 JSON 但缺 `blocker_key` 或非字符串时按未匹配处理（官方 `result.get`）。
- Precision 两种都记：harness 定义（已解决的不同 blocker 数 ／ 问题数）与论文定义（被判相关的问题数 ／ 问题数，含被 2 次上限截掉的）。条件汇总用 micro（先对计数求和再算 P／R／F1，与官方 `compute_hil_metrics` 一致），macro 作附加列。
- 格式错误：错误码与文字按 SWE-agent `FunctionCallingParser`（missing／multiple／invalid_command／missing_arg／unexpected_arg，先查缺参再查多余参数，忽略 `ENDOFSQL` 参数），提示模板用官方 Qwen 配置。requery 语义同 `forward_with_handling`：临时历史只含最近一次失败输出和错误提示，最多 3 次；改正后失败的回合不进入历史，也不计步数。execute_sql／submit_sql 的参数按 SWE-agent heredoc 方式截到第一个 `\nENDOFSQL`。每次尝试（含失败）都记录为一个决策点（`attempt` 字段）。与模板重渲染的差异：SWE-agent 的错误提示是一个真正的 user 回合，在 Qwen3.5 模板下会移动 `last_query_index`，重渲染时会丢掉失败回合及之前所有 assistant 回合的 reasoning；我们按 token 追加，这些 reasoning 都保留。
- business info 检索：用 transformers 复现 MiniLM（mean pooling + L2 归一化，最长 256 token，revision `1110a243`），精确余弦 top 5；约 30 条文档时与 Chroma 的排序一致（理论上，未逐条对照）。
- execute_sql 超时 120 秒（官方 1200 秒）；验证子进程超时 600 秒。
- 系统 prompt：ask 条件用官方 Qwen ask 配置原文；no-ask 条件用同一原文删去 ask_human 段落（官方 baseline 用另一份更长的 default 配置）。这样 blocked 与 full-info 在同一 ask 设置下只有 instance 文本不同。full-info 文本用论文 pipeline 的 jinja 模板（与 Harbor 的 instruction.md 格式不同）。
- 步数上限 100（与官方 SQL agent 一致；smoke 时为 40），每步最多生成 8192 token，上下文上限 65,536（与官方 max_input_tokens 相同），剩余预算不足 1024 时结束。
- 验证超时 2500 秒（官方每条查询 1200 秒，两条查询）。验证子进程失败记 `verify_error` 并在汇总中单列，不静默当作 0。SQL worker 的导入失败直接中止该 unit，不作为观察返回给模型。
- 采样：Qwen3.5 卡片的 thinking 模式"精确编码"设置，T=0.6、top_p=0.95、top_k=20；presence_penalty 在 HF generate 中不可用（卡片该设置本身为 0）。
- 历史以 token ID 追加方式维护：模型看到的是自己生成的原始 token，工具返回按模板格式追加。格式错误提示作为 user 消息追加，这与官方模板在下一轮重渲染时会丢弃之前 reasoning 的行为不同（我们不丢弃）。

**采集实现**：每次尝试生成后对"前缀 + 本次输出"做一次 teacher-forced 前向，在 32 个 block 输出上取六个位置（定义见 `agent.py` 文件头），存为 `activations.safetensors` 的 `acts [决策点数, 6, 32, 4096] bfloat16` 与 `valid [决策点数, 6]`（bf16 避免 fp16 对残差流大值溢出）。`act_first` 与工具打分只在 `</think>` 闭合后取。

工具选择打分：Qwen 的分词把 `=` 与部分工具名粘在一起（`=get`、`_database`…；`ask_human` 等是 `=`、`ask`），所以不能用"工具名首 token 概率"。改为在 `<function` 的最后一个 token 处截断前向、保留 KV cache，用 cache 副本逐 token teacher-forcing 计算每个工具完整续写 `=<name>` 的 log 概率（`tool_logprobs`），对所有工具都可比，不受模型实际选择的影响。preflight 用全序列 teacher forcing 交叉核对该值。

blocked + ask 条件额外做一次配对前向：同一前缀与输出，只把 instance 文本换成 full-info 版本（`paired_acts`，off-policy，只用于 v_miss 的严格配对对比）。

**第二次代码审查（2026-11-16，独立 subagent，含 requery 循环与续写打分）**：确认 requery 次数与"只保留最近一次失败输出"同 SWE-agent，解析错误码与官方一致，续写打分只在主前向挂 hook、位置不越界。已修：Slurm 在已有 run 上执行该 run 冻结的入口脚本（此前只有 `src/` 被冻结，入口脚本仍用仓库当前版本）；`info_seeking.runs` 改为在 `init`／`prepare` 内延迟导入，使旧 run（冻结代码里没有 `runs.py`）的其他 stage 仍可运行。

**可追溯性**：`init` 把 `src/info_seeking`、复用的 `persona_repro/{__init__,common,model}.py`、入口脚本与 slurm 冻结到 `runs/<id>/source/`；在已有 run 上的所有 stage 都从这份冻结代码导入，SQL／验证子进程也用它。非 smoke run 要求这些路径在 git 中干净；脏树只能以 `--purpose smoke` 初始化。官方文件和 7 个工具 config 都钉哈希，不匹配即报错。

**合成测试**：21 项通过（作业 66225157）；覆盖工具调用解析与 SWE-agent 错误码、ENDOFSQL 处理、判定输出容错解析（含缺 key）、ask_human 上限／解析失败／registry 外 key、两种 precision、只读 SQL 与截断、子集分层（按 blocker 数量分层，再在数据库间轮流抽取）、判定 prompt 重建与官方字符串。

**代码审查（2026-11-16，独立 subagent）**：确认无 resolution 泄漏、工具语义与官方一致、位置索引正确。已修复：工具名打分位置（上段）、Ask 汇总改 micro、判定解析失败不重问、格式错误码与 requery 语义、子进程显式 PYTHONPATH、冻结代码导入、`.tmp` 目录排除、未闭合 think 内的 tool call 不计、`data_format` 缺列、bf16 存储、工具输出里的特殊 token 字符串按普通文本分词。

**环境问题与处理**：`venv-fast`（Python 3.10）中 fla 0.5.2 导入失败。原因是 Python 3.10 的 `inspect.getsourcelines` 遇到装饰器里的 lambda 会提前截断，Triton 找不到 kernel 的 `def`（`scripts/accelerate.slurm` 的注释已指出需 Python ≥ 3.11）。transformers 因此静默退回 PyTorch 参考实现：结果正确但慢，preflight 单步约 12.6 token/s。smoke run 用的是这个回退路径。子集起改用独立环境 venv-is（见上表）。

**preflight 发现（smoke-is-hil-sql-qwen35-9b-20261116-133313，旧代码版本）**：计算节点上 Claude CLI 可用（每次判定约 3–4 秒）；模板逐 token 一致（我们的追加方式 = 官方模板渲染）；Qwen3.5-9B 的工具调用格式解析正常。官方判定 prompt 下，Haiku 把该题 registry 自带的示例问题（"Which sets should I consider as the early and later sets?"）判为不相关，理由是"未展示分析"。即本地判定可能比 benchmark 设计意图更严，系统性校准见 `calibrate-judge`。

## 条件

| 条件 | 内容 | 用途 |
|---|---|---|
| blocked + ask | 原任务，开启 ask_human | 主条件；Ask-F1、recall |
| full-info + ask | resolution 全部放回，仍开启 ask_human | 过度提问率；v_miss 的条件对比 |
| full-info，无 ask | resolution 全部放回，关闭 ask_human | 任务成功率上限 |
| blocked，无 ask | 原任务，关闭 ask_human | 地板；猜测推进时的激活 |

## 规模

| 阶段 | 任务 | 条件 × seed | 目的 |
|---|---|---|---|
| 试跑 | 2 题 | 4 × 1 | 校正每步耗时、每决策点存储、格式错误；验证模拟用户与采集 |
| 子集 | 20 题 | 4 × 1 | 可行性指标；首批激活与 H1／H2 初步分析 |
| 全量（待决定） | 100 题 | 4 × 3 | 回顾子集后决定是否跑、是否调整条件 |

子集 20 题按 blocker 类型与数量分层、固定随机种子抽取，任务 ID 列表写入 run 的 `tasks/` 并冻结。20 题不足以按任务划分出可靠的 test，子集上的 probe 结果只算初步。

## 可行性指标（子集后回顾，不预设通过线）

- full-info 无 ask 的 pass@1。
- blocked + ask 下至少提问一次的任务比例、每题问题数、Ask precision／recall／F1。
- full-info + ask 下的提问率（过度提问）。
- 工具调用格式错误率、达到步数上限的比例、每条轨迹步数与 token 数。

回顾时要回答的三个问题：任务成功率能否作为终点指标；自然提问率是否足以做"提问 vs 未提问"对比（否则改用正反 system prompt 诱导）；是否需要先修 scaffold。

## 采集内容

**决策点** = 模型每一次产生动作（任意工具调用或提交）之前的状态。

激活（每个 block 输出的残差流，全部层，float16，层号 1 起）：

| 键 | 位置 |
|---|---|
| `pre` | 生成前最后一个输入 token |
| `think_end` | `</think>` token |
| `act_first` | 动作（tool call）的第一个 token |
| `obs_mean` | 最近一次工具返回的 token 均值 |
| `think_mean` | 本步 reasoning token 均值 |
| `input_mean` | 全部输入 token 均值（每条轨迹第一步，以及每次 ask 得到回答后的下一步） |

标签与元数据（每决策点一行 JSONL）：

- 任务 ID、条件、seed、步序号、前缀 token 数。
- 本步动作类型：ask_human／其他工具／提交／格式错误；ask 的问题文本。
- 工具名位置上各工具名首 token 的概率（含 ask_human），作为单步扫描的无干预基准。
- 严格判定结果（blocker ID 或 irrelevant）；宽松判定另存一列。
- 到本步为止已解决的 blocker 集合、剩余数量。
- 轨迹级：是否通过、Ask precision／recall／F1、总步数、格式错误数。
- 完整前缀的 token ID 与文本（含模型自己的 reasoning），供之后在 on-policy 前缀上做单步 steering 重放。

采集阶段不计算任何方向；方向由离线脚本生成并记录向量 hash。

存储估算待试跑校正：每决策点 = 层数 × 6 × hidden × 2 字节；按 36 层、4096 维约 1.8 MB。子集约 80 条轨迹 × 约 15 步 ≈ 1200 决策点 ≈ 2 GB；全量约 32 GB。

## 实现方案

**步骤 0：读 harness（登录节点可做，无 GPU）**
- 检出仓库到固定 commit，读 SQL 任务格式、四个工具的实现、blocker registry、full-info 的构造方式、步数上限、判定 prompt、许可。
- 决定 scaffold：若 SQL 工具是可直接调用的 Python 函数，写自己的最小 agent 循环并复用官方工具与 prompt（首选，token 位置和工具调用解析都在自己控制下）；若与 SWE-agent 耦合过深，则用 `ModelRuntime` 包一个 OpenAI 兼容的本地服务供官方 harness 调用，在服务端采集。把选择和理由写回本文件。

**步骤 1：代码**（新包 `src/info_seeking/`，复用 `persona_repro.model.ModelRuntime`、`common`）

| 文件 | 职责 |
|---|---|
| `hil_env.py` | 载入任务与 registry；四种条件的 prompt 构造；工具执行；通过判定 |
| `agent_loop.py` | 多轮循环：生成 → 解析 tool call → 执行／ask → 追加观察；步数上限；格式错误处理 |
| `capture.py` | 每步生成后，对"前缀 + 本步输出"做一次 teacher-forced 前向，取六个位置的全层激活与工具名位置的 logits |
| `simulator.py` | `ClaudeSimulator`：CLI 子进程、缓存、重试；严格与宽松两套 rubric |
| `probe_analysis.py` | 离线：按层 × 位置的 probe AUC、2×2 表、方向间余弦 |

- 采集用重放前向而不是在生成时挂 hook：位置选择精确、实现简单，每步多一次前向。需用 `scripts/check_runtime_interactions.py` 的思路确认重放激活与带缓存生成时的激活一致（在容差内）。
- 入口 `scripts/hil_sql_pilot.py` 与 `scripts/hil_sql_pilot.slurm`，配置 `configs/info-seeking-hil-sql.json`（模型 revision、thinking、采样器、seed、步数上限、每步 max_new_tokens、条件、任务列表、模拟用户设置）。通过 `scripts/submit.sh` 提交，`qdj_project_owned1`／`spgpu2`，1 GPU、60 G。
- 轻量合成测试（不加载模型）：tool call 解析、位置索引、模拟用户 JSON 解析与缓存、指标计算。测试经 `scripts/checks.slurm` 运行，不在登录节点跑。
- run 目录 `${PV_WORK}/runs/<run_id>/` 按现有约定冻结 `config.json`、`manifest.json`、`source/`、`tasks/`，记录实现 commit 与各 hash；断点续跑以（任务、条件、seed）为单位。

**步骤 2：preflight 与试跑（GPU，短作业）**
- 载入 Qwen3.5-9B，核对层数、hidden size、thinking 模板、stop token、tool call 格式；填写上文"待核实"项。
- 2 题 × 4 条件端到端，检查激活形状、位置索引抽查、模拟用户往返、存储与耗时。

**步骤 3：子集运行**，完成后写完成标记 `logs/<name>_<jobid>.done.json`。

**步骤 4：离线分析与回顾**
1. 可行性指标表。
2. H1：各层 × 位置的 probe AUC，分别用条件间（blocked vs full-info）与轨迹内（回答前 vs 回答后）标签；按任务划分，打乱标签对照。
3. H2：2×2 表（probe 高／低 × 提问／未提问），只统计有未解决 blocker 的决策点。
4. v_ask 与 v_miss 按层的余弦相似度；均值差、probe 权重、PCA、稀疏维度掩码四种方向在同一层／位置上的对比。
5. 严格 vs 宽松判定的 precision／recall 差；人工抽查一致率。
6. 与用户回顾可行性指标，决定全量、换模型或改 scaffold。

## 后续证据小节（占位）

- 单步 teacher-forced 扫描：层 × 位置 × 系数 → ask_human 概率的变化，blocked 与 full-info 决策点分开报告。
- 闭环确认：无干预、prompt 指令基线、无条件 v_ask、probe 门控 v_ask、随机方向，各取单步扫描的前 2–3 个配置。

## Run 记录

| run ID | 内容 | 实现 commit | 状态 |
|---|---|---|---|
| smoke-is-hil-sql-qwen35-9b-20261116-133313 | 旧代码 preflight（审查前） | 5ec8675 + 未提交改动（smoke） | 仅 preflight，已被下一行取代 |
| smoke-is-hil-sql-qwen35-9b-20261116-135913 | 审查修复后：preflight、2 题 × 4 条件、20 题判定校准 | 5ec8675 + 未提交改动（smoke） | preflight 与校准完成；8 个 unit 运行中（作业 66225364／66225365） |

**smoke 初步观察（仅供核对流程，不作结论）**

- preflight 全部通过：我们追加的 token 与官方模板渲染逐 token 一致；`pre` 位置在有无后续 token 时激活完全相同（差 0.0）；7 个工具的续写打分中，cache 打分与全序列 teacher forcing 一致（−0.0162 vs −0.0145，bf16 误差）；激活无溢出（|max| 125）。
- 判定校准（20 题的全部 260 个 registry 示例问题，作业 66225366）：

  | rubric | 判到正确 blocker | 拒绝 | 判错 blocker |
  |---|---|---|---|
  | 官方 prompt + Haiku | 32.3% | 67.7% | 0% |
  | 宽松 rubric + Haiku | 100% | 0% | 0% |

  官方 prompt 下有 49 次输出带尾逗号，经容错修复后才可解析；官方解析器遇到这种情况会返回 CANT_ANSWER，但这 49 次都是拒绝。论文报告其判定在人工标注对上的 recall 为 91%，所以本地严格判定明显更严。
- 第一个 unit（public_sql_48，blocked + ask）：40 步、527 秒，0 次提问，没有提交即耗尽步数，0 次格式错误。每步 log P(ask_human) 约在 −13 到 −31 之间，即自然提问率可能接近 0。
- 8 个 unit 全部完成（每条 6–18 分钟，PyTorch 回退路径）。轨迹阅读（2026-11-16）：
  - **推理里从未考虑提问**：8 条轨迹的 reasoning 中没有一次提到 ask_human、询问分析师或请求澄清，包括有 ask 工具的 4 条。
  - **识别到了歧义，但自己选解读**。public_sql_63（thrombosis）blocked + ask：从第 1 步起反复写"这看起来矛盾""could mean""17–19 只是启发式、不是官方定义"，列出多种解读，用 business info 和数据逐一试，最后自选"两种结果都出现过 + 按年份差 17–19 岁 + 1990–1993 有检查记录"。这与 registry 的 resolution（最近一次检查为 0、17 岁 9 个月到 18 岁、按 First Date）三处都不同。public_sql_48（card_games）blocked + ask：明确写"user asked without specifying how to divide them"，然后自定默认"按发布日期中位数切分""convertedManaCost 大概就是 balanced average mana cost"，之后反复验证自己的选择，直到步数用完。
  - **"做对"是数值碰巧一致**。public_sql_63 的 blocked + ask 与 blocked + noask 两条的 SQL 和 GT 不同、解读也不同，但 `COUNT` 结果都等于 GT（2）。该库插入了几条人造病人（ID 999995–999999）专门区分不同解读，计数很小，不同解读容易得到相同数字。官方验证只比较输出，所以 blocked 条件下的 solve 不能当作"blocker 被正确处理"的证据。
  - **full-info 也会失败**：public_sql_48 的 full-info 两条都没做对（ask 版提交了、noask 版用完步数），即使信息给全，这道题的 SQL 对 9B 也偏难。
  - **Haiku 离线标注试跑**（`hil_sql_pilot.py annotate --target-run …`，结果在该 run 的 `analysis/annotations/`；用仓库当前代码，记录 commit 与 `annotate.py` 哈希）：逐步"是否意识到缺失／歧义、对应哪个 blocker、原文证据、处理方式（自由描述）"，以及逐 blocker"提交的 SQL 是否按 resolution 实现"。8 个 unit、约 300 次调用，无失败。意识到的步数占比 blocked 条件明显高于 full-info（48 题 27/40、16/40 vs 12/36、14/40；63 题 20/37、23/36 vs 5/24、8/40）。实现判定能区分数值碰撞：63 题 blocked 两条 solve = 1 但三个 blocker 全判"no"；full-info + ask 判"partial／yes／yes"。处理方式在 blocked 条件下集中在"列出解读、查 business info、查数据、自选默认"，没有任何"问人"。暴露的标签问题：full-info 下模型按给定的 clarification 行事，也常被描述为"picks its own default"，所以之后需要把"用给定信息解决"与"自选默认"分开标；blocker ID 偶有不规范写法，已在代码中归一化；"意识到"的判定尺度（例如开头列出要弄清的概念算不算）尚未定。
  - **加"拍板"标签（v2）**：每步另标 `commits`（是否对已注意到的问题定下一种解读并继续用）、`basis`（own_default／business_info／data／provided_clarification／human_answer）、`commit_blockers`。`basis = own_default` 即"在猜"。修正了一个 bug：此前标注者看到的是原始题面，full-info 条件下看不到模型实际收到的澄清，导致"照澄清做"被标成 own_default；现在给标注者的是模型实际看到的题面。结果：blocked 条件下的拍板几乎全是自己猜（48 题 17/18、9/12；63 题 11/12、14/14），full-info 下以"照给定澄清"为主（48 题 7/10、4/7；63 题 4/4、3/5）。blocked 中还有不在 registry 里的猜测（如 card_games 里自行剔除 Gleemax 的异常 mana cost），记为 other。可用于之后提取"在不确定中拍板"（v_guess）的方向：同一 blocked 条件内，拍板步 vs "已注意到但仍在查"的步，另以 full-info 的"照澄清拍板"步为对照；需控制步数位置，并检查与 v_miss 的相关。仍有噪声：个别"重新考虑"的步被标为拍板；basis 偶尔写成复合字符串。
  - 对设计的含义：① 自然的"提问 vs 不提问"对比在这个 prompt 下不存在，`blocked_ask_prompted` 是必要的；② reasoning 文本本身提供了不依赖工具的**识别标签**（"指出缺失／歧义并说明自选的默认"），可以逐步标注，作为 v_miss probe 的行为侧标签，与条件标签对照；③ 任务成功率之外需要一个"是否按 resolution 实现"的逐 blocker 判定（例如让 Claude 对照 resolution 检查提交的 SQL），否则会被数值碰撞误导。

## 限制

- 模拟用户不是论文的 Llama-3.3-70B，分数与论文不可直接比较。
- 公开 SQL 集只有 100 题；结论需在第二 benchmark 上复核。
- HiL-Bench 没有原生的无 blocker 任务；full-info 是"已解决"对照，表征证据同时依赖轨迹内对比。
- 论文中没有 ≤10B 模型的结果，难度评级是推断。
