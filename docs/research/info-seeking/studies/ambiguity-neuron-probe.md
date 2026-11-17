# is-ambiguity-probe：在 Qwen3.5-9B 上复现 Sparse Neurons 的歧义 probe

状态：**代码已写，未提交作业**（2026-11-16）；等 venv-is 环境构建完成后跑 smoke。假设与路线见 [overview](../overview.md)。

## 问题

复现 Sparse Neurons Carry Strong Signals of Question Ambiguity in LLMs（EMNLP 2025，arXiv 2509.13664）的 probe 部分，得到一个与已有工作可比的"问题信息不足"读出（probe、AEN 与方向），保存成可直接打分的包，之后拿到 BIRD evidence 配对、HiL 等其他设定上测试。

**不复现他们的 steering**（用户决定，2026-11-16）：论文的 steering 向量是"歧义且弃答" vs "清楚题"，把信息不足和弃答行为混在一起；仓库代码里又是另一种做法（歧义题中弃答 vs 直接回答、最后一个 token），与论文不一致；评价也没有测清楚问题上的过度弃答。steering 之后按我们自己的设定（缺失固定、只比较行为）来做。

## 原文设置（依据 arXiv HTML 全文）

- 模型：LLaMA 3.1 8B Instruct、Mistral 7B Instruct v0.3、Gemma 7B IT，生成温度 0.1。
- 数据：AmbigQA（原始歧义问题 vs 标注者的一个消歧改写）、SituatedQA（去掉时间或地点的问题 vs 补上的 `edited_question`）。每个数据集每类 400 训练、1000 测试。
- 表征：prefill 阶段所有 token 在第 l 层的隐状态取均值；默认 l = 14。
- probe：logistic regression；按 |w| 排名维度，对 top-k 维注入高斯噪声看准确率下降，下降陡峭的前几维称为 AEN（LLaMA 3 个，Mistral、Gemma 各 1 个）；只用 AEN 重训 probe。
- 其他：逐层 probe（全维与 AEN），跨数据集迁移，TriviaQA 上的误报；steering（第二阶段）用"歧义且弃答"100 条 vs "清楚"100 条做均值中心化后的 PCA 第一主成分，只在 AEN 维上施加。
- 原文未给出：probe 的 prompt 格式、噪声方差、AEN 的判定阈值、steering 系数与后缀文本，没有公开代码。

## 原作者代码（2026-11-16 核对）

仓库 `github.com/Zhuoxuan-Zhang/Internal_State_Detect_Ambiguity`（第一作者账号，commit `63a29bad`，2025-05，**无许可证**，README 为空；检出在 `${PV_WORK}/external/Internal_State_Detect_Ambiguity`，只读不复制）。数据文件导出到 `${PV_WORK}/external/sparse-neurons-data/original/`。与论文对照：

| 项 | 代码中的实际做法 | 与论文描述 |
|---|---|---|
| 数据 | AmbigQA light train 中带 multipleQAs 的问题，清楚版 = `qaPairs[0].question[0]`（4747 对）；SituatedQA 合并文件 8456 对，每个 id 取第一条 `edited_question` | 一致，论文未写细节 |
| prompt | 手写模板，system = "You are a helpful assistant."，用户消息 = 问题（模板字符串里带缩进空格） | 论文未写 |
| 表征 | `hidden_states[14]`（即第 14 个 block 输出），对所有位置取均值；**批量右侧补齐后连 padding 一起平均** | 论文说"对 token 均值"，没提 padding |
| 划分 | 训练和测试来自**同一文件**，两类各自用 numpy 种子 11–14 打乱，训练取前 400、测试取后 1000。按此复算：AmbigQA 有 306 个问题 id 同时出现在训练和测试（同题或其配对版），SituatedQA 有 164 个 | 论文写"randomly shuffled and split" |
| probe | sklearn `LogisticRegression(max_iter=1000)`，原始特征，不标准化 | 一致 |
| AEN | 按 |coef| 排名，前 k 维替换成同列均值、方差的高斯噪声（不是叠加），k = 0…10；AEN 下标是看曲线后手写的（LLaMA 788、4062、1384；Gemma 1995；Mistral 2070） | 论文未写判定规则 |
| steering 向量 | `steering_vector.py`：歧义题中"弃答"均值减"直接回答"均值，**最后一个 token**、第 14 层 | 论文写的是"弃答 vs 清楚题"、均值池化、PCA |
| 其他 | 仓库中硬编码了 OpenAI 与 DeepInfra 的 API key；我们不使用 | |

## 我们的设置

两个协议共用同一批激活（每条唯一文本、每种前缀只前向一次）：

- **忠实版（faithful）**：原作者的数据文件与划分（含上面的泄漏），sklearn probe，第 14 层，噪声替换法。用来与原文趋势对照。
- **修正版（grouped）**：从原始数据集重建配对（规则同原代码），SituatedQA 训练取 train 文件、测试取 dev + test 文件，AmbigQA 训练取 train、测试取 validation；同一问题的两版只在一侧。每类 400 训练、1000 测试。加词面对照（见下）。

| 项 | 设置 | 与原文的差异 |
|---|---|---|
| 模型 | Qwen3.5-9B（revision `c2022362`），32 层，与 HiL 同一 runtime | 原文三个模型需 HF 授权；我们要的是自己模型上的 probe |
| prompt | Qwen3.5 chat template，system = "You are a helpful assistant."（同原代码），用户消息 = 问题。两种生成前缀：`nothink`（`enable_thinking=False`，接近原文的非推理模型）与 `think`（以 `<think>\n` 结尾，与 HiL 一致） | 原文用手写模板 |
| 位置 | `input_mean`（全部 prompt token 均值，原文做法，但**不含 padding**：逐条前向）、`user_mean`（只取问题 token）、`pre`（最后一个 token），全部 32 层 | 后两个是我们加的 |
| AEN 判定 | 噪声曲线上准确率下降达到最大降幅一半时的最小 k | 原文人工挑选 |

**我们加的对照**：

1. **词面对照**：从 SituatedQA 标为"不依赖上下文"的问题（`id_data` dev／test，`is_dependent = no`，共 3901 条）中抽 400 条，在后面接上从训练集抽到的同类短语（" in india"、" as of 2020"），两边都"清楚"。probe 若把未加短语的一边判为歧义，说明它读的是插入的词，而不是信息是否充分。
2. **长度基线**：只用问题 token 数分类的 AUC。
3. **逐层曲线**：原文报告第 5 层前就饱和，提示可能是表面特征；同时给出词面对照在各层的表现。
4. **忠实 vs 修正**：两种划分下的准确率差，反映原划分的泄漏影响。

## 保存的读出（供迁移测试）

`analysis/directions.safetensors`，键名为 `<mode>/<protocol>/<dataset>/<key>/L<layer>/{dom,coef,intercept}`：均值差方向（歧义减清楚）与完整 probe 的权重和截距，覆盖两种前缀 × 两个协议 × 两个数据集 × 三个位置 × 32 层。AEN 包另存在 `aen/<mode>/<protocol>/<dataset>/input_mean/L14/{dims,coef,intercept,train_mean,train_std,top50_dims}`。用 `info_seeking.ambiguity.score_with_bundle(bundle, 前缀, 激活)` 打分（> 0 = 判为歧义）。

**只适用于同一取法的激活**：同一模型与 revision、同一层与位置、同一 prompt 格式（chat template + system "You are a helpful assistant."，逐条前向不含 padding）。AEN 下标是模型特有的：原文的 LLaMA 3.1 8B（788、4062、1384）、Mistral 7B（2070）、Gemma 7B（1995）只作记录，不能用在 Qwen3.5-9B 上。

## 代码与产物

- `src/info_seeking/ambiguity.py`（两个协议的数据构建、词面对照、sklearn probe、噪声与 AEN），入口 `scripts/ambiguity_probe.py`（init／forward／probe），作业 `scripts/ambiguity_probe.slurm`，配置 `configs/info-seeking-ambiguity.json`。
- 数据：`${PV_WORK}/external/sparse-neurons-data/`（SituatedQA GitHub commit 见 `situatedqa/COMMIT`；AmbigQA HF `sewon/ambig_qa` revision `e969d013`，light 配置，CC BY-SA 3.0）。
- 规模：去重后 11,177 条短 prompt × 2 种前缀 ≈ 2.2 万次前向，预计不到 1 GPU 小时（待 smoke 校正）；probe 阶段约 800 次 sklearn 拟合，CPU 即可。

## Run 记录

| run ID | 内容 | 实现 commit | 状态 |
|---|---|---|---|
| （尚无） | | | |

## 限制

- 不是对原文模型的复现，数值不能与原文直接比较；能比较的是趋势（是否线性可分、是否稀疏、是否浅层饱和、是否跨数据集迁移）。
- AmbigQA 的消歧版是改写，不完全是插入；SituatedQA 是插入。
