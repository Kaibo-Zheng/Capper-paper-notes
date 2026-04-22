# GOBoost

## Paper Info

- **Title**: GOBoost: leveraging long-tail gene ontology terms for accurate protein function prediction
- **Authors**: Lei Zhang, Yang Wang, Xiao Chen, Jie Hou, Dong Si, Rui Ding, Bo Jiang, Hailey Ledenko, Renzhi Cao
- **Venue**: Bioinformatics 2025, 41(6), btaf267
- **Paper**: [paper.pdf](./paper.pdf)
- **DOI**: [10.1093/bioinformatics/btaf267](https://doi.org/10.1093/bioinformatics/btaf267)
- **Code**: [Cao-Labs/GOBoost](https://github.com/Cao-Labs/GOBoost)

## Abstract

`GOBoost` 是一个面向蛋白功能预测的长尾标签建模方法。
它认为很多 protein function prediction 方法把任务当作普通 multi-label classification，
但忽略了 Gene Ontology terms 的长尾分布：
宽泛功能标签样本多，具体功能标签样本少，模型容易偏向高频标签。

一句话总结：
`GOBoost` 的核心贡献不是换一个更大的结构编码器，
而是从 GO term 长尾分布出发，同时改 ensemble、label graph 和 loss，
让模型更重视低频但更具体的功能标签。

## Motivation

蛋白功能预测通常要在 MF、BP、CC 三类 Gene Ontology 标签上做多标签预测。
由于 GO DAG 的层级结构越深越具体，深层功能标签往往出现频率低，
训练集中会形成明显的 long-tail distribution。

如果直接用普通 multi-label loss 训练，模型会倾向预测高频、宽泛的 GO terms，
而忽略低频、具体、信息量更高的功能标签。
这会让模型的平均指标看起来还不错，但真正有科学价值的 specific function prediction 不够可靠。

`GOBoost` 想解决的问题就是：
如何让蛋白功能预测模型在长尾 GO terms 上也保持稳定表现。

## Method

方法可以分成四个关键部分：

1. **结构与序列输入**
   - 使用 `ESM-1b` 提取 residue-level sequence embedding。
   - 使用 amino acid class embedding 补充基础 residue 信息。
   - 用 AlphaFold2 或实验结构构建 protein graph，节点是 residue，边来自 `C-alpha` 距离。
   - 通过 GCN 聚合蛋白结构图特征。

2. **Global-local label graph**
   - 先用 CAM 把 residue-level protein embeddings 映射成 GO term embeddings。
   - `global label graph` 学习训练集层面的 GO term 共现关系，更容易捕捉高频标签关系。
   - `local label graph` 针对每个蛋白动态学习个体化标签关系，用来补充低频 GO terms 与其他标签的联系。

3. **Long-tail optimization ensemble**
   - `GOBoostAll`：在全部 GO labels 上训练。
   - `GOBoostHead`：聚焦高频 head labels。
   - `GOBoostTail`：聚焦中低频 tail labels。
   - 最终对重叠标签的预测取平均，让 All 模型提供整体稳定性，Head/Tail 模型分别修正不同频段的偏差。

4. **Multi-grained focal loss**
   - 将传统 focal loss 的 focus parameter 进一步拆成正负样本粒度和 head-tail 粒度。
   - 对低频 tail labels 分配更高关注权重。
   - 目标是减少负标签和高频标签在 loss 中的支配效应。

最终预测由 graph pooling classifier 和 GO term embedding classifier 两路结果平均得到。

## Key Insights

### 关键结果 1：PDB test set 上全面超过 HEAL

在 PDB test set 上，`GOBoost` 在 MF、BP、CC 三类 GO domain 的所有指标上都取得最好结果：

- `AUPR`: **0.765 / 0.458 / 0.573**
- `Fmax`: **0.787 / 0.659 / 0.745**
- `Smin`: **0.292 / 0.450 / 0.401**

相比强基线 `HEAL`，论文报告 AUPR 分别提升：

- MF: **10.71%**
- BP: **35.91%**
- CC: **22.71%**

BP 的提升尤其明显，因为 BP 标签数量更多、层级更复杂，也更容易体现长尾问题。

### 关键结果 2：AF2 test set 上也能泛化

在更困难的 AF2 test set 上，GOBoost 仍然取得最好结果：

- `AUPR`: MF **0.582** / BP **0.246** / CC **0.318**
- `Fmax`: MF **0.556** / BP **0.497** / CC **0.643**

相比 `HEAL`，AUPR 分别提升 **15.64% / 23.00% / 10.80%**，
Fmax 分别提升 **13.24% / 4.63% / 4.92%**。

这说明 GOBoost 的收益不是只来自 PDB 数据分布，
在低序列相似度、依赖 AlphaFold2 预测结构的测试场景下也有效。

### 关键结果 3：base model 本身已经强，ensemble 进一步补长尾

`GOBoostAll` 不使用 long-tail optimization ensemble，
但仍然超过 `HEAL` 的所有主要指标。
这说明 global-local label graph 和 multi-grained focal loss 已经能缓解一部分 label imbalance。

完整 `GOBoost` 相比 `GOBoostAll` 继续提升，
说明 Head/Tail/All 的 ensemble 策略确实在不同频段标签上提供了互补。

### 关键结果 4：长尾视角比单纯堆结构编码器更关键

`HEAL` 的主要贡献是结构图表征，
而 `GOBoost` 的主要贡献是 label-side modeling。
二者的关系不是简单替代，而是从不同瓶颈切入：

- `HEAL`: 如何从蛋白结构图中学到更好的 protein representation。
- `GOBoost`: 如何让模型不要被高频 GO terms 主导，尤其照顾 specific low-frequency labels。

这也是 GOBoost 在 BP 上提升最大的原因之一。
BP 标签更多、更稀疏，更容易暴露普通 multi-label learning 的缺陷。

### 关键结果 5：specific GO terms 是更值得关注的评价对象

论文按照 GO term 的 information content 把功能标签分成 shallow、normal 和 specific。
结果显示，GOBoost 在 specific labels 上也能保持优势。

这点比整体 Fmax 更有价值：
蛋白功能预测的真正目标不是只给出“这个蛋白有某种代谢相关功能”这样的粗标签，
而是尽可能准确地预测更具体、更可操作的功能注释。

### 我的结论

如果只用一句话评价这篇论文：

> GOBoost 的价值在于把 protein function prediction 的瓶颈从“结构怎么编码”推进到“GO 标签长尾分布怎么学习”。

它对 `HEAL` 这类结构模型是一个很自然的后续补强：
结构图解决 protein-side representation，
GOBoost 则解决 label-side imbalance 与 co-occurrence modeling。

## Limitations & Future Work

- **依赖 GO 标签分布统计**：Head/Tail 划分和 focal 权重都依赖训练集标签频率，跨数据库或跨时间版本迁移时需要重新校准。
- **ensemble 增加训练与推理成本**：完整 GOBoost 需要训练多个 base models，不如单模型轻量。
- **co-occurrence 可能学习到标注偏差**：GO term 共现关系来自现有数据库，可能混入 annotation bias。
- **仍依赖结构质量**：输入结构来自 PDB 或 AlphaFold2，结构预测误差会影响 protein graph。
- **缺少实验验证**：论文主要在 benchmark 上评估功能注释预测，没有 wet-lab 验证新预测的蛋白功能。

后续值得追的方向是：

1. 将 GOBoost 的长尾 label modeling 接入更强的结构编码器或 protein foundation model。
2. 研究动态 GO 数据库更新下 Head/Tail 划分和 loss 权重的稳定性。
3. 把模型预测用于新蛋白功能假设生成，并通过实验或高置信数据库更新做闭环验证。
