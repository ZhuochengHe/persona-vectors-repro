# 复现框架运行手册

截至2026-10-25，E01/E02/E06及E08的15份adapter训练已实际运行；E08后续评估和E09/E10/E11/E19尚未完成。最新选层、注入位置对照与结果见[实验文档](persona-vectors/studies/steering.md#evidence-followups)，总览见[README](../../README.md)。以下按阶段解释入口，历史默认规模不代表每个run的最终设置；精确复现应使用归档中的冻结config、任务、向量及source。

## 目录和共用口径

- `configs/reproduction.json`：唯一默认配置；模型revision已固定，三个traits、15份训练子集、评分与资源路径明确。
- `src/persona_repro/`：懒加载模型依赖；data、inference_tasks、model、training、judge、operations、analysis/reporting、mmlu、CLI。
- `assets/monitoring_prompts.json`：论文C.3的24条原始提示，已按空白归一化逐条核对。
- `docs/experiments/strategies/`：8个具体策略；输入、对照、默认规模、输出、指标和失败条件。
- `scripts/bootstrap.sh`：在scratch构建独立环境；固定已检查的Transformers源码commit，保存最终环境lock。
- `scripts/run.slurm`：执行单一CLI阶段，默认owned1/spgpu2、1GPU/60G/4CPU/2小时；按阶段调整时限。
- `scripts/checks.slurm`：只运行轻量合成测试，不下载或加载模型。

活动目录：`${PV_WORK}`。scratch不是永久归档。代码与小型报告在home，权重/环境/全量回答/数据/adapter均在scratch；没有自动迁移或清理用户已有数据。

E01当前数量口径：每trait选10题、3组正负指令，得到60个输入条件；每条件3次rollout得到180条回答，三trait共540条。原repo规模保留为历史参考，不是本轮配置。

向量bundle为`{raw: [32,2560], unit: [32,2560]}`，从block输出直接提取、排除最终norm与embedding。层号一律1–32；steering用raw，投影用单位方向。生成期干预末位prefill及随后decode；E11按作者实现训练期干预全部token，正向添加undesired向量，保存前移除。

## 1. 先检查manifest，不做计算

```bash
export PYTHONPATH=${PV_ROOT}/src
python -m persona_repro.cli plan
```

该命令不加载模型、不请求judge。输出包含依赖关系、15个数据版本和固定题目dev/test索引。`--config`是全局选项，须放在子命令之前。

## 2. 独立环境与模型预检

先准备Slurm日志目录，然后在分配内运行bootstrap。模型下载会写scratch缓存。

```bash
mkdir -p ${PV_WORK}/logs
srun --partition=spgpu2 --account=qdj_project_owned1 --gres=gpu:1 --mem=60G --cpus-per-task=4 --time=01:00:00 bash scripts/bootstrap.sh
bash scripts/submit.sh scripts/run.slurm preflight
```

preflight验证non-thinking模板前缀、32层形状、零系数生成、assistant loss mask、文本LoRA目标发现。完整小步训练与缓存/gradient checkpointing兼容性仍需在200题pilot中确认。不要将纯单元测试通过表述为模型兼容性已通过。

模型环境首次安装版本来自明确范围及指定Transformers commit，成功后以scratch中的`environment.lock.txt`为环境快照；已完成安装及真实模型检查；每个run的环境记录以归档文件为准。

## 3. 准备训练数据和MMLU

以下`PV_WORK`变量在本节及后续例子中都需在提交命令的shell定义：

```bash
PV_WORK=${PV_WORK}
bash scripts/submit.sh scripts/run.slurm fetch-data --output "$PV_WORK/raw"
bash scripts/submit.sh scripts/run.slurm prepare-data --dataset-root "$PV_WORK/raw/dataset" --output "$PV_WORK/subsets"
bash scripts/submit.sh scripts/run.slurm prepare-mmlu --output "$PV_WORK/mmlu/test.jsonl"
```

这些阶段有先后依赖，前一个完成后再启动下一个；示例不是无依赖同时提交的脚本。`prepare-data`默认每类1000训练+100开发问题组，Normal/I/II共享题目组，严格检查足量；`--train-size 200`写到另一个pilot输出目录。不要把pilot与正式输出覆盖混用。MMLU数据revision也已固定，分层抽取约1000题、0-shot，仅评估，不用judge。

批量judge只做远端调用、不使用GPU计算；但Great Lakes的spgpu2/arph要求至少申请一张GPU，不能在该QOS下直接用`--gres=none`。如使用其他CPU分区，需先确认账户权限。这里不提供无限并发的整批提交器。运行时全局配置示例：`bash scripts/submit.sh scripts/run.slurm --config configs/natural.json generate ...`。

## 4. E01：提取三个trait向量

以下以evil为例；另两个键为`sycophantic`与`hallucinating`。

```bash
python -m persona_repro.cli tasks extract --trait evil --output "$PV_WORK/tasks/evil_extract.jsonl"
bash scripts/submit.sh scripts/run.slurm generate --input "$PV_WORK/tasks/evil_extract.jsonl" --output "$PV_WORK/E01/evil.responses.jsonl"
bash scripts/submit.sh scripts/run.slurm score --input "$PV_WORK/E01/evil.responses.jsonl" --output "$PV_WORK/E01/evil.scored.jsonl"
bash scripts/submit.sh scripts/run.slurm vectors --input "$PV_WORK/E01/evil.scored.jsonl" --output "$PV_WORK/vectors/evil.pt"
```

按完成顺序执行。生成token IDs、文本、截断标记和seed身份先落盘；judge独立读取，逐条缓存。错误请求不会变成零分；拒绝/无效分数显式记录。原repo式成对trait与coherence过滤固定为50，不增加校准步骤。若没有有效正负对则先写审计再报错，不能输出零向量。向量旁的`.audit.json`包含逐pair排除原因、按题/指令覆盖及截断率；`.json`包含来源hash、模型/评分身份与逐层范数。生成回答保存完整effective_generation_config，防止采样默认值漂移。

## 5. E02/E06：共享生成、评分、投影

```bash
python -m persona_repro.cli tasks eval --trait evil --split dev --output "$PV_WORK/tasks/evil_dev.jsonl"
bash scripts/submit.sh scripts/run.slurm generate --input "$PV_WORK/tasks/evil_dev.jsonl" --output "$PV_WORK/E02/evil_l16_c1.jsonl" --vector "$PV_WORK/vectors/evil.pt" --layer 16 --coefficient 1
python -m persona_repro.cli tasks monitor --trait evil --split test --output "$PV_WORK/tasks/evil_monitor.jsonl"
```

这里layer16/coef1只是命令格式示例，不是已选层。E02先dev集32层×{0,1}扫描，候选层再做系数网格，冻结所选层后测test。每个条件独立文件，零系数也走相同HF后端。

E06按`generate → score → project --mode prompt_last`顺序，以scored文件作为project输入，则投影输出同时保留评分，可直接用于：

```bash
python -m persona_repro.cli analyze E06 --input "$PV_WORK/E06/evil.scored.projected.jsonl" --output "$PV_WORK/E06/evil.summary.json"
```

E06的prompt projection不传入未来回答。C.2的within-condition结果需按提示分别计算并排除score标准差<1的条件，不能仅用总体相关性代替。

## 6. E08/E09/E10/E11：共享训练baseline

```bash
bash scripts/submit.sh scripts/run.slurm train --train-file "$PV_WORK/subsets/evil/misaligned_2/train.jsonl" --dev-file "$PV_WORK/subsets/evil/misaligned_2/dev.jsonl" --output "$PV_WORK/adapters/evil_II_seed0"
```

对15个类别/版本分别训练。已占用的adapter输出目录会报错；不会覆盖旧模型。普通SFT与E11共用固定子集、seed与步数，E11从同一基座初始化，不继续训练E08 adapter。

用`tasks eval --split test`生成测试任务；`generate --adapter ... → score`评估全部三个traits；`project --mode prompt_last --adapter ...`取得E09投影；同样对base任务评分/投影。保存前确认各文件是同一题目、同一vector、同一层与同一trait。

```bash
python -m persona_repro.cli analyze E09 --base "$PV_WORK/E09/base.merged.jsonl" --input "$PV_WORK/E09/evil_II.merged.jsonl" --output "$PV_WORK/E09/summary.json"
```

对多个模型可给`--input`多个文件。每个merged文件应由scored记录直接投影获得，不需要手工按行拼接。

E10：在相同测试任务上用`generate --adapter ... --vector ... --layer ... --coefficient -1`做反向干预，并使用`mmlu`的相同干预参数。E11：使用下列训练分支，随后评估不传vector/coefficient。

```bash
bash scripts/submit.sh scripts/run.slurm train --train-file "$PV_WORK/subsets/evil/misaligned_2/train.jsonl" --dev-file "$PV_WORK/subsets/evil/misaligned_2/dev.jsonl" --output "$PV_WORK/adapters/evil_II_prevent_c2_seed0" --vector "$PV_WORK/vectors/evil.pt" --layer 16 --coefficient 2
bash scripts/submit.sh scripts/run.slurm mmlu --input "$PV_WORK/mmlu/test.jsonl" --output "$PV_WORK/E08/evil_II.mmlu.jsonl" --adapter "$PV_WORK/adapters/evil_II_seed0"
```

E11只先做策略文档中目标分支与有限网格；正系数含义与E10负系数不同。MMLU字母选择按完整选项token似然，复用同一runtime/hook。结果只称MMLU子集分数。

## 7. E19：微调前数据投影差

```bash
python -m persona_repro.cli dataset-tasks --input "$PV_WORK/subsets/evil/misaligned_2/train.jsonl" --trait evil --category evil --version misaligned_2 --output "$PV_WORK/tasks/evil_II.dataset.jsonl"
python -m persona_repro.cli natural-tasks --input "$PV_WORK/subsets/evil/misaligned_2/train.jsonl" --trait evil --output "$PV_WORK/tasks/evil.natural.jsonl"
```

自然任务用基座`generate`，使用`--config configs/natural.json`得到temperature0/rollouts1（不改变其他实验采样）；对数据原回答与自然回答均用**同一个基座模型**`project --mode response_avg`。原回答teacher forcing，投影层/向量一致，记录prompt hash后配对。禁止对微调模型的自然回答算E19预测特征。

```bash
python -m persona_repro.cli analyze E19 --input "$PV_WORK/E19/dataset.projected.jsonl" --natural "$PV_WORK/E19/natural.projected.jsonl" --base "$PV_WORK/E08/base.scored.jsonl" --finetuned "$PV_WORK/E08/fine.scored.jsonl" --checkpoint-map "$PV_WORK/checkpoint_map.json" --output "$PV_WORK/E19/summary.json"
```

checkpoint_map是显式映射，例如`{"/absolute/adapter/path": {"category":"evil", "version":"misaligned_2"}}`，不能靠路径名猜训练数据。分析会检查题目与模型/向量身份，缺失或重复配对报错。

## 8. 尚未完成的运行验证


剩余真实环境验证：专用依赖环境、Qwen3.5全模型加载与模板mask、梯度重算/LoRA训练、Luna实际请求和严格JSON、MMLU数据实际加载与模板口径。没有增加人工校准步骤。这些验证是接口与运行正确性检查，不是评估judge与人工是否一致。

汇总命令当前每次使用**一个trait的一套向量/层**；E09可以同时输入该trait的多个checkpoint文件，E19可以输入该trait的15份数据投影和对应自然回答。三种trait分别汇总，避免混淆vector_id。相关性表已实现；出版图形、问题聚类置信区间及开发集自动选层器仍需在对应实验执行阶段补齐，目前不会自动给出这些结果。
