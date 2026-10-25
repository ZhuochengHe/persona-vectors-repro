# E02诊断：小系数、向量边界和实际扰动

## 做了什么

固定evil第19层补测较小系数；在同一批有效正负配对上比较旧response边界与第一个EOS前的内容边界；以同一模型、同一向量比较我们的hook和upstream hook，并检查cached生成与完整历史重放。另在40条无干预回答上测block输出L2范数。

## 结果

早期小系数补测（旧向量/历史协议）：

| α | trait均值 | coherence均值 |
|---:|---:|---:|
| 0.1 | 0.05 | 87.42 |
| 0.25 | 1.38 | 79.70 |
| 0.5 | 14.46 | 59.85 |
| 0.75 | 32.25 | 34.33 |
| 1 | 44.12 | 19.55 |

- 同一25对样本重放旧提取实现时，32层向量被精确复现；修正边界后的第19层方向与旧方向余弦约0.99995，范数4.3615→4.3875。边界修正需要保留，但没有恢复α=1时的连贯性。
- 完整重提evil后，第19层范数为4.3499。无干预平均activation范数约14.125，因此α=1的相对扰动约30.8%，α=0.1约3.1%；这里只代表这40条回答的测量。
- 0、0.1、1三个系数的短生成对照中，我们与upstream hook的token一致；cached与正确完整重放在13个预测位置的top-1一致率为1。最初runtime归档保留初次尝试，有效比较以115342归档的result.json为准。

## 结论

没有证据表明raw-vector注入位置或短序列cache计算与upstream存在主要偏差；这不等于所有长序列或所有运行路径都无bug。缩小系数可以保住连贯性，但evil提升也随之减弱。α的数值不能独立于向量范数、层及activation强度解释。

## 对应Drive归档

| 实验 / run ID | Drive文件ID | 下载 |
|---|---|---|
| `e02-evil-small-alpha-20261023-101344` | `1UItEBgN1sDwppFdLq8GZBG-gVISGLqfL` | [ZIP](https://drive.google.com/file/d/1UItEBgN1sDwppFdLq8GZBG-gVISGLqfL/view?usp=drivesdk) |
| `evil-vector-boundary-20261023-121712` | `17BYDH0NRSKy74DBNYcyZM6pXrSubZbXe` | [ZIP](https://drive.google.com/file/d/17BYDH0NRSKy74DBNYcyZM6pXrSubZbXe/view?usp=drivesdk) |
| `perturbation-norm-20261023-141237` | `1ki2k7ofakvVFdTu9TYelgyTVPCzMjH0s` | [ZIP](https://drive.google.com/file/d/1ki2k7ofakvVFdTu9TYelgyTVPCzMjH0s/view?usp=drivesdk) |
| `runtime-interactions-20261023-114603` | `1hJ3-XOiPqc9k9In3dTh4GnPeEqHA_r86` | [ZIP](https://drive.google.com/file/d/1hJ3-XOiPqc9k9In3dTh4GnPeEqHA_r86/view?usp=drivesdk) |
| `runtime-interactions-20261023-115342` | `1a0_G6VnEslX3mVrmbkmGzLg-jY-IAr6V` | [ZIP](https://drive.google.com/file/d/1a0_G6VnEslX3mVrmbkmGzLg-jY-IAr6V/view?usp=drivesdk) |

## 归档内看哪些文件

- 小系数归档：`heldout-summary.json`和逐条件回答/评分。
- 边界对照归档：`vector-comparison.json`、`diagnostic-summary.json`、`original_vectors/`、`vectors/`。
- 范数归档：`result.json`；runtime有效对照归档：`result.json`及`hook_comparisons`、`cache_comparisons`字段。

[返回实验索引](README.md)
