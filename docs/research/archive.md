# 实验归档

源码公开仓库与实验产物分开保存。GitHub包含代码、配置模板、测试、实验策略及结果文档；Drive保存原始实验记录，方便单独分享。

[打开Google Drive实验文件夹](https://drive.google.com/drive/folders/1Y9fgfox6sSKq2qOig1c53hWE8oMZIZuZ)

按研究问题组织的中文说明见[研究入口](index.md)，run与已确认Drive文件ID集中在[登记表](run_registry.json)。Drive的[experiment-records文件夹](https://drive.google.com/drive/folders/1apVr0qwyjlxgrXi3PgUmB32hljJ54qcS)保存的是此前上传的旧编号文档；此次本地重组尚未同步到Drive，不能把它当作新目录的镜像。

## 归档内容

- 按scratch中的run目录分别生成ZIP，保留相对路径；原始失败和恢复run也保留，以免误把旧结果与修正协议混在一起。
- 包含Slurm stdout/stderr、阶段日志、实际配置、代码快照、环境记录、任务、回答、评分、指标、向量及完成标记（原目录中存在时）。
- 另存公共Slurm日志、run指针/环境记录和项目文档；`files-manifest.csv`按文件列出大小与SHA-256，`SHA256SUMS`校验ZIP本身。
- 不包含模型或LoRA权重、优化器状态、虚拟环境、下载缓存、完整训练数据、Git内部目录或凭据文件。E08训练日志与配置保留；adapter权重仍在原存储。
- 导出不改写原实验文件。若文本中发现凭据模式，仅在导出副本中脱敏，数量记录在清单；私人存储路径保留在Drive原始实验记录中。

## 阅读顺序

先从[研究入口](index.md)定位study，再在[统一登记表](run_registry.json)查run和实际Drive文件ID。各研究记录列出汇总和ZIP内路径；冻结run配置与源码优先于当前模板。没有Drive ID不代表已归档。

历史E01/E02/E06部分结果使用旧回答结束协议；不要与修正后的`explicit-generation-v3-turn-end`输出直接合并。各次复用来源及向量哈希保存在对应manifest中。当前public仓库的路径参数化只便于迁移，不会改变归档中的历史记录。

Drive文件夹保持当前账户默认访问权限；可以直接在Drive里为需要的对象或整个文件夹设置分享权限。
