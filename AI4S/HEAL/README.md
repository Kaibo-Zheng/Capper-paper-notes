# HEAL

## Paper Info

- **Title**: Hierarchical graph transformer with contrastive learning for protein function prediction
- **Authors**: Zhonghui Gu, Xiao Luo, Jiaxiao Chen, Minghua Deng, Luhua Lai
- **Venue**: Bioinformatics 2023, 39(7), btad410
- **Paper**: [paper.pdf](./paper.pdf)
- **DOI**: [10.1093/bioinformatics/btad410](https://doi.org/10.1093/bioinformatics/btad410)
- **Code**: [ZhonghuiGu/HEAL](https://github.com/ZhonghuiGu/HEAL)

## Abstract

`HEAL` 是一个面向蛋白功能预测的结构生物信息学模型。
它把蛋白序列特征、蛋白语言模型特征和 3D 结构图结合起来，
用 hierarchical graph Transformer 捕捉局部 residue message passing 难以覆盖的长距离结构语义，
再用 contrastive learning 做图表示正则化。

一句话总结：
`HEAL` 的核心是把蛋白结构图里的功能 motif 从普通 graph pooling 中显式拎出来，
让模型更好地从结构与序列共同推断 Gene Ontology 功能标签。

## Motivation

蛋白功能注释的实验成本高、通量低，而新测序得到的蛋白数量增长很快。
传统的序列比对方法依赖相似序列和已有数据库，遇到低同源、缺少注释的新蛋白时会受限。
结构信息通常比序列更保守，也更直接关联功能，因此基于结构图的深度模型很有价值。

但已有 GNN 类方法有两个问题：

1. **长距离结构相关性难捕捉**：浅层 GNN 只能聚合局部邻域，深层又容易 oversmoothing。
2. **关键残基容易被平均掉**：mean/max pooling 把所有 residue 近似等权处理，而真实功能往往由少数活性位点或结合区域决定。

`HEAL` 想解决的就是这两个结构建模问题。

## Method

方法可以拆成四个部分：

1. **蛋白图输入**
   - 每个 residue 是一个节点。
   - 节点特征来自 one-hot amino acid encoding 和 `ESM-1b` residue embedding。
   - 如果两个 residue 的 `C-alpha` 原子距离小于 `10 A`，就在图中连边。

2. **Message Passing GCN**
   - 先用 GCN 在蛋白图上聚合局部结构信息。
   - 这一层负责捕捉短距离几何邻域中的 residue interaction pattern。

3. **Hierarchical Graph Transformer**
   - 引入一组可学习的 `super-nodes`。
   - super-nodes 作为 query，与 residue-level key/value 交互，聚合出带结构语义的 motif-level 表示。
   - 再用 attention pooling 把多个 super-node 表示汇总为 graph-level protein representation。

4. **Contrastive Learning 正则化**
   - 对 node embedding 做平滑扰动，形成同一个蛋白图的不同 view。
   - 用 `InfoNCE loss` 拉近同一蛋白不同 view 的 graph representation。
   - 最终训练目标是 `BCE supervised loss + contrastive regularization loss`。

## Key Insights

### 关键结果 1：HEAL 在 PDBch 上超过 DeepFRI

在 `PDBch` test set 上，`HEAL` 在三个 GO domain 上都优于 DeepFRI。
论文报告的主要结果为：

- `AUPR`: MF **0.691** / BP **0.337** / CC **0.467**
- `Fmax`: MF **0.747** / BP **0.595** / CC **0.687**
- `Smin`: MF **0.342** / BP **0.509** / CC **0.458**

相比只用 PDBch 训练的 `HEAL-PDB`，加入 AlphaFold2 预测结构构成的 `AFch` 数据后，
模型整体明显增强，说明高质量预测结构可以作为有效的数据扩充来源。

### 关键结果 2：Hierarchical Graph Transformer 是主要增益来源

消融实验里，把 HGT 换成传统 max pooling 后，性能下降很明显：

- `HEAL`: AUPR = **0.691 / 0.337 / 0.467**
- `HEAL w/o MP`: AUPR = **0.588 / 0.252 / 0.378**

这说明关键点不是“用了结构图”本身，
而是 HGT 让模型能以 motif-like super-node 的方式聚合结构语义，
避免所有 residue 被粗暴地等权汇总。

### 关键结果 3：ESM-1b embedding 非常关键

去掉 ESM-1b 后，AUPR 掉到 **0.284 / 0.130 / 0.222**。
这个下降幅度说明，结构图并不能完全替代蛋白语言模型学到的进化与序列模式。

更合理的理解是：
`HEAL` 的有效性来自 `sequence language embedding + 3D structure graph` 的互补，
而不是单纯押注结构信息。

### 关键结果 4：对低同源和高 specificity GO terms 更有价值

论文按照 sequence identity 阈值和 GO term information content 做了分析。
结果显示，`HEAL` 在低同源场景下下降更平缓，
在高 specificity GO terms 上也有更强表现。

对 `IC > 10` 的高特异功能标签，平均 AUPR 为：

- `HEAL`: **0.321**
- `HEAL-PDB`: **0.214**
- `DeepFRI`: **0.204**
- `DeepGO`: **0.137**

这点很重要，因为真正难的功能预测往往不是宽泛标签，
而是更具体、更稀疏的功能注释。

### 关键结果 5：Grad-CAM 能定位功能残基

论文用 grad-CAM 把预测贡献投影回蛋白结构，
在 DNA-binding、nucleoside triphosphate metabolic process 等例子中，
高贡献 residue 与实验确认的 binding sites 有较好重合。

这说明 `HEAL` 不只是输出 GO term 概率，
还可以提供一定程度的结构可解释性。

### 我的结论

如果只用一句话评价这篇论文：

> HEAL 的贡献在于把蛋白功能预测从“结构图全局池化”推进到“用可学习 super-node 捕捉功能 motif 的结构语义建模”。

它是一个很适合作为后续 protein function prediction 方法基线的模型。
后来的 `GOBoost` 也直接把 `HEAL` 作为强基线，
说明这篇论文在结构式蛋白功能预测路线里有承上启下的作用。

## Limitations & Future Work

- **仍依赖结构输入**：需要实验结构或 AlphaFold2 预测结构，比纯序列模型多一个结构获取步骤。
- **结构预测误差会传导**：AF2 结构质量、低置信区域和多构象问题都会影响图输入。
- **长尾 GO label 问题没有被系统解决**：HEAL 提到低频标签表现，但核心方法主要解决结构表征，不是专门处理 label imbalance。
- **实验验证有限**：论文验证的是功能注释预测和 binding-site 对齐，没有进一步 wet-lab 验证模型新预测的功能。
- **GO 标签本身有数据偏差**：模型学习到的 co-occurrence 与 annotation pattern 仍受数据库标注完整性影响。

后续值得追的方向是：

1. 把结构建模和长尾标签建模结合起来，例如与 `GOBoost` 的 label-side 策略融合。
2. 用更新的 protein language model 或 single-sequence structure model 替换 ESM-1b/AF2 管线。
3. 在真实新蛋白功能发现任务中验证模型预测，而不是只在历史注释 benchmark 上比较。
