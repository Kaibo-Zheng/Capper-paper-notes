# mRNABERT

## Paper Info

- **Title**: mRNABERT: advancing mRNA sequence design with a universal language model and comprehensive dataset
- **Authors**: Ying Xiong, Aowen Wang, Yu Kang, Chao Shen, Chang-Yu Hsieh, Tingjun Hou
- **Venue**: Nature Communications (2025)
- **DOI**: [10.1038/s41467-025-65340-8](https://doi.org/10.1038/s41467-025-65340-8)
- **Paper**: [mRNA-BERT.pdf](./mRNA-BERT.pdf)

## Motivation

现有不少 RNA/mRNA 模型主要针对单一区域（如 UTR 或 CDS），难以直接支持全长 mRNA 的统一设计。本文希望构建一个覆盖完整 mRNA 序列的通用语言模型，用于提升设计效果与下游任务泛化能力。

## Method

- 构建了大规模 mRNA 数据集，作为统一预训练语料。
- 提出双 tokenization 策略，兼顾不同粒度的序列表示。
- 通过跨模态对比学习引入蛋白序列语义，增强 mRNA 表征能力。
- 在 5'UTR/CDS 设计、RBP 位点预测、全长 mRNA 属性预测等任务上进行系统评测。

## Key Insights

- 同时建模 UTR 与 CDS 的全长结构，对实际 mRNA 设计价值更高。
- 引入蛋白语义后，多个 mRNA 相关任务性能有明显提升。
- 在多任务基准上取得较强结果，体现出较好的迁移与泛化能力。

## Limitations & Future Work

- 训练与评测仍主要依赖公开数据，体内/体外实验验证空间较大。
- 长序列建模能力和可解释性还可继续加强。
- 后续可结合结构先验、多组学信息与实验闭环进一步优化设计质量。
