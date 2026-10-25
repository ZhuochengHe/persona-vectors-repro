# E02：等范数随机方向对照

## 做了什么

固定evil第19层，使用完整重提的新向量，以及3个固定种子（101、202、303）的Gaussian随机方向。每个随机方向缩放到与persona向量相同的L2范数，约4.3499；不刻意正交化。

各方向都用α={0.1,0.25,0.5,1}，相同10题、每题4次、配对seed。共640条steered回答及40条共享基线。注入为response模式，测trait、coherence、重复4-gram比例和截断。

## 结果

| α | persona trait | persona coherence | 随机trait均值 | 随机coherence均值 |
|---:|---:|---:|---:|---:|
| 0.1 | 0.36 | 87.58 | 0.10 | 89.35 |
| 0.25 | 3.10 | 80.65 | 0.13 | 89.96 |
| 0.5 | 12.82 | 58.05 | 0.04 | 89.92 |
| 1.0 | 41.52 | 13.38 | 0.09 | 88.02 |

无干预coherence为89.45。α=1时persona方向的重复4-gram比例约27.3%，随机方向3种子均值约2.6%。

## 结论

同层、同范数的随机方向没有产生同等退化，因此“只要扰动这么大就会崩溃”不足以解释现象。方向本身很重要，但当前对照不能确定persona方向是否同时编码了重复、风格或其他混杂特征，也不能证明安全训练是原因。

## 对应Drive归档

| 实验 / run ID | Drive文件ID | 下载 |
|---|---|---|
| `eval-evil-random-control-20261023-144307` | `1-UAyz24DXqWA7sYwsRrUizZkCrodRs96` | [ZIP](https://drive.google.com/file/d/1-UAyz24DXqWA7sYwsRrUizZkCrodRs96/view?usp=drivesdk) |

## 归档内看哪些文件

- `summary.json`汇总全部17个条件；`vectors/*.json`记录各方向范数、seed及与persona方向的余弦。
- `responses/`、`scored/`及`metrics/`保存完整回答、judge评分与逐回答重复率。

[返回实验索引](README.md)
