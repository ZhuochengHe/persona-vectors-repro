# 研究与实验总入口

从研究问题进入，按稳定研究ID找记录，再用run ID定位原始产物。这里不维护逐次提交历史或复制实时进度。

| 研究线 | 高层分析 | 实验记录 |
|---|---|---|
| 原论文复现 | [问题、证据与后续](persona-vectors/overview.md) | [pv-extraction](persona-vectors/studies/extraction.md)、[pv-steering](persona-vectors/studies/steering.md)、[pv-monitoring](persona-vectors/studies/monitoring.md)、[pv-training](persona-vectors/studies/training.md)、[pv-remaining](persona-vectors/studies/remaining-work.md) |
| Steering × 解码策略 | [问题、证据与后续](steering-decoding/overview.md) | [sd-model-control](steering-decoding/studies/model-control.md)、[sd-sampler-ablation](steering-decoding/studies/sampler-ablation.md)、[sd-model-layer-transfer](steering-decoding/studies/model-layer-transfer.md)、[sd-distribution](steering-decoding/studies/token-distribution.md)、[sd-confirmation](steering-decoding/studies/independent-validation.md) |
| Gaming迁移 | [问题、证据与后续](gaming/overview.md) | [gaming-altruism](gaming/studies/altruism-figure3.md) |

## 按层次找文件

| 层次 | 唯一职责 |
|---|---|
| `<研究线>/overview.md` | 研究问题、假设、证据链接、解释边界和下一步；不堆每次状态 |
| `<研究线>/protocol.md`、`protocols/` | 稳定的方法与预先固定的实验规则 |
| `<研究线>/studies/<稳定名称>.md` | 一个可解释的研究问题及其所有对照、run、结果和限制 |
| [run_registry.json](run_registry.json) | 研究ID→记录→引用run→本地路径模板与已确认Drive文件ID |
| `${PV_WORK}/runs/<run_id>/` | 冻结配置、源码、题目、回答、评分、向量、汇总和日志 |

## 维护规则

1. 补模型、层、系数、seed、恢复失败任务或更新进度：更新已有study，不创建新文件。不同run在同一study中增加一行或证据小节。
2. 新建study必须有新的研究问题/可区分的对照目标，先分配稳定ID并登记在run_registry.json；文件名用语义名称，禁止递增编号、时间戳、latest/final/v2等临时命名。
3. 新run的数据目录仍然独立、不可覆盖。合并文档不合并不同模型、采样、向量或EOS协议的原始数据。
4. 高层解释只在对应overview维护，完整数值只在study维护；引用已有表格，禁止另开每批summary文件。已有历史批次汇总只作证据保留。
5. 不创建修复日志、审查报告或工作日记，除非用户明确要求。
6. docs/ideas、docs/plans、docs/experiments旧入口和experiment_records编号路径只是兼容链接，不再写新文件。冻结作业仍可通过旧路径回写同一份study；不能给同一文档安排并发写入。
7. 更新study后运行`python scripts/sync_research_registry.py`同步run引用。新增Drive文件需要把确切ID登记到registry的archives项；没有上传就留空。

## 执行、论文与归档

- [运行手册](runbook.md)、[归档规则](archive.md)、[论文/文献入口](../papers/README.md)。
- 根目录[AGENTS.md](../../AGENTS.md)给出存储路径、真值优先级与HPC约束；英文[README](../../README.md)只做代码文件导航。
- 旧路径兼容不代表旧文本的pending状态仍有效；查进度需核对具体作业和产物。
