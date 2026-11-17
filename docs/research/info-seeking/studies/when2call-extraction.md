# is-when2call-extraction：When2Call 上的 v_miss／v_ask 读出与方向提取

状态：**暂停（见"暂停与审查待修项"），未提交作业**。假设与路线见 [overview](../overview.md)；HiL 侧的验证在 [is-hil-sql-pilot](hil-sql-pilot.md)。

## 问题

在单轮、成对的数据上提取"缺信息"（v_miss）和"提问"（v_ask）方向，作为之后在 HiL-Bench SQL 上检验读与写的外部方向（H5）。HiL 定位为验证集，提取优先在这里做。

## 数据

- When2Call（NVIDIA，CC BY 4.0），HF `nvidia/When2Call` revision `0582f774`；MCQ 测试集 3652 条（sha `8c3694e5…`），评测代码 GitHub commit `ecc8d423`（Apache 2.0）。文件留在 `${PV_WORK}/external/when2call*`，钉哈希。
- 每个 BFCL `source_id` 有三个变体：
  - `tool_call`：完整问题与工具；
  - `request_for_info`：删去一个必需参数（`held_out_param`）后的**改写**问题，工具相同（1062 组中 1046 组问题被改写，不只是删参数）；
  - `cannot_answer`：与 tool_call 相同的问题，目标工具被移除。
  1062 组三元组 + 233 组只有 tool_call／cannot_answer。
- 划分：按 tool_call 变体工具集的哈希分组（1295 个 source_id 对应 433 个工具集，最大一组 29 条），seed 0，train／dev／test = 0.6／0.2／0.2。共用工具集的近似重复问题不会跨集合。所有方向与 AUC 只用 train；dev／test 不动。

## 设计

| 读出 | 设置 | 用途 |
|---|---|---|
| prompt 激活（全部 3652 条） | thinking 开启的 prompt（以 `<think>\n` 结尾，与 HiL agent 同一 runtime 与位置定义），无额外 system prompt；`pre`、`input_mean`、`user_mean`（只取用户问题 token） | v_miss：rfi vs tool_call（缺参数 + 改写）；特异性对照：cannot vs tool_call（同一问题、缺工具） |
| MCQ log 似然（全部 3652 条） | 官方方式：四个候选答案在 prompt 后的 log 似然；`acc` 取总和最大，`acc_norm` 按 UTF-8 字节归一化，另报 macro-F1 与工具幻觉率。**非 thinking 模板**，工具调用候选为 Qwen3.5 原生 XML 格式 | 行为基线，与论文的可比性有限（候选比官方 JSON 长，acc_norm 不可直接比）。与 thinking 激活分开，不混用 |
| 试点自由生成 | train 中随机 50 组三元组 × 3 变体 × 2 条件 = 300 条，thinking 开启，最多 4096 token，采样同 HiL | 自然提问率、参数幻觉率；v_ask：rfi 题上"提问 vs 仍调用工具"的行为对比 |

**两个生成条件**：`native`（官方工具列表；提问 = 纯文本）与 `ask_tool`（非官方，额外加一个 `ask_user` 工具，使"提问"和 HiL 的 ask_human 一样是一次工具调用）。`native` 条件下 `act_first` 及之后的位置部分编码"文本回复 vs 工具调用"，所以迁移到 HiL 时以 `pre` 与 `think_end` 为主。

**生成阶段的记录**：激活位置 `pre`、`think_end`、`act_first`、`think_mean`、`input_mean`、`user_mean`；`</think>` 后第一个非空白 token 前的位置上 log P(`<tool_call>`)（调用 vs 文本的决策）；工具调用时各工具名续写的 log 概率（同 HiL 的打分方式）。

**行为标签**：工具调用直接解析（`ask_user` → request_for_info；其他工具 → tool_call，并确定性检查 `held_out_param` 是否出现在参数里，即参数幻觉）；只有纯文本回复交给判定，用官方 When2Call `JUDGE_PROMPT`（AST 读取，工具格式同官方脚本的 `str(list)`），由 Claude Haiku 回答（论文用 OpenAI 模型）。官方脚本在 JSON 解析失败时会重问一次；我们不重问，改用正则提取 classification，失败单独计数。未闭合 think 或生成被截断时标为 `no_response`。

## 代码与产物

- `src/info_seeking/when2call.py`（数据、分组划分、MCQ 渲染与指标、标签与判定），入口 `scripts/when2call_extract.py`（init／preflight／forward／generate／summarize／probe），作业 `scripts/when2call_extract.slurm`，配置 `configs/info-seeking-when2call.json`。
- 与 HiL 共用：`agent.QwenAgentRuntime`（同一模型加载、快速 kernel 检查、位置与续写打分）、`runs.create_run_dir`（冻结代码与 manifest）、`probe_analysis.readout`（按组交叉验证的均值差／logistic／打乱标签 AUC 与方向）、`simulator.call_claude`。
- run 目录：`forward/chunk_*.{jsonl,safetensors,done}`、`generate/chunk_*`、`analysis/probe/{forward,generate}/`。按 chunk 断点续跑。

## 计划顺序

1. venv-is 就绪后：smoke（`--purpose smoke --pilot-limit 2 --forward-limit 40`）+ preflight。
2. forward 全量（预计不到 1 GPU 小时，待 smoke 校正）与 50 组试点生成。
3. 看自然提问率与参数幻觉率，再决定是否扩大生成规模，以及 v_ask 用 `native` 还是 `ask_tool` 条件。

## 暂停（2026-11-16）与审查待修项

用户决定回退一步：When2Call 缺的是一眼可见的工具参数，且 rfi 版问题被整句改写，作为 v_miss 的提取来源偏浅、混杂。先比较其他 benchmark（候选：BIRD 训练集的 evidence 有／无配对、BIRD-INTERACT LITE、QuestBench GSM-Q／GSME-Q、CLARITI），本 study 暂不提交作业。若恢复，先修下列审查发现（独立 subagent，读代码确认）：

1. 行为标签把真实工具调用记成 `format_error`：rfi 题上缺 `held_out_param` 的调用触发 `missing_arg`，cannot 题上调用被移除的工具触发 `invalid_command`，正好是要测的参数幻觉和工具幻觉。应改为宽松解析：任何格式正确的 `<function=X>` 都算 tool_call，另记 `tool_in_list`、`missing_required`、`held_out_supplied`。
2. macro-F1 应对金标与预测标签的并集求平均（与 lm-eval／sklearn 一致），否则预测出 `direct` 时会偏高。
3. 官方工具幻觉率只算工具列表为空的 cannot_answer 题（258 条）；现在的合并口径需改名另报。
4. `cannot_vs_toolcall` 中 258 条无工具的 prompt 缺整个工具 system 块，是平凡的结构线索；应排除或单独成组。
5. 按工具集分组仍有 26 个相同问题（大小写归一后）跨 split；应对问题文本与目标工具名做并查集分组。
6. 判定失败行被写入且 chunk 标 `.done` 后不会重判；需补重判或不标完成。
7. 生成被截断在工具调用中途时应记 `no_response`，现在记成 `format_error`。
8. 需运行时核对：MCQ 工具候选中布尔参数被模板渲染为 `True`（模型生成可能写 `true`）；lm-eval `acc_norm` 的长度单位（字符还是字节）。

## Run 记录

| run ID | 内容 | 实现 commit | 状态 |
|---|---|---|---|
| （尚无） | | | |

## 限制

- rfi 与 tool_call 的问题文本不同（改写），rfi vs tool_call 方向混有改写风格；需要和 cannot vs tool_call、HiL 上的读出一起解释。
- 缺失的是 prompt 中可见的工具参数，不是执行中才出现的 blocker。
- MCQ 用非 thinking 模板，与 thinking 下的行为可能不同。
