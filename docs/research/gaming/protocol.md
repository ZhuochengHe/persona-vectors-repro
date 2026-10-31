# Gaming论文Figure 3：Qwen3.5-4B迁移复现方案（规模与扫层已确认）

状态：2026-10-30用户已确认Qwen3.5-4B、统一Transformers、建议规模，并指定按我们的方法sweep选层。已提交完整预检和依赖链；正式设置及任务ID见[记录18](studies/altruism-figure3.md#evidence-18)。总预算含新增扫层为2600条。

## 目标与正文位置

论文：[Persona Vectors in Games](https://arxiv.org/abs/2603.21398)，v1。Figure 3对应§4.2：六种游戏中，altruism评分随正负steering系数β的变化。方法见§3.1–3.5；提取prefix见Appendix A；coherence rubric见Appendix F；退化曲线见Appendix G Figure 8。Figure 4才是实际金额曲线，不把它误称为Figure 3。

六个panel：Dictator、Trust、Ultimatum、Overfishing、Prisoner's Dilemma、Apology。它们是给定游戏描述下的独立决策与简短解释，不需要实现两模型完整对局。Overfishing的故事涉及连续季节，但本文任务询问第一季行动；不另实现多轮模拟。

本轮只需新增altruism向量。forgiveness、expected_altruism和expected_forgiveness是后续扩展，不在Figure 3必要范围。不能用evil或sycophantic方向代替，也不能跨模型直接使用作者Qwen2.5向量。

## 数据与代码证据

固定repo：[johnathansun/persona-vector-agents](https://github.com/johnathansun/persona-vector-agents)，commit `2ae96c5e0ac29ac9ecd5ac54b947ad44d2423c3a`。只下载了相关代码和JSON供检查（项目本地缓存），未下载约500MB的整个历史结果集合、未执行其安装或API入口。

关键文件：

- `data_generation/trait_data_extract/altruism.json`：当前为40道提取题、5组正负instruction与原rubric。论文§3.1写50道题、5正5负共500条，repo问题数不同。复用已有题目/prefix，不重新调用Claude生成。
- `data_generation/trait_data_eval/altruism.json`：13个字典式问题；0–5是Figure 3的自身行为，6–12涉及他人预期/Agent 2角色，不混入本次主图。
- `altruism_v3.json`：6道文本式游戏题，与公开Figure 3结果CSV的六题逐字一致。`altruism_v1.json`有部分0–10/0–5金额上限，不能因为CSV文件名含game_v1就误用它。
- `analyze_results.ipynb`第33–34格读取v1目录下β=-5..5的11个CSV，以altruism均值和95%CI画2×3子图。抽查β=1文件共300行、每游戏50条；其六题匹配当前altruism.json前六题及altruism_v3，而非旧altruism_v1。
- `scripts/eval_steering.sh`：Qwen2.5-7B-Instruct、1-based L20、`steering_type=all`、β=-5..5整数网格。脚本本身没写rollout数量，不能把当前Python默认10当作公开图的50。
- `generate_vec.py`：raw response-mean正负差，过滤正trait≥50、负trait<50，双方coherence≥50；不做L2归一化。作者向量含embedding索引，读取`vector[layer]`；我们的向量不含embedding，读取`vector[layer-1]`，须显式适配。

## 采样：原文、代码和本次适配分开

论文没有明确列出top_k/repetition_penalty等完整采样表。不能把代码继承值写成论文明确指定。

| 项目 | gaming公开代码 | Qwen3.5本次建议 |
|---|---|---|
| 模型 | Qwen2.5-7B-Instruct | Qwen3.5-4B，固定此前revision851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a，非thinking |
| temperature | n_per_question>1时1，=1时自动变为greedy0 | 显式1；即使每个prefix只提取1条，也保持随机采样，不触发旧入口greedy分支 |
| top_p | HF steering入口默认1 | 显式1 |
| top_k | HF调用未覆盖，Qwen2.5固定模型generation_config为20 | 显式20，不依赖Qwen3.5文件默认值 |
| repetition_penalty | HF调用未覆盖，Qwen2.5默认1.05 | 建议显式1.05，与上一轮双参数配置一致；记录为适配，不称为Qwen3.5官方默认 |
| 长度 | max_new_tokens1000，min_new_tokens1 | 同样1000/1，保存EOS及截断 |
| 注入 | all：整段prompt及所有decode，单L20 | 同样all；通过开发集16层×4系数sweep选择，不固定20层 |
| β=0 | vLLM | Transformers，与非零系数统一 |
| β≠0 | Transformers BF16 | 同一Transformers运行时、BF16、显式SDPA |
| judge | GPT-4.1-mini概率加权 | 按此前约定Luna直接评分、不校准，注明与原文差异 |

vLLM路径传入SamplingParams且未显式写top_k/repetition_penalty，两条路径实际继承行为还与vLLM版本有关。当前尚未运行原vLLM环境核验，不能把推测的vLLM默认值当成已测事实。统一HF是用户已同意的本次控制。

Qwen3.5固定revision的generation_config.json公开地址返回404，本方案不据此猜其默认采样值，全部显式设置。即便权重配置后来更新，也只用固定revision。

## 管线与预检

1. 从固定repo复制altruism题目、5组正负prefix和rubric，保留来源与哈希；另建gaming任务适配器，不把游戏字典题直接塞进只接受字符串的旧builder。
2. Qwen3.5按正负prefix生成、Luna评分和配对过滤；teacher forcing提取response token平均激活差。保存各层32×2560向量，再由开发集选层。不要归一化raw向量。
3. 检查chat模板、assistant-turn EOS、1-based层号、向量模型元数据与形状；all hook与作者实现短生成对照、α=0等价及hook清理。原repo[embedding+blocks]索引与我们[blocks]索引分开处理。
4. 记录保留配对数和逐层向量范数；有效配对至少20、覆盖至少10题/3组prefix。若没有足够正负对，不进入正式游戏评估，不静默放松阈值。
5. 先开发集扫层：16层×β={0.4,0.8,1.2,1.6}×5个独立游戏变体×4次，加20条共享基线，共1300条；主coherence≥75、补充≥80，达标且有充分数值评分覆盖时最大化trait配对增量。冻结主选层后，在Dictator/PD/Apology开发变体上β={-1,-0.5,0,0.5,1}、每格4次，共60条，用独立pilot seed查方向、格式和退化。
6. 正式Figure 3：六游戏×冻结β网格×rollout，逐条保存利他分数、coherence、回答、token与配置。画六panel评分曲线，所有β都保留，不能仅删除低coherence系数。
7. 补充报告金额/合作率、无法提取比例和重复率，作为评分是否只反映措辞的诊断；不强制改变原prompt来索取JSON。只在原回答有明确决策时解析，不把非法或含糊决策补成0。

β不能跨模型按数值直接比较。首轮以原文-3..3为候选范围；预检若已退化，正式网格改为较小范围必须先记录，不能凭evil方向的阈值推断altruism也一样。Luna与GPT-4.1-mini的绝对分数也不直接等同。

## 规模（已选建议档，额外增加开发集扫层）

提取每组prefix仅1次随机采样；正负各计1条。正式各rollout使用不同seed、各β配对seed。

| 方案 | 新向量提取 | Figure 3评估 | 预检 | 总新回答数 |
|---|---:|---:|---:|---:|
| 轻量 | 20题×5对prefix×2极性×1=200 | 6游戏×7β×10=420 | 60 | 680 |
| 建议 | repo全部40题×5对×2×1=400 | 6游戏×7β×20=840 | 60 | 1300 |
| 更接近公开图 | repo全部40题×5对×2×1=400 | 6游戏×11β×50=3300 | 60 | 3760 |

7β暂拟{-3,-2,-1,0,1,2,3}；11β为-5..5整数。预检独立，不混入正式样本。原文50题在当前repo缺失，第三档也不是完全同条件复制。建议优先保证新向量的40题/5组覆盖，评估每格先20次；只缩rollout，不减少六个panel。

## 已确认与后续注意

- 用户已定：Qwen3.5-4B、统一Transformers、建议档400提取/60预检/840正式；采用开发集sweep而非固定L20。执行采样显式top_k20/rep1.05。新增扫层1300条，总计2600条。
- 默认建议Luna维持不变、先只做altruism，forgiveness与预期向量后置。
- 游戏主实验没有明确的人类总体分布，CI以同一prompt的rollout变异为对象，不能把20次rollout说成20道独立题。
- 先检查公开问题版本与保存向量索引，再实现adapter；不原样运行带OpenAI API凭据要求的入口。

结果：完整任务链已提交，尚无正式gaming行为结果、无Drive ID；run及任务ID见记录18，不使用其他实验归档ID。
