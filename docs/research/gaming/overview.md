# Gaming：persona向量与博弈决策

## 问题

Qwen3.5-4B上新提取的altruism方向，能否改变博弈中的利他表现？哪些层在coherence约束下有较好的效果？本轮首先对应gaming论文Figure 3，不能把评分变化自动等同于实际策略变化。

## 当前设计

复用作者的题目/prefix，重新提取Qwen3.5向量；基线与干预统一Transformers，显式控制采样。开发集扫描层/正系数，满足coherence门槛后最大化trait增量，再冻结层进行正式六游戏正负系数评估。模型、judge和选层与原文存在适配差异，必须一并解释。

- [统一协议、规模与原repo采样核对](protocol.md)。
- [唯一执行与结果记录](studies/altruism-figure3.md)（`gaming-altruism`）：提取、扫层、预检、正式Figure 3均在此维护。
- [run/Drive登记表](../run_registry.json)：具体run ID和产物定位。

## 解释边界

游戏评分反映回答中的利他表达，不自动证明金额或合作行为改变。其他trait、实际动作解析或更换模型可作为本研究的新增对照；只有形成独立研究问题时才另开研究记录。实际进度查run，不在这里复制状态日志。
