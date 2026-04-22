# mRNABERT

## Paper Info

- **Title**: mRNABERT: advancing mRNA sequence design with a universal language model and comprehensive dataset
- **Authors**: Ying Xiong, Aowen Wang, Yu Kang, Chao Shen, Chang-Yu Hsieh, Tingjun Hou
- **Venue**: Nature Communications (2025)
- **DOI**: [10.1038/s41467-025-65340-8](https://doi.org/10.1038/s41467-025-65340-8)
- **Paper**: [paper.pdf](./paper.pdf)

## Motivation

这篇论文要解决的核心问题是：
现有 RNA/mRNA 模型通常只擅长局部区域建模（例如只看 5'UTR、只看 CDS 或只看 3'UTR），
但真实的 mRNA 设计任务需要对完整序列进行统一建模与联合优化。

一句话总结：
mRNABERT 试图把“全长 mRNA”作为统一对象学习，并通过与蛋白语义对齐，提升对真实设计场景的支持能力。

## Method

作者先构建了约 1800 万条高质量、非冗余的 mRNA 预训练语料，随后做了三层关键设计：

1. **双重分词（Dual Tokenization）**
   - UTR 按 nucleotide 切分。
   - CDS 按 codon 切分。
   - 目标是在保留 UTR 细粒度信息的同时，显式编码 CDS 翻译语义。

2. **长序列建模架构**
   - 主体为 12 层、hidden size 768 的 BERT 编码器。
   - 使用 ALiBi 替代传统位置编码。
   - 引入 Flash Attention，提高长序列训练效率。

3. **跨模态对比学习**
   - 在 MLM 预训练后，使用约 50 万条 CDS 及其翻译蛋白序列。
   - 蛋白侧使用冻结的 ProtT5-XL 表征。
   - 将核酸和蛋白 embedding 投影到共享空间进行对比学习。

### 图 1：整体框架与应用全景

![Fig. 1](./fig1.png)

- 数据侧：多源数据清洗后形成约 1800 万条样本。
- 编码侧：UTR/CDS 采用不同粒度 token。
- 训练侧：先 MLM，再做核酸-蛋白跨模态对齐。
- 任务侧：覆盖 5'UTR、CDS、3'UTR、蛋白属性与全长 mRNA 属性预测。

## Key Insights

### 图 2：模型学到了什么（表征可视化）

![Fig. 2](./fig2.png)

- 对比学习显著改善语义结构：
  - ARI：**0.166 -> 0.498**
  - FMI：**0.325 -> 0.596**
- 表征不仅能区分不同 mRNA 区域，还可分离 lncRNA 与 mRNA。
- 同源序列在 embedding 空间按物种聚类，说明模型保留了跨物种进化信息。

### 图 3：5'UTR 任务（翻译起始效率）

![Fig. 3](./fig3.png)

- 在 8 个 5'UTR MPRA 数据集上评估 MRL（Spearman）。
- 在 U1/U2 两个大规模随机 UTR 数据集上达到 **0.962 / 0.924**。
- 总体与专门 5'UTR 模型 UTR-LM 基本持平，体现了通用模型的竞争力。

### 图 4：3'UTR 任务（转录后调控与修饰）

![Fig. 4](./fig4.png)

- RBP 结合位点预测平均表现：
  - **ACC 0.786 / F1 0.751 / MCC 0.501**
- 与 3UTRBERT 接近（ACC 0.785 / F1 0.751 / MCC 0.503），且在 22 个 RBP 中有 13 个任务最优。
- m6A 预测在 9 个细胞系中整体稳定排名第二，说明通用模型在专门任务上也有强可迁移性。

### 图 5：跨模态迁移到蛋白属性任务

![Fig. 5](./fig5.png)

- 对比学习后，蛋白熔点预测 R² 由 **0.60 -> 0.77**。
- 蛋白溶解度预测达到 **R² = 0.63**。
- 7 个物种转录本丰度预测中有 5 个优于对比基线（文中以 Homo sapiens 为例：0.38 vs 0.35）。

核心含义：
模型不是替代蛋白模型，而是通过核酸-蛋白语义对齐，让 mRNA 表征具备更强跨任务迁移能力。

### 图 6：全长 mRNA 综合属性（最关键）

![Fig. 6](./fig6.png)

- 在 PERSIST-seq 全长 mRNA 评估中，覆盖 6 个关键任务（稳定性与翻译相关指标）。
- mRNABERT 在这类全长任务上整体领先区域特化模型。
- 在超长外推设置（3066 tokens）下，
  - Human：R² = **0.669**，Spearman R = **0.814**
  - Mouse：R² = **0.649**，Spearman R = **0.812**

### 其他关键结果

- 在 6 个 CDS 相关任务上，整体表现稳定且多数任务最优或并列最优。
- 论文也明确承认并非所有局部任务都绝对第一，这反而增强了全长场景结论的可信度。

### 我的结论

如果只用一句话评价：

> mRNABERT 的核心贡献不是“模型更大”，而是证明了全长 mRNA 统一建模在方法上可行、在结果上有稳定收益。

## Limitations & Future Work

论文讨论的限制点比较清晰：

- **结构信息未显式建模**：主要仍基于序列学习，二级结构与修饰信息尚可进一步融合。
- **超长序列成本仍高**：ALiBi 有助外推，但未从根本上解决长序列计算开销。
- **数据与标注整合空间大**：更复杂的转录本边界、功能注释与实验标签可进一步提升上限。
- **离闭环设计仍有距离**：当前强在预测，距离“自动生成并实验验证最优 mRNA”的端到端闭环仍需工程推进。
