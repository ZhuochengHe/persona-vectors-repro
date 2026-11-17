# is-ambiguity-probe：在 Qwen3.5-9B 上复现 Sparse Neurons 的歧义 probe

状态：**完成**。Qwen 复现、LLaMA 原模型核对、BOS 消融与 Qwen 大激活检查都在 run `full-is-ambiguity-probe-qwen35-9b-20261116-210747` 下，作业见文末 Run 记录。假设与路线见 [overview](../overview.md)。

**一句话结论**：原文的"稀疏歧义神经元"是 BOS 大激活经含 padding 的均值池化后形成的长度伪影；去掉 BOS 后仍有可分信号，但它没有通过词面对照，不能当作歧义表征。这个 probe 只作为与已有工作可比的基线保留。

## 问题

复现 Sparse Neurons Carry Strong Signals of Question Ambiguity in LLMs（EMNLP 2025，arXiv 2509.13664）的 probe 部分，得到一个与已有工作可比的"问题信息不足"读出（probe、AEN 与方向），存成可直接打分的包，供其他设定测试。

**不复现 steering**（用户决定，2026-11-16）：论文的 steering 向量把信息不足与弃答行为混在一起，仓库代码的做法又与论文不同，评价也没有测清楚问题上的过度弃答。

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
| AEN | 按 |coef| 排名，前 k 维替换成同列均值、方差的高斯噪声（不是叠加），k = 0…9；AEN 下标是看曲线后手写的（LLaMA 788、4062、1384；Gemma 1995；Mistral 2070） | 论文未写判定规则 |
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
- 规模：去重后 11,177 条短 prompt × 2 种前缀，约 2.2 万次前向。
- 原模型核对与消融：`scripts/ambiguity_faithful.py`（照原代码）、`scripts/ambiguity_bos_ablation.py`（换池化方式）、`scripts/qwen_massive_check.py`（Qwen 首 token 与大激活），各有同名 `.slurm`，通过 `scripts/submit.sh` 提交。

## 结果（2026-11-17）

### Qwen3.5-9B（`analysis/summary.json`、`probe_metrics.csv`；测试集每类 1000 条）

1. **线性可分性可以复现**：第 14 层 probe 在 SituatedQA 上 acc 0.93–0.94（AUC 0.98–0.99），AmbigQA 上 0.85–0.88（AUC 0.92–0.94）。三种位置、两种前缀差别很小；最佳层分散在 6–25 层。
2. **原划分的泄漏影响可忽略**：忠实版与修正版相差不超过约 0.01。
3. **信号主要是表面特征**：只用问题 token 数分类的 AUC 已有 0.83–0.88。词面对照上，SituatedQA 训练的 probe 在第 14 层把未加短语的一版判为歧义 77–82%，加了短语的一版只有 1–4%，AUC 0.95–0.97；AmbigQA 训练的 probe 也有 0.90–0.93，各层都如此。
4. **没有稀疏神经元**：替换前 10 维为噪声，准确率只从 0.94 降到 0.92–0.93（AmbigQA 0.88→0.85）。按原文规则（两数据集各自 top-5 的共有维），忠实划分下只有第 2560 维，修正划分下没有；把 2560 维换成噪声，准确率只降 0.003–0.006。按我们的自动规则选出的 2–6 维重训后只有 0.70–0.80。
5. **跨数据集迁移不对称**：AmbigQA → SituatedQA 为 acc 0.75–0.84（AUC 0.84–0.91），反向只有 0.55–0.69（AUC 0.66–0.79）。
6. **Qwen 的大激活不在 probe 里**（`analysis/qwen_massive/qwen_massive_check.json`）：Qwen3.5 不加 BOS，第一个 token 是 `<|im_start|>`。第 14 层的大激活维是 3456（首 token 71.5，其他位置最高 21.5）与 3994（33.5），所有维度最大绝对值的中位数为 1.0。常排第一的 2560 维最大只有 5.1，在 4096 维中排第 42，不是大激活维。去掉 3456、3994 后 probe 的 acc／AUC 基本不变（相差 ≤ 0.002）。probe 分数与 prompt 长度的相关为 −0.73 至 −0.77，即 Qwen 上长度也被读到了，只是分布在许多维度上，而不是集中在几个大激活维。

AEN 判定规则（2026-11-17 用户更正）：原文 Table 2 的 AEN 是"两个数据集各自按 |w| 取前 5 维，两边共有（加粗）"的维度，再参照噪声曲线定个数（LLaMA 3 个，Mistral、Gemma 各 1 个；LLaMA 的 4055 两边都在前 5 却未加粗，原文没解释）。我们的自动规则是"单数据集上准确率下降达到最大降幅一半时的最小 k"，在 LLaMA 上能选出原文的神经元。

### LLaMA 3.1 8B Instruct 原模型核对（作业 66284263，`analysis/faithful/faithful_llama.json`）

逐项照原代码：
- 导出的四个数据文件与原仓库逐字节相同。
- numpy legacy 打乱在 1.23.5 与 2.2.6 下排列相同，训练／测试泄漏也一并复现（AmbigQA 83／103，SituatedQA 47／45 条共用 prompt）。
- 手写模板逐字节相同，含缩进与重复的 BOS。
- 每批 20 条右侧补齐、pad = eos、均值含 padding、fp16、`hidden_states[14]`、sklearn 1.5.2。
- 噪声随机数接续 seed 14 打乱后的全局状态（原代码不重设种子），k = 0…9，另延长到 50 供自动规则用。

以上经独立 subagent 审查（2026-11-17）。审查还指出：原文 Mistral SituatedQA 的 94.14% 在 2000 条测试集上不可能出现（准确率只能是 0.05% 的倍数），说明该格的运行与代码划分不同或有笔误。Gemma 无下载权限；Mistral 按用户要求不做。

| | AmbigQA 复现／原文 | SituatedQA 复现／原文 |
|---|---|---|
| 完整 probe 准确率 | 90.55／90.65 | 95.30／95.40 |
| Top-5 神经元 | 788, 1384, 4062, 4055, 1298（与原文一致） | 788, 1384, 4062, 4055, 3231（与原文一致） |
| 原文写死的 3 个神经元的 probe | 88.55／88.6 | 94.05／94.0 |
| 自动规则选出的 AEN | 788、1384（k = 2），probe 88.0 | 788、1384、4062（k = 3），probe 94.05 |

- **复现是忠实的**：数字相差 0.1 以内，神经元完全一致。所以"Qwen 上没有 AEN"不是选法的问题。
- **这些 AEN 是长度检测器**：
  - 788、1384、4062 是 LLaMA 的大激活维度，在两个 BOS 位置上约为 +323、−294、−296，其他位置约为 0。特征均值的绝对值约 10，而所有维度的中位数约 0.026。
  - 原代码对含 padding 的整段求均值，这三维的特征就等于"BOS 尖峰 ÷ 补齐后长度"，与 1／补齐长度的相关为 +1.000、−0.999、−1.000。
  - 补齐只让同一批的长度相同。原代码每批只放同一类题，批内最长长度就编码了类别：只用补齐长度分类的 AUC 为 0.97–0.99，真实 token 数为 0.83。完整 probe 分数与补齐长度的相关为 0.97–0.99。
- **词面对照**：两版都清楚、只差末尾短语时，probe 把未加短语的一版判为歧义 78–100%，AUC 0.98–0.99（每批 20 条）；每批 1 条（无 padding）时 AUC 仍为 0.88–0.89。

"忠实"有两种含义，因为代码与论文描述不一致（划分是否不相交、噪声是叠加还是替换、AEN 是规则选还是写死、均值是否含 padding 与模板 token）。`ambiguity_faithful.py` 跟代码走，用于核对报告的数字；`src/info_seeking/ambiguity.py` 的 grouped 协议跟论文意图走。

### BOS／padding 消融（LLaMA 3.1 8B，作业 66305651，`analysis/bos_ablation/bos_ablation_llama.json`）

prompt、划分与分批同原代码，只换池化方式：orig＝原文，含 BOS 与 padding；real_nobos＝只取真实 token 且去掉 BOS；user＝只取用户问题的 token；last＝最后一个真实 token。每格为 AmbigQA／SituatedQA。

| 池化 | A 原 probe 直接套用 | B 重训 acc（AUC） | 分数与真实长度相关 | D 等长分层 AUC | 词面对照 AUC（未加短语判为歧义） | C 原文 3 个神经元的排名 | C 噪声曲线 k=0→10 |
|---|---|---|---|---|---|---|---|
| orig | 90.5／95.3 | 90.5（0.986）／95.3（0.994） | 0.55／0.62 | 0.98／0.98\* | 0.99（100%）／0.99（78%） | 1、2、3 | 90.5→50.4／95.3→53.0 |
| real_nobos | **50.0／50.0** | 84.9（0.91）／88.3（0.95） | 0.89／0.84 | 0.82／0.88 | 0.87（93%）／0.96（89%） | 1417 名以后 | 84.9→84.0／88.3→87.0 |
| user | 50.0／50.0 | 86.6（0.93）／92.6（0.98） | 0.73／0.70 | 0.86／0.96 | 0.91（93%）／0.98（93%） | 1375 名以后 | 基本不变 |
| last | 50.0／50.0 | 85.5（0.93）／93.4（0.98） | 0.72／0.73 | 0.85／0.97 | 0.91（91%）／0.99（92%） | 176 名以后 | 基本不变 |

只用真实长度分类的 AUC 为 0.83／0.83。\*orig 的等长分层不能排除长度：分层用真实长度，而 orig 的特征依赖批内补齐长度。

- **原 probe 完全依赖 BOS 特征（A）**：换成任何去掉 BOS 的池化，准确率都是 50%。
- **去掉 BOS 后没有稀疏神经元（C）**：遮掉前 10 维准确率只降不到 1 个点；前 5 维特征幅度 0.1–0.5（只有 4055 约为 2，原文 3 维约为 10）；原文 3 维排到 176–4080 名；按原文规则只剩 0–1 维，probe 53–66%；自动规则选出的 2–21 维为 55–77%。
- **仍有分布式信号，但没有通过词面对照（B、D）**：重训 AUC 0.91–0.98，等长分层 AUC 0.82–0.97，长度不能完全解释。但两版都清楚、只差末尾无关短语时，probe 照样能分开（AUC 0.87–0.99），并把未加短语的一版 89–93% 判为歧义。这个信号的主要成分是"后面有没有多一段限定词"。

对后续的含义：要证明模型内部有"缺信息"本身，需要两边没有系统性词面差别的对照，例如真缺失 vs 等长无关文本；AmbigQA／SituatedQA 的构造做不到这一点。

## Run 记录

| run ID | 内容 | 实现 commit | 状态 |
|---|---|---|---|
| full-is-ambiguity-probe-qwen35-9b-20261116-210747 | Qwen：忠实版 + 修正版 + 词面对照，两种前缀，三个位置，32 层（forward 66256648，probe 66256649） | 9570088 | 完成 |
| 同上，`analysis/faithful/` | LLaMA 3.1 8B 原模型核对（66284263） | 5b39d52 + 未提交的 `ambiguity_faithful.py` | 完成 |
| 同上，`analysis/qwen_massive/` | Qwen 首 token 与大激活检查 | 5b39d52 + 未提交的 `qwen_massive_check.py` | 完成 |
| 同上，`analysis/bos_ablation/` | LLaMA BOS／padding 消融（66305651） | 5b39d52 + 未提交的 `ambiguity_bos_ablation.py` | 完成 |

后三项用的是提交前的脚本版本；本次提交的版本只做了可读性重构，输出键与计算不变（HiL 部分逐字节比对，BOS 消融用合成数据跑通）。

## 限制

- Qwen 部分不是原文模型，数值不能与原文直接比较；与原文可比的只有 LLaMA 核对。
- AmbigQA 的消歧版是改写，不完全是插入；SituatedQA 是插入。
