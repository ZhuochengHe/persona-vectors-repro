# Persona Vectors原论文复现

## 问题与范围

复现persona方向提取、推理steering、prompt监测、微调漂移及干预。当前主要基座为Qwen3.5-4B；Qwen2.5-7B模型对照归入[采样与steering研究线](../steering-decoding/overview.md)。

## 方法入口

- [复现协议和适配决策](protocol.md)、[原文实验目录](paper-inventory.md)。
- [工作包具体协议](protocols/)：E01、E02、E06、E08、E09、E10、E11、E19。
- [历史提交上下文](submission-history.md)仅供追溯，不作为实时状态表。

## 证据与尚未完成的工作

- [E01：persona vector提取](studies/extraction.md)（`pv-extraction`）
- [E02：注入、选层与方向对照](studies/steering.md)（`pv-steering`）
- [E06：prompt投影与行为监测](studies/monitoring.md)（`pv-monitoring`）
- [E08：微调与后续评估](studies/training.md)（`pv-training`）
- [其余复现工作包与依赖](studies/remaining-work.md)（`pv-remaining`）

原始与修正后的EOS协议、不同采样配置、不同选层规则不能混成一组结果。E08 adapter训练完成不代表行为/能力评估完成；具体完成情况查研究记录和对应run。跨实验高层解释只在本页维护，数值表留在研究记录。
