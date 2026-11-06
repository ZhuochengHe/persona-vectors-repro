# Assistant Axis 被引阅读

[打开独立Google Doc](https://docs.google.com/document/d/11tsm0krcXAGAMhL-UUjZnidLEOUgft84DYlPaKrnkVU)

本集合独立于原Persona Vectors阅读表。种子为[The Assistant Axis](https://arxiv.org/abs/2601.10387)，只从直接被引列表收集候选，不递归扩展；种子本身作为基础阅读单列。

## 筛选与细读

先读全部候选的标题和官方摘要，保留逐篇keep／exclude／pending及理由。标题或摘要含persona的论文保留在候选集中，但不自动进入精读。优先考虑默认Assistant身份、persona几何、长程漂移、稳定化、表征读写及行为分离；其他人格应用按独立贡献选择代表，不按引用量凑名额。

相关性分核心相关／问题相关／方法参考；精读优先级分A／B／defer。机构、会议和引用量只能作辅助信号，不能替代证据。区分源列表报告的直接引用与正文参考文献核实；精读时定位种子引用及实际使用方式，不能把主题相似写成引用已确认。

精读笔记交代Research question、任务、摘要一句话Major finding、benchmark／validation、方法与贡献、具体limitation、Future work及证据范围。区分作者提出与阅读推演；Additional think留空供用户写。Theory仅用于正式数学命题与证明，不为公式或几何实验自动标注。无需模型架构列，必要的模型和任务设置放Validation或贡献中。

按研究问题分组，使用独立稳定ID。原Persona Vectors表中已有的文章也可以纳入本集合，但不改原ID／笔记／筛选历史。批量任务先完成筛选，再让workers按不重叠ID输出证据，协调者统一写Doc和仓库文件。

## 文件与维护

- `sources/`：不可覆盖的直接被引快照、官方摘要及抓取manifest。
- `screening.json`：逐篇筛选判断与精读去向。
- `reading.json`：入选论文结构化笔记；不与原文献CSV或Excel对齐。
- `reading.md`：本地可读镜像。
- `google_doc.json`：独立Google Doc的真实ID、revision和标题锚点。

Google Doc为日常阅读／编辑入口，原文和笔记ID可点击；总表列ID、短标题、类型、状态、Task、Major finding（摘要）、Benchmark／Validation，长贡献与局限放每篇正文。总表横向，正文竖向。具体样式沿用[维护合同](../literature_document_maintenance.md)，但本集合明确不参与Windows／仓库Excel同步，也不要求架构字段。后续修改先读live Doc，按ID合并用户笔记；不重放初始化覆盖已有文档。

开始工作先检查`git status`并安全`git pull --ff-only`；若dirty／diverged导致无法安全拉取，报告并保留现有修改，不stash／reset。完成后提交可复用改动和阅读内容，分别保留证据范围。只有来源快照覆盖范围内的数量可称已收集，不宣称所有数据库完整。

## 当前覆盖

来源快照95条arXiv记录，官方标题／摘要初筛保留89、排除5、待核1；从保留集选43篇做正文与相关附录定向细读，另列AA00种子原文，共44条阅读笔记。43篇被引关系均在原文核实（42篇HTML、1篇PDF），不把单一数据库快照当作跨库完整集合。AA-C046的标题与当前摘要议题不一致，留待核实，没有据标题猜写贡献。未精读的保留条目仍留在screening，不等于已经判为低质量。

条目ID AA00／AA01–AA43独立于原表；候选AA-C编号用于引用来源追溯，后续新增不重编号。网页可编辑笔记；本地`reading.json`／`reading.md`保存可审阅工作源，当前没有自动双向同步。`sources/coordinator_checks.json`保留关键高风险解释的交叉核验。

抓取：`python scripts/collect_assistant_axis_citations.py`（已有sources时拒绝覆盖）。渲染：`python scripts/render_assistant_axis_reading.py --requests-output /tmp/assistant_axis_requests.json`（仅NEW-document初始化，绝不能重放到现有Doc）。live原生表格、链接、独立横向section需按当前结构维护，范围与revision以`google_doc.json`为准。
