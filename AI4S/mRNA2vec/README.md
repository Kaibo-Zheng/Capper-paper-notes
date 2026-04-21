# mRNA2vec

## Paper Info

- **Title**: mRNA2vec: mRNA Embedding with Language Model in the 5'UTR-CDS for mRNA Design
- **Authors**: Honggen Zhang, Xiangrui Gao, June Zhang, Lipeng Lai
- **Venue**: AAAI 2025
- **Paper**: [paper.pdf](./paper.pdf)
- **Code**: [honggen-zhang/mRNA2vec](https://github.com/honggen-zhang/mRNA2vec)

## Motivation

这篇论文关注的是 mRNA 表征学习，而不是直接生成新序列。
现有 RNA/mRNA 模型常常把 `5'UTR`、`CDS` 或其他区域分开建模，
但真实翻译过程里，`5'UTR` 尾部和 `CDS` 起始区域之间存在强耦合，
只看单一区域容易丢掉影响翻译效率和表达量的上下文。

一句话总结：
`mRNA2vec` 想把 `5'UTR + CDS` 作为一个联合序列来学习 embedding，
并用 mRNA 的物理结构知识增强语言模型预训练。

## Method

作者的方法可以拆成四个部分：

1. **联合输入表示**
   - 将 `5'UTR` 和 `CDS` 拼接作为输入，而不是分别建模。
   - 使用 64 个 codon token 表示三联体碱基。
   - 预训练数据来自 human、rat、mouse、chicken、zebrafish，处理后约 **510k** 条序列，平均长度 **459 bp**。

2. **data2vec 风格的上下文预训练**
   - student model 接收 masked sequence。
   - teacher model 接收 unmasked sequence。
   - 目标不是预测单个 masked token，而是让 student 对齐 teacher 的上下文表示。

3. **位置相关 hard masking**
   - 对 `5'UTR` 尾部和 `CDS` 起始附近区域设置更高 mask 概率。
   - 论文中重要区域大致设为第 15 到第 45 个 token。
   - 这样做的动机是翻译起始附近区域对下游功能更敏感。

4. **结构相关辅助任务**
   - `MFE regression`：让表示显式吸收最小自由能信息。
   - `Secondary Structure classification`：把 dot-bracket 结构按三联体切分成 **27 类** token-level 分类任务。
   - 总损失为 `data2vec loss + MFE loss + SS loss`。

模型规模并不大：主干是 4 层、4 heads、256 维 token embedding，
总参数约 10M，其中可训练参数约 3M。

## Key Insights

### 关键结果 1：上下文目标比单纯 masked token prediction 更适合 mRNA embedding

论文比较了 data2vec、T5 encoder 和未预训练模型。
结果显示，T5 这类单 token 预测目标在部分任务上有提升，
但 data2vec 在多个 epoch 后更稳定，尤其在 5'UTR 相关任务上更适合学习完整序列表征。

这点很重要，因为 mRNA 下游任务通常读的是整段序列的功能，
而不是恢复某个被 mask 的碱基。

### 关键结果 2：MFE 和二级结构辅助任务确实带来增益

在同一个 data2vec 主干上加入结构信息后，下游 Spearman 表现整体提升。

代表性结果包括：

- `Muscle-TE`: **0.550 -> 0.573**
- `Muscle-EL`: **0.619 -> 0.662**
- `mRFP-Expression`: **0.508 -> 0.552**

这说明结构信息不是额外噪声。
只要预训练任务设计得合适，MFE 和 secondary structure 可以帮助模型学到更贴近翻译功能的表示。

### 关键结果 3：在 5'UTR 的 TE/EL 任务上超过现有方法

在 5'UTR 下游任务中，`mRNA2vec` 在三个细胞/组织数据集上取得了很强结果：

- `HEK-TE / PC3-TE / Muscle-TE`: **0.68 / 0.71 / 0.75**
- `HEK-EL / PC3-EL / Muscle-EL`: **0.69 / 0.70 / 0.80**

相比同规模 `UTR-LM`，论文报告在 TE 任务上分别提升约 **13% / 12% / 14%**，
在 EL 任务上分别提升约 **6% / 27% / 31%**。

这里的核心不是单个 benchmark 的刷新，
而是说明 `5'UTR-CDS` 联合上下文对翻译相关任务有实际价值。

### 关键结果 4：CDS 任务上也有可迁移性

论文还在 `mRNA stability` 和 `mRFP protein production` 两个 CDS 任务上测试。

- 在 mRNA stability 上，相比 `CodonBERT`，结果从约 **0.34** 提升到 **0.53**。
- 在 protein production 上，表现与已有 CDS 专门模型接近。
- 更有意思的是，mRFP 数据来自 `E. coli`，而预训练并没有使用 `E. coli` mRNA 序列。

这说明 `mRNA2vec` 学到的并不完全是物种内记忆，
而是具有一定跨场景迁移能力的 mRNA 表征。

### 关键结果 5：工程细节对下游效果影响很大

论文做了几个很实用的分析：

- 下游任务不一定使用完整 5'UTR 最好，截取靠近 CDS 的子序列反而更强。
- 倒数第二层 hidden state 比最后一层更适合作 embedding。
- 简单 linear head 已经能超过部分基线，但 CNN / two-layer regressor 还能进一步提升。

这说明 mRNA 表征学习不是“预训练好就结束”，
下游读取哪一层、读哪一段、用什么 regressor 都会明显影响结论。

### 我的结论

如果只用一句话评价这篇论文：

> mRNA2vec 的价值在于把 mRNA embedding 从单一区域建模推进到 `5'UTR-CDS` 联合表征，并证明结构信息可以通过合适的预训练目标稳定进入语言模型。

它更像是 mRNA 设计系统里的基础表征层，
而不是一个完整的端到端生成模型。

## Limitations & Future Work

- **还不是生成式设计模型**：本文主要证明 embedding 对预测任务有效，距离自动生成优化 mRNA 还有一步。
- **没有覆盖 full-length mRNA**：模型考虑 `5'UTR + CDS`，但没有纳入 `3'UTR`、poly(A)、cap 等完整构件。
- **下游效果依赖子序列选择**：靠近 CDS 的区域很关键，但这种截取策略仍带有任务调参色彩。
- **实验验证仍是离线预测为主**：没有像 LinearDesign 或 GEMORNA 那样进入 wet-lab 序列验证。
- **结构信息仍较粗**：MFE 和 dot-bracket SS 有用，但还不能完全表达真实细胞内 RNA 结构与修饰状态。

后续值得追的方向是：

1. 将 `5'UTR / CDS / 3'UTR` 放进同一个 full-length mRNA 表征框架。
2. 把 embedding 接入生成器或优化器，形成真正的 mRNA design loop。
3. 用实验反馈校准结构辅助任务，而不是只依赖 RNAfold 这类离线估计。
