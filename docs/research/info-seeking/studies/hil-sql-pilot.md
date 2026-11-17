# is-hil-sql-pilot：9B 模型在 HiL-Bench SQL 上的可行性与激活采集

状态：**20 题子集完成**（run `subset-is-hil-sql-qwen35-9b-20261116-210747`）；离线重判、分级意识标注、逐 blocker 漏斗已完成。是否跑全量待定。假设与变体目录见 [overview](../overview.md)。

**主要结论**

- 9B 能用：full-info pass@1 = 0.70；自然条件下 40% 的 unit 会提问，加提问指令后升到 90%。
- 几乎每个 blocker 都被意识到（76/80），但只问到 27 个，其余主要靠自己猜。识别与行动是分开的（H2）。
- 拿到信息时逐 blocker 实现准确率约 70%，自己猜只有 6–8%。
- 这个子集的 KB 从不含完整答案，"自己检索"不能单独解决 blocker。
- HiL 适合作验证集：blocked 条件内几乎没有"没意识到"的负例，结构标签的 probe 只读到题面文本或时间顺序。

## 目标

1. 判断小模型在 HiL-Bench SQL 公开集上是否可用（任务成功率、提问行为是否退化）。
2. 采集所有层、多个位置的决策点激活，供离线比较提取方式、读取方式和选层，不必重跑 rollout。
3. 给出 H1（可读出）、H2（识别 vs 行动）的初步证据。

## 已定的决定（2026-11-16）

| 项 | 决定 |
|---|---|
| 模型 | Qwen3.5-9B（revision `c2022362`，32 层，hidden 4096），thinking 开启。理由：bf16 放得进单张 L40S；仓库流程已在 Qwen3.5-4B 上验证。代价是与文献的可比性（HiL-Bench 的小模型是 Qwen3-32B，CLARITI 是 Qwen3-8B） |
| 模拟用户 | Claude Haiku，headless CLI |
| 闭环判定 | 宽松 rubric（`simulator.py` 的 `LENIENT_RUBRIC`）。官方 prompt + Haiku 只接受 32% 的 registry 示例问题；官方 rubric 用于离线重判。分数标为"HiL SQL（Claude 宽松判定）" |
| 步数上限 | 100，与官方 SQL agent 一致 |
| 第一轮条件 | 20 题 × {blocked_ask（官方 prompt）、blocked_ask_prompted（加提问指令段 `ASK_PROMPT_PARAGRAPH`）、fullinfo_ask（过度提问对照）} × 1 seed = 60 个 unit（unit = 一条完整轨迹）。blocked 的两个条件都做 full-info 配对前向。no-ask、部分放回、等长无关文本推后 |
| HiL 的定位 | 验证集。方向在更干净的配对数据上提取，在 HiL 上检验读（投影是否在 blocker 暴露时升高、得到回答后下降）与写（注入后是否提问） |
| 环境 | 独立环境 `${PV_WORK}/venv-is`（Python 3.12，`scripts/bootstrap_info_seeking.slurm`），torch／transformers 与项目锁定版本相同，加 fla 0.5.2 与 causal-conv1d 1.7.0；快速 kernel 未绑定时直接报错（`require_fast_kernels`） |
| 采集范围 | 全部层、六个位置、全部标签 |

## 数据、模拟用户与官方设置

- HiL-Bench SQL 公开集 100 题，SQLite，工具：业务信息检索、schema 探索、SQL 执行、`ask_human`。数据许可：HF 数据卡与仓库都未写明。
- 外部检出与数据在 `${PV_WORK}/external/`、`${PV_WORK}/data/hil-bench-sql/`。
- **Claude 只做分类，不写回答**：输入为判定 prompt（blocker ID、描述、示例问题，不含 resolution），输出 blocker key 或 null；环境原样返回 registry 中的 resolution 或 "irrelevant question"。缓存键为（rubric、模型、effort、完整 prompt）的哈希。
- 官方判定很严：自动拒绝"定义型"问题和"我假设 X，对吗"型问题，要求 95% 置信；同时要求"展示已做的分析"与"不得包含背景或假设"，两条互相冲突。

**官方来源**（全部钉 SHA-256，见 `official.py` 的 `PINNED_FILES`；上游无顶层许可，文件不复制进仓库）

| 来源 | 用途 |
|---|---|
| `hilbenchauthors/hil-bench` commit `c5a656e4` | 工具 config（函数 schema）、Qwen ask 配置的 system／instance／observation／格式错误模板、full-info 模板 `problem_full_info.jinja2` |
| HF `ScaleAI/hil-bench` parquet（sha `260c245b…`） | 100 道 SQL 题的问题、business info、ground truth、blocker registry；数据库从 HF bucket `hil-bench-sql-artifacts` 按题下载 |
| ECR 镜像 ask-human 层 `server.py` | 判定 prompt（AST 解析 f-string 重建，不执行）；每个 blocker 最多回答 2 次、少于 3 字符直接判 irrelevant |
| ECR 主镜像 `sql_server.py`、`business_info_server.py` | execute_sql 只读、200 行截断；business info 用 all-MiniLM-L6-v2、top 5、按库过滤 |
| Harbor `test_verify.py` | 通过判定直接导入官方 `compare_pandas_outputs` |

**与官方设置的差异**（报告时必须标注）

- 模拟用户：Claude Haiku（`claude-haiku-5-5`），论文为 Llama-3.3-70B、temperature 0.05。CLI 不能设温度；managed CLAUDE.md 无法关闭，判定上下文里会带上约 2k token 的 HPC 策略文本。
- 判定 JSON：官方 null 示例带尾逗号，官方解析器会返回 CANT_ANSWER；我们容错解析并记录 `parse_mode`。
- Precision 两种都记：harness 定义（解决的不同 blocker 数／问题数）与论文定义（被判相关的问题数／问题数）。汇总用 micro。
- 格式错误与 requery 同 SWE-agent `FunctionCallingParser` 与 `forward_with_handling`。区别：我们按 token 追加历史，失败回合之前的 reasoning 都保留；官方模板重渲染会丢掉。
- business info 检索用 transformers 复现 MiniLM（revision `1110a243`），精确余弦 top 5。
- execute_sql 超时 120 秒（官方 1200 秒）；每步最多生成 8192 token，上下文上限 65,536。
- 系统 prompt：ask 条件用官方 Qwen ask 配置原文；blocked 与 full-info 只差 instance 文本。full-info 文本用论文 pipeline 的 jinja 模板。
- 采样：Qwen3.5 卡片 thinking 模式设置，T=0.6、top_p=0.95、top_k=20。

## 采集内容

**决策点** = 模型每一次产生动作（任意工具调用或提交）之前的状态。每次尝试生成后，对"前缀 + 本次输出"做一次 teacher-forced 前向，取 32 个 block 输出在六个位置的激活，存为 `activations.safetensors`（`acts [决策点数, 6, 32, 4096] bfloat16`）。

| 键 | 位置 |
|---|---|
| `pre` | 生成前最后一个输入 token |
| `think_end` | `</think>` token |
| `act_first` | 动作（tool call）的第一个 token |
| `obs_mean` | 最近一次工具返回的 token 均值 |
| `think_mean` | 本步 reasoning token 均值 |
| `input_mean` | 全部输入 token 均值（每条轨迹第一步，以及每次 ask 得到回答后的下一步） |

- **工具选择打分**：Qwen 分词会把 `=` 与工具名粘在一起，不能用"工具名首 token 概率"。改为在 `<function` 的最后一个 token 处截断，用 KV cache 逐 token 计算每个工具完整续写 `=<name>` 的 log 概率（`tool_logprobs`）。
- **配对前向**：blocked 条件额外做一次前向，前缀与输出相同，只把 instance 文本换成 full-info 版（`paired_acts`，off-policy）。
- **每步元数据**：动作、问题文本、判定结果、已解决 blocker、完整前缀 token，供之后做单步 steering 重放。
- **可追溯性**：`init` 把 `src/info_seeking`、复用的 `persona_repro` 模块、入口脚本与 slurm 冻结到 `runs/<id>/source/`，已有 run 的所有 stage 都从冻结代码导入。非 smoke run 要求代码树干净。

代码：`src/info_seeking/`，入口 `scripts/hil_sql_pilot.py`，作业 `scripts/hil_sql_pilot.slurm`（经 `scripts/submit.sh`），配置 `configs/info-seeking-hil-sql.json`，合成测试 `tests/test_info_seeking.py`（经 `scripts/info_seeking_tests.slurm`）。离线分析 stage（`annotate`、`rejudge`、`kb-map`、`blocker-outcomes`）用仓库当前代码，输出里记录 commit。

两轮独立 subagent 代码审查（2026-11-16）确认：无 resolution 泄漏、工具语义与官方一致、位置索引正确、requery 次数同 SWE-agent。据此修了这些问题：
- 工具名打分位置；Ask 汇总改 micro；判定解析失败不重问；格式错误码与 requery 语义；
- 子进程显式 PYTHONPATH；Slurm 执行 run 冻结的入口脚本；`.tmp` 目录排除；
- 未闭合 think 内的 tool call 不计；bf16 存储；工具输出里的特殊 token 字符串按普通文本分词。

## Run 记录

| run ID | 内容 | 实现 commit | 状态 |
|---|---|---|---|
| smoke-is-hil-sql-qwen35-9b-20261116-133313 | 审查前的旧代码 preflight | 5ec8675 + 未提交改动（smoke） | 已被下一行取代 |
| smoke-is-hil-sql-qwen35-9b-20261116-135913 | preflight、2 题 × 4 条件、20 题判定校准（PyTorch 回退路径） | 5ec8675 + 未提交改动（smoke） | 完成 |
| subset-is-hil-sql-qwen35-9b-20261116-210747 | 20 题 × 3 条件，宽松判定，100 步，venv-is 快速 kernel | 9570088 | 完成（preflight 66256643；shard 66256644–66256647，各 3–4 小时） |

## 结果：20 题子集（2026-11-17，每条件 20 个 unit，1 seed）

| 条件 | pass@1 | 提交率 | 有提问的 unit | 问题数 | blocker recall | precision（harness／论文） | 平均步数 | 平均用时 |
|---|---|---|---|---|---|---|---|---|
| blocked_ask | 0.20 | 0.90 | 0.40 | 35 | 27/80 = 0.34 | 0.77／0.83 | 60.0 | 1039 s |
| blocked_ask_prompted | 0.40 | 0.90 | 0.90 | 72 | 56/80 = 0.70 | 0.78／0.88 | 52.6 | 909 s |
| fullinfo_ask | 0.70 | 1.00 | 0.00 | 0 | — | — | 30.4 | 491 s |

- 指标为 micro 汇总，宽松判定；判定失败 0 次，同一 blocker 第 3 次命中被截 1 次（blocked_ask）与 3 次（prompted）。
- 自然条件下有 8 题提问（4、15、16、18、47、59、67、83），precision 约 0.8。smoke 的 2 题（48、63）仍未提问；与 smoke 的差别可能来自步数上限（40→100）、快速 kernel 的数值差异或样本题，尚未区分。
- 提问指令使有提问的 unit 从 40% 升到 90%，recall 从 0.34 升到 0.70，precision 基本不变，pass@1 从 0.20 升到 0.40。
- full-info 下 0 次提问。但这个条件的题面本身带着澄清，测不出"没有 blocker 时会不会乱问"；要测这一点需要真正无 blocker 的任务。

### 官方判定离线重判（`rejudge`，`analysis/rejudge/`）

同一批问题改用官方 prompt + Haiku 重判：

| 条件 | 问题数 | 宽松接受 | 官方接受 | 解决的 blocker（宽松 → 官方，含每个 blocker 最多 2 次） |
|---|---|---|---|---|
| blocked_ask | 35 | 29 | 3 | 27/80 → 3/80 |
| blocked_ask_prompted | 72 | 63 | 9 | 56/80 → 9/80 |

官方接受的问题，宽松判定全部接受且判到同一 blocker。这只衡量判定标准本身：闭环若用官方判定，被拒的问题拿不到答案，后续轨迹也会不同。

### 离线标注：分级意识与逐 blocker 漏斗

Haiku 逐步标注（60 个 unit，约 2900 步，0 次失败），cache key `hil-annotate-v4`：
- **意识等级 0–3**：只提到术语是 1 级，明确说缺失／歧义是 2 级，再说明无法确定或结果取决于它是 3 级。≥2 级才算"意识到"。
- **拍板依据**：问到的回答、检索到的 KB、查数据、给定的澄清、按题面字面、自己的默认；后两类算"猜"。
- **逐 blocker 实现**：提交的 SQL 是否按 resolution 实现。
- **KB 映射**（`kb-map`，结果存为各题的 `kb_resolution.json`，可复用）：哪些 business-info 条目完整或部分给出了 resolution。

结果在该 run 的 `analysis/blocker_outcomes.jsonl`、`blocker_outcomes_summary.json`，以及 `analysis/annotations/`。

| 条件 | 意识到的blocker/总blocker（≥2 级） | 其中 3 级 | 拍板前已意识到 | 问到 | 查 KB | 自己猜 | 未意识到 |
|---|---|---|---|---|---|---|---|
| blocked_ask | 76/80 | 73 | 69 | 27 | 6 | 41 | 4 |
| blocked_ask_prompted | 77/80 | 69 | 70 | 56 | 5 | 13 | 3 |
| fullinfo_ask | 30/80 | 12 | 5 | 0 | 1 | 6 | 50（其余 23 为照给定信息） |

逐 blocker 的实现准确率（是／已判定），按信息来源分：

| 条件 | 问到并得到回答 | 查 KB | 自己猜 | 给定澄清（full-info） |
|---|---|---|---|---|
| blocked_ask | 17/23（74%） | 0/6 | 2/34（6%） | — |
| blocked_ask_prompted | 34/49（69%） | 0/5 | 1/12（8%） | — |
| fullinfo_ask | — | 1/1 | 5/6 | 照给定信息 19/23；未提及但实现 37/50 |

- **blocked 条件下的意识率饱和**：分级后仍是 76/80，73 个到 3 级。分级只拉开了条件间差别（full-info 有 50/80 停在 1 级）。所以在 blocked 条件内，"意识到 vs 没意识到"几乎没有负例，不能作 probe 标签。可用的同条件对比是**意识到之后问 vs 猜**（blocked_ask 中 27 对 41）。HiL 的 blocker 多是题面里显眼的模糊词，9B 通常会在推理里逐一列出。
- **提问指令把"猜"变成"问"**（猜 41→13，问 27→56），不改变意识率（76→77）。
- **KB 从不含完整答案**：80 个 blocker 中 17 个 partial（方向对但缺关键值，例如说了 short 指身高却没给 173cm，给了公式却没给常数 2.4），63 个 none，0 个 full。查到 partial 条目后就停下的 6 个（prompted 中 5 个）全部实现错误：**找到部分线索就当作已解决，不再问**。所以 HiL SQL 不能评"自行检索成功"，只能评"检索后是否还会问"。summary 里的 `kb_contains_resolution` 含 partial；`kb_contains_full_resolution` 为 0。
- **不提问就做不对**：blocked_ask 中做对的 4 题（16、18、47、83）全部来自会提问的 8 题。
- **数值碰撞**：该库插入了人造病人（ID 999995–999999）专门区分不同解读，但计数很小，不同解读容易得到相同数字。官方验证只比较输出，所以 blocked 条件下的 solve 不能当作"blocker 被正确处理"的证据，需要上面的逐 blocker 实现判定。

旧的二值标注方案（v3）结果，作为对照：意识到过的 blocker 79/80、80/80、64/80；意识到缺失的步占 65%、59%、41%；拍板依据为自己猜的占 84%、75%、28%。v3 把只提到术语也算作意识到，并把"按题面字面"算作"给定澄清"，v4 已修正这两点。

### 结构标签的 probe（作业 66284313，`analysis/probe/`）

按题分 5 折，报 logistic、均值差投影、打乱标签三种 AUC。

- **条件对比**（paired_fullinfo、cond_ask）在第 4 层就达到 AUC 1.0：只是读出题面多了一段文本，不能当作"缺信息"的表征。
- **ask_action**：blocked_ask（35 个提问步／8 题）在 `pre` 位置第 9 层 logistic 0.94、均值差 0.79；推理之后的位置达到 1.0（推理里已写出要问）。正例太少，打乱标签的 AUC 在 0.24–0.62 之间波动，估计很不稳。prompted（72 个）：`pre` 第 10 层 logistic 0.96、均值差 0.85。
- **nothing_resolved**：步数本身就能预测（AUC 0.75），probe 约 0.95，没有明显超出时间先后的信息。
- 结论：结构标签要么读到题面文本，要么混着时间顺序，只能作流程检查。

## smoke 观察（2 题 × 4 条件，40 步，PyTorch 回退路径）

- preflight：我们追加的 token 与官方模板渲染逐 token 一致；`pre` 位置的激活与后续 token 无关（差 0.0）；cache 续写打分与全序列 teacher forcing 一致（−0.0162 vs −0.0145）；激活无溢出（|max| 125）。
- 判定校准（20 题全部 260 个 registry 示例问题，作业 66225366）：官方 prompt + Haiku 判对 32.3%、拒绝 67.7%；宽松 rubric 判对 100%；两者都没有判错 blocker。论文报告其判定的人工 recall 为 91%，本地官方判定明显更严。
- 推理里从未考虑提问：8 条轨迹没有一次提到 ask_human 或请求澄清，包括有 ask 工具的 4 条。模型识别到歧义（如 public_sql_63 反复写"这看起来矛盾""17–19 只是启发式"），然后自选解读；三处都与 registry 的 resolution 不同。
- full-info 也会失败：public_sql_48 的 full-info 两条都没做对，这道题的 SQL 对 9B 偏难。
- 环境：`venv-fast`（Python 3.10）里 fla 0.5.2 导入失败（`inspect.getsourcelines` 遇到装饰器里的 lambda 会截断），transformers 静默退回 PyTorch 实现，结果正确但慢（约 12.6 token/s）。子集起改用 venv-is。

## 后续

- 第二轮 probe：用标注标签做同条件内对比（意识到之后问 vs 猜），重点看 `pre` 位置，做基线扣除（逐题中心化、步数匹配）。
- 单步 teacher-forced 扫描：层 × 位置 × 系数 → ask_human 概率的变化，blocked 与 full-info 决策点分开报告。
- 闭环确认：无干预、prompt 指令基线、无条件 v_ask、probe 门控 v_ask、随机方向。

## 限制

- 模拟用户不是论文的 Llama-3.3-70B，分数与论文不可直接比较。
- 公开 SQL 集只有 100 题，子集 20 题、1 seed，结论需在其他 benchmark 上复核。
- HiL-Bench 没有原生的无 blocker 任务；full-info 是"已解决"对照，表征证据还需要轨迹内对比。
- 论文中没有 ≤10B 模型的结果。
