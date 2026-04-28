# CodonFM

## Paper Info

- **Title**: Learning the Language of Codon Translation with CodonFM
- **Authors**: Sajad Darabi, Fan Cao, Mohsen Naghipourfar, Sara Rabhi, Ankit Sethia, Kyle Gion, Jasleen Grewal, Jonathan Cohen, William J. Greenleaf, Hani Goodarzi, Laksshman Sundaram
- **Venue**: Preprint, 2025
- **Paper**: [paper.pdf](./paper.pdf)
- **Code**: [NVIDIA-Digital-Bio/CodonFM](https://github.com/NVIDIA-Digital-Bio/CodonFM)
- **Model Weights**: Hugging Face / NVIDIA NGC links are provided in the code repository.

## Summary

`CodonFM` 将 coding sequence（CDS）视为以 codon 为基本 token 的序列语言。论文主要展示了 CodonFM 家族中的 `EnCodon` encoder 系列：模型通过大规模 masked codon prediction 学习 codon choice 的上下文规律，并将所得表征用于 missense variant、synonymous variant、mRNA translation efficiency 和 protein expression 等任务。

本文的主要问题是：同义密码子虽然编码相同氨基酸，但其选择并非完全等价。不同 codon 可能通过翻译速度、mRNA 稳定性、RNA 结构或细胞环境相关因素影响表达和功能。因此，若模型能够从自然 CDS 中学习这种上下文依赖关系，就有可能为变异效应预测和 mRNA 设计提供新的序列表征。

## Problem Setting

遗传密码具有简并性，18 种氨基酸可由多个 synonymous codons 编码。早期观点往往将同义密码子视为功能上近似等价的替换，但已有研究表明，codon usage bias 与 tRNA abundance、translation elongation rate、RNA secondary structure、mRNA decay、protein folding 以及疾病相关突变均存在关联。

传统 codon optimization 通常依据 host codon bias、`CAI` 或少量人工规则选择密码子。这类方法实现简单，解释性较强，但难以同时考虑相邻 codon、GC content、RNA structure、物种背景和表达需求等因素。CodonFM 的基本思路是直接从大规模自然 CDS 中学习 codon usage 的统计规律，使模型在不显式写入全部生物物理规则的情况下获得上下文敏感的 codon 表征。

## Method Overview

### Codon-level tokenization

EnCodon 不以单个 nucleotide 为 token，而是按三联体 codon 切分 CDS。典型输入形式如下：

```text
<CLS> ATG GCG <MASK> ... TGA <SEP>
```

这种建模方式使 token 与翻译单位一致。与 nucleotide-level 模型相比，codon-level tokenization 更便于表达同一氨基酸下不同 synonymous codons 的选择差异，也便于在 masked language modeling 中直接预测完整 codon。

### Pretraining data

预训练数据来自 NCBI RefSeq / Genomes，包含超过 **130 million** 条 CDS，覆盖超过 **22,000 species**。训练集包括 bacteria、archaea、fungi、plants、protozoa、primates、non-primate mammals、invertebrates 和 non-mammal vertebrates 等类群。作者出于 biosafety 考虑移除了 human-affecting pathogen sequences。

Fig. 1B 显示，bacteria 在训练序列中占比约为 59.9%。因此，该语料并非以人类 CDS 为中心，而是覆盖了较广的系统发育范围；同时，训练分布存在明显不均衡，bacterial CDS 对预训练信号的贡献较大。

### Training objective

EnCodon 采用 Transformer encoder，并使用 masked codon prediction 作为预训练目标。给定一条 ORF 序列及其上下文，模型预测被 mask 的 codon：

```text
p(masked codon | surrounding codon context)
```

论文训练了四个版本：`EnCodon 80M`、`EnCodon 600M`、`EnCodon 1B` 和 `EnCodon 1B-CDWT`。其中 `CDWT` 表示 codon-frequency weighted masking strategy，该策略提高低频或信息量较高 codon 在 mask 过程中的权重，以减少模型主要依赖高频 codon 分布的风险。

### Zero-shot variant scoring

在变异效应预测任务中，论文主要比较 reference codon 与 alternate codon 在相同上下文中的 likelihood。可将其理解为如下分数：

```text
score = log p(reference codon | context) - log p(alternate codon | context)
```

若 alternate codon 在当前上下文下概率显著降低，则该变异可能偏离自然 CDS 中常见的 codon usage 规律。不同 benchmark 使用该分数区分 case/control、pathogenic/benign 或 hotspot/non-hotspot variants。

## Metrics

论文中涉及的主要指标如下。Validation loss 或 MLM loss 越低，表示 masked codon prediction 越准确。Normalized synonymous codon confusion score 越低，表示模型越能区分同一氨基酸对应的不同 synonymous codons。KNN purity 越高，表示 embedding 空间中的邻近序列更可能属于同一 taxonomy division。AUROC 用于二分类任务，0.5 接近随机水平，数值越高区分能力越强。Mann-Whitney U test 的 `-log10(p)` 越高，表示两组样本的分数分布差异越显著。`R^2` 和 Spearman correlation 分别衡量回归解释度和排序相关性。

## Main Figures

Fig. 1 介绍数据、模型结构和预训练结果；Fig. 2 分析模型是否形成具有生物意义的 codon 表征；Fig. 3 和 Fig. 4 分别评估 missense variants 与 synonymous variants；Fig. 5 将 EnCodon embedding 用于 translation efficiency 和 protein expression 预测。

### Fig. 1: dataset, architecture, and pretraining

![Fig. 1: data, model architecture, and pretraining](./figures/fig1.png)

#### Fig. 1A

作者从 NCBI RefSeq / Genomes 构建 CDS 训练语料，规模超过 130M sequences，覆盖 22,000 余个物种。该规模为模型学习跨物种 codon usage 差异提供了数据基础。

#### Fig. 1B

饼图给出训练序列的 taxonomy composition。bacteria 占比最高，约为 59.9%；non-mammal vertebrate、invertebrate、primates、plants 和 fungi 分别占一定比例。该分布说明模型训练覆盖多个类群，但样本数量并不均衡。

#### Fig. 1C

横轴为 CDS 的 codon 数量，纵轴为序列数量。红色虚线对应模型上下文长度 **2,046 codons**。大多数 CDS 长度低于 1,000 codons，因此多数 ORF 可以完整放入模型上下文中。较长的上下文窗口有助于模型利用 gene-level 的 codon pattern，而不仅限于局部片段。

#### Fig. 1D

每条 ORF 以 `<CLS>` 开始，以 `<SEP>` 结束，中间为 codon tokens。模型主体为 Transformer encoder，包含 RoPE + self-attention 和 position-wise feed-forward layers。预训练时，模型根据上下文预测被 mask 的 codon。

#### Fig. 1E

不同规模模型的 validation loss 随训练迭代下降。`EnCodon 600M`、`EnCodon 1B` 和 `EnCodon 1B-CDWT` 均明显低于 `EnCodon 80M`，说明扩大模型规模能够提升 codon-level masked prediction 的效果。

### Fig. 2: codon representation and taxonomy structure

![Fig. 2: codon grammar and phylogenetic structure](./figures/fig2.png)

Fig. 2 讨论 EnCodon 表征是否超越简单的 nucleotide composition 或 amino acid composition。作者从 synonymous codon confusion、UMAP embedding 和 principal components 三个角度进行分析。

#### Fig. 2A

横轴为 amino acid，纵轴为模型版本，颜色表示 normalized confusion score。分数越低，说明模型越不容易将同一氨基酸的不同 synonymous codons 混淆。

从 `80M` 到 `1B`，confusion score 整体下降。这表明较大模型不仅能识别 codon 与 amino acid 的映射关系，还能进一步利用上下文区分不同 synonymous codons 的使用偏好。

#### Fig. 2B

作者将 sequence embedding 经 PCA 和 UMAP 降维后可视化，并按 taxonomy division 着色。较大模型，尤其是 `1B-CDWT`，在 embedding 空间中形成较清晰的类群结构。这与 codon usage bias 具有物种和类群差异的事实一致。

#### Fig. 2C

左图展示不同 taxonomy division 上的 normalized MLM loss。总体来看，模型规模增大后，多数类群上的 loss 降低。中图展示 KNN purity，`1B-CDWT` 在不同邻居数下均保持较高 purity，说明 codon-frequency weighted masking 有助于形成更稳定的 taxonomy organization。右图分析 top principal components 与 amino acid hydrophobicity 的相关性。小模型的一些主成分更容易与氨基酸疏水性相关，而大模型相关性相对降低，提示较大模型可能编码了更多 codon usage 和上下文信息，而不主要依赖简单氨基酸属性。

### Fig. 3: missense variant effect prediction

![Fig. 3: missense variant tasks](./figures/fig3.png)

Missense mutation 会改变氨基酸，因此 protein language models 在这类任务中通常具有直接优势。EnCodon 在该任务上的表现可用于考察 CDS-level codon model 是否能间接捕捉 protein constraint。

#### Fig. 3A-B

Fig. 3A 和 Fig. 3B 分别评估 DDD 与 ASD de novo missense variants。指标为 Mann-Whitney U test 的 `-log10(p)`，用于衡量 case 与 control variants 的分数分布差异。

在这两个任务中，EnCodon 系列表现出较明显的规模效应。`EnCodon 1B-CDWT` 和 `EnCodon 1B` 排名靠前，`600M` 和 `80M` 次之。与多个 RNA 或 mRNA sequence model baseline 相比，EnCodon 的区分能力更强。在 DDD 数据集中，EnCodon 的 `-log10(p)` 大致位于 30 到 36 区间；在 ASD 数据集中，该指标约为 6 到 8，说明不同数据集的任务难度和统计功效存在差异。

#### Fig. 3C-D

Fig. 3C 和 Fig. 3D 分别使用 AUROC 评估 cancer hotspot mutations 和 ClinVar missense variants。在 cancer hotspot task 中，ESM-2 (3B) 略高于 EnCodon 大模型；在 ClinVar missense task 中，ESM-2 仍为最强基线，EnCodon 大模型约在 0.85 左右，优于多数 RNA/mRNA baselines。

该结果说明，在直接涉及氨基酸替换和蛋白功能约束的任务中，protein language models 仍然具有优势；与此同时，仅以 CDS codon sequence 为输入的 EnCodon 能够接近强蛋白模型，并明显优于多数核酸序列模型。

#### Fig. 3E-G

Fig. 3E 展示 fine-tuning 设置。作者使用 gnomAD missense variants 对 `EnCodon 1B` 进行 fine-tuning，得到 `EnCodon 1B-FT`，随后在 ASD 和 DDD 数据集上评估。

Fine-tuned EnCodon 相比 zero-shot `EnCodon 1B` 有进一步提升。在 ASD 数据集上，`EnCodon 1B-FT` 高于 AlphaMissense；在 DDD 数据集上，AlphaMissense 略高，但 `EnCodon 1B-FT` 与其接近。这表明 EnCodon 可作为 supervised variant effect prediction 的预训练初始化模型。

### Fig. 4: synonymous variant effect prediction

![Fig. 4: synonymous variant task](./figures/fig4.png)

Synonymous mutation 不改变氨基酸序列，因此 protein language models 难以直接建模这类变异。若模型能够区分 pathogenic 与 benign synonymous variants，则说明其利用了 codon-level 或 RNA-level 的序列信息。

#### Fig. 4A

作者 mask 变异位置的 codon，并比较 reference codon 与 mutation codon 在相同上下文下的 likelihood ratio，得到 pathogenicity score。该流程不需要对 ClinVar synonymous variants 进行任务特异的监督训练。

#### Fig. 4B

Fig. 4B 使用 ClinVar 中 pathogenic 与 benign synonymous variants 进行评估。为减少混杂因素，作者进行了 50 次 stratified subsampling，并匹配 reference/alternate codon、variant 在 gene 中的位置、gene-level pLI 和 local mutation rate。

在上述匹配条件下，`EnCodon 1B-CDWT` 的 median performance 最高，`EnCodon 1B` 和 `EnCodon 600M` 也明显优于 `EnCodon 80M`。多数 RNA/mRNA baselines 的表现低于 EnCodon 大模型。该结果表明，CodonFM 的优势不仅体现在 CDS 中与蛋白功能相关的间接信号，也体现在对不改变氨基酸序列的 codon-level variant effects 的建模能力上。

### Fig. 5: translation efficiency and protein expression

![Fig. 5: translation efficiency and protein expression](./figures/fig5.png)

Fig. 5 将 EnCodon embedding 用于 mRNA design 相关任务。作者提取预训练模型 embedding，并训练 random forest regressor 预测实验读数，而不是直接生成新的 mRNA 序列。

#### Fig. 5A

Fig. 5A 预测 mammalian cell 中的 translation efficiency，指标为 10-fold cross-validation 的 mean `R^2`。`EnCodon 1B` 表现最高，`R^2` 约为 0.52；`EnCodon 600M`、`mRNA-FM` 和 `EnCodon 1B-CDWT` 接近，约为 0.48 到 0.49；`EnCodon 80M` 和 `CodonBERT` 较低。该结果说明 EnCodon embedding 能够提供与翻译效率相关的序列特征。

#### Fig. 5B

Fig. 5B 预测 mRFP protein expression，指标为 predicted expression 与 observed expression 的 Spearman correlation。`EnCodon 1B` 最高，约为 0.73；`EnCodon 600M` 接近，约为 0.71；`EnCodon 80M` 和 `EnCodon 1B-CDWT` 约为 0.65；`CodonBERT` 与 `mRNA-FM` 较低。

需要注意的是，`1B-CDWT` 在 synonymous variant task 中表现较好，但在 expression prediction 中不一定最优。论文给出的解释是，CDWT 表征较少受 GC content 等简单 sequence composition 特征影响；而在部分表达数据中，这类简单特征本身具有一定预测能力。因此，CDWT 更适合强调 codon-level specificity，但并不保证在所有 expression benchmarks 上获得最高结果。

## Main Observations

首先，codon choice 具有可学习的上下文规律。Fig. 2 中的 synonymous codon confusion 结果显示，模型规模增大后，模型更能区分同一氨基酸对应的不同 synonymous codons。这说明同义密码子的使用偏好并非完全由氨基酸身份决定。

其次，模型容量对 codon-level representation learning 有明显影响。从 validation loss、confusion score、KNN purity 到 variant prediction tasks，`80M -> 600M -> 1B` 大体呈现一致的性能提升趋势。

再次，`1B-CDWT` 在强调 codon-level specificity 的任务中表现较好，尤其是 taxonomy organization 和 synonymous variant prediction。但在 translation efficiency 或 expression prediction 中，`1B-CDWT` 不一定优于 random masking 的 `1B`，这与不同任务对 GC content 等低阶特征的依赖程度有关。

此外，missense variant 任务表明 CDS 表征中包含与 protein constraint 相关的信息。EnCodon 并不直接输入 amino acid sequence，但在 DDD、ASD、ClinVar missense 和 cancer hotspot tasks 中均取得较强结果。

最后，synonymous variant prediction 是 CodonFM 区别于 protein language models 的重要应用场景。由于 synonymous variants 不改变蛋白序列，codon-level 模型能够提供 protein-level 模型难以直接获得的信息。

## Relation to Related Models

### LinearDesign

`LinearDesign` 显式优化 `MFE + CAI`，重点在于通过搜索算法和 RNA folding objective 生成优化后的 mRNA CDS。`CodonFM` 不直接进行 folding 或全局组合搜索，而是从自然 CDS 中学习隐式 codon context。二者可形成互补：LinearDesign 提供明确的结构和 codon bias 目标，CodonFM 提供由大规模进化序列学习得到的上下文评分。

### RNA foundation models

许多 RNA foundation models 以 nucleotide 为 token，适合泛 RNA structure 或 function 表征。CodonFM 的区别在于将 CDS 对齐到 codon token，因此更适合 translation-aware tasks，尤其是 synonymous codon choice 相关问题。

### Protein language models

Protein language models 直接建模 amino acid sequence，因此在 missense variant、protein constraint 和 structure-related tasks 中具有优势。但它们无法区分编码同一蛋白的不同 synonymous CDS。CodonFM 关注的是位于 nucleotide sequence 与 amino acid sequence 之间的 codon-level regulatory space。

## Limitations

- 论文结果主要来自 benchmark、embedding analysis 和回归预测，仍需更多 wet-lab perturbation 验证。
- 高质量 synonymous variant 标注数据较少，相关统计结果需要结合数据规模和匹配策略谨慎解释。
- 训练集覆盖面较广，但类群分布不均衡，bacterial sequences 占比较高。
- 当前模型没有显式纳入 cell-type-specific tRNA abundance、RNA modification、ribosome profiling、RBP binding 或 tissue-specific translation context。
- 模型没有显式 RNA structure objective，因而不能替代直接优化 MFE 或 folding path 的方法。
- 论文主要展示 EnCodon encoder 系列，并未提供完整的 de novo mRNA generation pipeline。
- 在直接涉及氨基酸替换和蛋白结构约束的任务中，ESM-2 和 AlphaMissense 等 protein-level models 仍是重要基线。

## Reading Notes

这篇论文的主要贡献在于将 synonymous codon choice 表述为可通过大规模预训练学习的序列建模问题。相比传统 codon optimization，CodonFM 更强调上下文相关的 codon usage 表征；相比 protein language models，它能够处理不改变氨基酸序列的 synonymous variants。

若将 EnCodon 用于 mRNA therapeutic design，更合理的方式是将其作为候选序列的 scoring 或 representation component，而不是单独依赖它完成全部设计流程。实际应用中可将 RNA folding model、`CAI` / `tAI`、host-specific codon usage、实验反馈模型与 CodonFM score 组合起来，形成多目标评价框架。

## Assets

- 主文 PDF: [paper.pdf](./paper.pdf)
- 主图目录: [figures](./figures/)
- 当前 README 使用的主图为 [fig1.png](./figures/fig1.png) 到 [fig5.png](./figures/fig5.png)。
