# 文献阅读文档：格式与维护

Assistant Axis的独立被引阅读遵循[单独维护约定](assistant-axis/README.md)：使用Persona Google Doc中的“Assistant Axis 被引阅读”分页，筛选与阅读JSON／Markdown仍单独维护，不更新原文献CSV／Excel，不设置架构字段。以下跨Excel同步规则仅适用于原Persona Vectors阅读集合。两集合共用document_id但tab_id不同；读取、索引链接及写入范围必须明确分页，标题锚点不可沿用旧独立文档的ID。

## 阅读入口与职责

[Google Doc](https://docs.google.com/document/d/1YZAZDvTuybzJkV-fI60UDMioMRm1ckEho8IR_t276Ro) 是日常阅读、批注和长笔记入口。保留同一个文件及URL，不因更新新建副本。它包含原生表格、可点击索引和正文标题；不是把Excel整张宽表复制过去。

| 位置 | 职责 |
| --- | --- |
| Google Doc | 面向阅读的索引、研究问题、详细笔记与用户思考 |
| `literature_reading.csv` | 按稳定ID保存的结构化内容及合并工作源，便于Git审阅 |
| `workbook_catalog.json` | 稳定source key／ID、关键词、主题与关联编号 |
| `literature_reading.md` | 从CSV生成的本地可读镜像，含论文表和稳定锚点 |
| Windows／仓库xlsx | 筛选、排序、阅读状态及离线查看；保留用户编辑 |
| 原筛选CSV与证据文件 | 收集溯源及筛选记录，不因阅读界面调整而重建 |

线上与本地同时存在编辑时，不以位置或文件时间强行判定谁覆盖谁。先读线上Doc及用户通知涉及的Excel，按ID和字段合并，再更新各视图。线上索引是正文元数据的摘要，正文已读深度不能由索引标签推定。

## 格式合同

1. **首页导航**：标题、简短使用说明、六组研究问题入口、按Paper type查找。索引中的ID链接到对应论文标题，不只列不可点击的编号。
2. **论文总表**：原生Google Docs表格，按ID递增；八列为ID、论文短标题、Paper type、Architecture、Read status、Task、Major finding（摘要）、Benchmark / Validation。Task写实际实验任务；Major finding从作者摘要提炼一句话；Validation列出benchmark、任务环境与关键条件，区别问卷、答案token概率、生成文本与实际执行动作。ID链接到笔记，短标题链接原文。短标题只是显示别名，正文保留完整英文标题；未指定别名的新论文使用完整标题。
3. **详细笔记**：按研究问题分组；每篇只出现一份正文。跨组关联使用链接，不复制同一段笔记。各研究问题另起页；论文之间连续排版。
4. **单篇顺序**：完整标题及稳定ID → 分类／状态／优先级 → 原文 → 模型与架构（实测模型、骨干、实际输入／推理模式、证据） → Research question → 一句话主题 → 方法与贡献 → 局限与解释边界 → Future work → Additional think → 关联论文、关键词、机构／会议、证据范围 → 返回论文总表。
5. **标题层级**：TITLE为22pt，SUBTITLE为13pt；研究问题与总表为HEADING_1（18pt），论文为HEADING_2（16pt）。字段标签加粗但不加入大纲，避免每篇×多个字段淹没导航。标题与字段标签保持与下段相连。
6. **表格**：9pt，八列宽22／104／55／64／38／102／185／200pt，总宽770pt；总表单独使用A4横向section、左右36pt边距，前方导航与后方详细笔记保持竖向、左右72pt边距；首行加粗、浅色底、固定为跨页重复表头，隔行轻底色，单元格内边距3pt，单倍行距、段后0pt。说明文字使用正文样式，不继承标题的分页或字号。
7. **内容**：RQ写问题，贡献写方法与发现，limitation围绕真实证据边界，避免重复的防守性套话。Theory仅用于正式数学命题与证明；分类允许多选，部分阅读的标签仍属工作判断。用户笔记原样保留，除非用户明确授权编辑。

总表适合浏览与跳转，不具有Excel同等的自动筛选和公式能力。长RQ、详细贡献和局限放正文；总表保留Task、摘要一句话发现与精简验证条件，避免把整段解读塞入单元格。

## 修改流程

### 每次开始

- 读取`citation_screening_sources/google_reading_doc.json`确认真实document／tab ID，再用Docs工具读所有相关tab及当前revision。
- 对比线上内容与CSV。格式调整也先确认用户是否改了正文；保留文字、原文链接、用户笔记与阅读状态。
- Task、Major finding、Validation在总表中维护；按ID读取这三列的在线编辑并回同步CSV，详细笔记不重复保存同一短摘要。
- 表格、标题锚点、样式均从实时结构读取；不要把历史index当成固定地址。Google Docs索引按UTF-16计算。

### 更新已有论文

- 按稳定ID定位正文，只修改相关字段；每批使用`requiredRevisionId`，遇并发冲突重新读取并合并。
- 若变更分类／状态／标题／RQ或分组，更新相应总表单元格、类型索引、研究问题索引；关联论文编号维持可点击。
- 不重建全文，不删除原生表格再用纯文本替代。格式修改保留用户文字。

### 新增论文

- 查重，给新source key分配未使用ID，追加CSV与catalog；不重编号。
- 在总表底部新增一行，给对应研究问题增加一篇正文，并更新类型与研究问题索引。新问题可新建分组；正文仍只有一份。
- 用实时heading ID建立ID→笔记、关联ID→笔记、返回总表三个方向的链接。文内表短标题链接论文原文。
- Additional think初始化空白。原精选30篇的筛选历史不因后来追加论文而重写。

### 完成同步

1. 把用户线上修改按ID合并回CSV，保留明确清空的字段。当前没有自动Doc双向导入，需agent逐字段合并，不能声称已自动同步。
2. 本地运行`python scripts/export_literature_reading_doc.py`生成Markdown镜像。`reading_doc_layout.json`保存短标题与总表布局；研究问题分组目前在生成器`GROUPS`中。
3. WSL可访问Windows时，按[Excel交接流程](handover_paper_excel.md)同步Windows和仓库xlsx；每个目标仅保留最近一份backup。Slurm例外按AGENTS.md执行。
4. 用connector读回受影响区域，核对论文总数、表格行列、标题和链接目标，确认用户笔记。涉及分页、列宽、重复表头时导出PDF检查，不能仅凭API成功声称布局正确。
5. 更新Doc注册文件中的实际revision、标题锚点及格式版本，提交相关CSV／镜像／文档改动。若某视图无法写入，明确记录待同步项。

只有格式、索引或维护说明变化且没有修改任何字段时，不必重导出Excel，以免无意义地替换备份。

## 生成器边界

`export_literature_reading_doc.py --requests-output <临时路径>`输出的是**新文档正文初始化**请求，以及`index_rows`数据；原生表格、内部链接、分页需要随后依据实时Doc结构应用，`native_index_pass_required`明确标识这一点。它不是线上Doc更新器，不能把初始化请求再次发到已有文档。

线上维护必须使用Docs原生请求，保留revision与tab。生成器不包含联网鉴权，也不存储下载凭据。原生Doc身份与最近核验的标题锚点保存在`google_reading_doc.json`；锚点消失时重新读取解决，不复用不存在的ID。

## 并行阅读与架构审计

批量阅读时由subagents分工读论文和官方模型配置，输出有证据的结构化笔记；协调者统一写CSV、目录和Doc。新的架构字段不替代原Evidence scope：前者说明模型设置的核验范围，后者说明论文贡献等阅读范围。

总表架构是紧凑导航，正文保存准确模型、稀疏性、attention／SSM结构、视觉模块、干预位置及实际thinking设置。不要把judge、数据generator或仅做probe的模型列为已steer。每篇缺失的suffix、revision、输入模态、reasoning开关须明确保留未核实状态。标签从已审阅配置读取，不能靠关键词自动把“非MoE”判成MoE。

## 索引摘要证据

`citation_screening_sources/index_summary_review.json`保存Task、Major finding、Validation的逐篇来源。摘要结论保持作者原有范围，方法细节与实验条件可来自已核对正文；不要把结论写成研究问题，也不要将短摘要当作全文核验状态。新增三字段同步CSV、总表、Markdown与XLSX，正文已有贡献／证据不重复维护同一短摘要。用户在Additional think插入的原生表格保留，回同步本地时可用Markdown表格表达，不能摊平后丢失列对应。

Validation使用`【场景】… 【验证】…`：场景说明单轮、多轮、长输入／持续对话／长程环境任务及真实行动证据；验证部分保留原benchmark／条件。明确干预目标agent、用户模拟器、审计工具或离线轨迹，不用“有agent”替代执行验证。证据在各集合的`evaluation_regimes.json`；原始审计伞标签经协调者拆分，不能把long-context与long-horizon混计。

[方向评估](research_directions.md)对应主Doc的独立标签页“方向评估：Agentic 与架构”，tab ID见注册文件。更新时同时读相关tabs；原阅读正文和该分析分别维护，原初始化渲染器不负责更新分析tab。新增主题检索来源另存`direction_review_sources.json`，不回写为冻结种子的直接被引。架构证据变化可以追加核验，但已有用户笔记和阅读状态仍须保留。
