# Windows 文献阅读表与 WSL 工作流程

Windows 主阅读表：`D:\umich\research\persona\persona_literature.xlsx`。
WSL 对应路径：`/mnt/d/umich/research/persona/persona_literature.xlsx`。

仓库已备好 [Excel](persona_literature.xlsx)：32篇，包含最初的Persona Vectors和游戏应用两篇，以及精选30篇。Title、Link、Key words、One sentence/topic、Contributions、Limitation均已填写；Additional think全部留空。机构／会议和阅读深度另外标明，未把未核实接收写成顶会。

## 分工

- WSL中的仓库：检索、筛选、引用溯源、正文证据和导出脚本。
- Windows Excel：高层整理、分组阅读、阅读状态和你自己的想法。
- 总清单继续保存在仓库，Windows只放32篇主阅读表，不复制376条原始候选作为默认工作量。

## 本地接手

1. 拉取包含本文和AGENTS.md的提交。文献任务从本文开始，不依赖尚在单独整理的实验文档。
2. 在本地WSL确认D盘确实挂载，检查目标目录及已有xlsx。不得在HPC创建假的`/mnt/d`目录。
3. 若是首次使用，目标目录不存在时可在确认D盘挂载后创建；可以直接复制仓库中的xlsx，或运行下述导出命令。
4. 若目标Excel已经存在，不直接复制覆盖。先关闭Excel，再用导出脚本读取、备份和合并；没有内部合并基线的外来表会停止，需先检查迁移。

需要重新导出时，在本地WSL的仓库根目录运行；依赖装在虚拟环境中：

```bash
python3 -m venv .venv-literature
.venv-literature/bin/python -m pip install -r scripts/requirements-literature.txt
.venv-literature/bin/python scripts/export_literature_workbook.py
```

脚本默认写入上述WSL路径，要求父目录已经存在。若Windows目录不可访问，会明确停止，不自动回退或创建替代挂载。

本仓库内的可交付副本这样生成：

```bash
python scripts/export_literature_workbook.py --output docs/papers/persona_literature.xlsx
```

## 表格与更新约定

- Papers是主表，可筛选、排序，冻结了表头和编号／标题。
- ID是稳定论文编号，不是当前行号。1为原论文、2为游戏应用；3–32为精选。新增论文在目录中分配未使用的新ID，不重编号。
- Related paper填的是主题或方法相关编号，不代表已确认互相引用。
- Additional think只由你填写，生成器从不覆盖；Read status也保留。
- 其他列使用三方合并：只有当前值仍等于上次生成值时才更新，已经手改的内容保留。用户删除的已有行不会自动恢复。
- Guide解释字段。隐藏的_ExportState保存源键、ID和上次生成基线，复制Excel时保留它。
- 更新已有目标文件前会生成同目录backup副本。Excel锁文件存在时停止；保存用临时文件后替换。
- 贡献、局限是目前阅读范围内的综合笔记；局限栏也包含尚需核对的问题，不能理解为所有论文都经过完整方法审计。

## 源文件

- [筛选规则](citation_screening_rules.md)：后续筛选基准。
- [精选CSV](citation_screening_shortlist.csv)：30篇的已核查贡献、局限和机构／会议状态。
- [稳定编号、关键词和一句话主题](citation_screening_sources/workbook_catalog.json)：32篇的人工作品目录；序列各字段依次为源键、ID、关键词、一句话主题、相关ID。
- [导出脚本](../../scripts/export_literature_workbook.py)：32篇合并、样式和用户修改保护。

本次在Great Lakes生成并随Git保存，尚未写入用户Windows目录。本地接手后再完成该路径的首次交付；不要把仓库副本描述成已送达D盘。
