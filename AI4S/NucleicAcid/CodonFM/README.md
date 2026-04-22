# CodonFM

## Paper Info

- **Title**: Learning the Language of Codon Translation with CodonFM
- **Authors**: Sajad Darabi, Fan Cao, Mohsen Naghipourfar, Sara Rabhi, Ankit Sethia, Kyle Gion, Jasleen Grewal, Jonathan Cohen, William J. Greenleaf, Hani Goodarzi, Laksshman Sundaram
- **Venue**: Preprint, 2025
- **Paper**: [paper.pdf](./paper.pdf)
- **Code**: [NVIDIA-Digital-Bio/CodonFM](https://github.com/NVIDIA-Digital-Bio/CodonFM)
- **Model Weights**: Hugging Face / NVIDIA NGC links are provided in the code repository.

## Motivation

这篇论文关注的是 **codon-level foundation model**。
同一个氨基酸通常可以由多个同义密码子编码，
但这些同义 codon 并不只是“等价替换”：
它们会影响翻译效率、mRNA 稳定性、蛋白表达，甚至疾病相关突变效应。

传统 codon optimization 往往依赖宿主 codon bias、CAI 或少数手工规则，
但真实 CDS 中的 codon 选择是上下文相关的：
相邻 codon、GC content、RNA 结构、tRNA 可用性、蛋白功能约束等因素都可能交织在一起。

一句话总结：
`CodonFM` 想把 CDS 看成一种以 codon 为 token 的“语言”，
通过大规模自监督学习捕捉同义密码子选择背后的上下文语法。

## Method

论文当前主要介绍 `CodonFM` 家族中的 **EnCodon** 系列模型。

1. **大规模 CDS 预训练数据**
   - 数据来自 NCBI RefSeq / Genomes。
   - 规模超过 **130 million** 条 coding sequences。
   - 覆盖超过 **22,000 species**。
   - 覆盖 bacteria、archaea、fungi、plants、protozoa、metazoans 等主要系统发育类群。
   - 出于 biosafety 考虑，作者排除了 human-affecting pathogen sequences。

2. **codon-level tokenization**
   - 模型不是按单个 nucleotide 建模，而是按三联体 codon 建模。
   - 每条 ORF 以 `<CLS>` 开始，以 `<SEP>` 结束。
   - 上下文长度为 **2,046 codons**，基本覆盖大多数天然 CDS。

3. **BERT-style masked codon modeling**
   - `EnCodon` 使用 Transformer encoder。
   - 训练目标类似 masked language modeling，但 mask 单位是 codon。
   - 模型需要根据上下文预测被 mask 的 codon。

4. **模型规模与 masking 策略**
   - 作者训练了 `EnCodon 80M`、`EnCodon 600M` 和 `EnCodon 1B`。
   - 还训练了 `EnCodon 1B-CDWT`，使用 codon-frequency weighted masking。
   - `CDWT` 的思路是更重视低频或信息量更高的 codon，
     让模型不要只学到高频 codon 的表面分布。

5. **评估任务**
   - 表征分析：synonymous codon confusion、UMAP、taxonomy KNN purity、MLM loss。
   - missense variants：DDD、ASD、ClinVar missense、cancer hotspots。
   - synonymous variants：ClinVar pathogenic vs benign synonymous variants。
   - mRNA design features：translation efficiency 和 mRFP protein expression。

## Main Figures

下列主图由 PDF 内嵌图片直接抽取得到，未包含图注文字。

### Fig. 1：数据、模型结构和预训练

![Fig. 1](./figures/fig1.png)

#### Fig. 1A：训练数据规模

作者从 NCBI RefSeq / Genomes 收集超过 `130M` 条 CDS，
覆盖超过 `22,000` 个物种。
这说明模型不是针对人类或少数模式生物训练，
而是试图学习跨物种的 codon 使用语法。

#### Fig. 1B：物种类别分布

数据集中 bacteria 占比最高，
同时包含 archaea、fungi、plants、protozoa、primates、non-primate mammals 等类别。
这个分布很重要：
codon usage bias 有明显物种差异，
跨类群训练能迫使模型学习更通用的 codon grammar。

#### Fig. 1C：CDS 长度分布

横轴是 codon 数量，纵轴是序列数量。
大多数 CDS 长度低于 1,000 codons，
而模型上下文长度为 2,046 codons。
因此，绝大多数 CDS 可以被完整放入模型上下文中，
不需要严重截断。

#### Fig. 1D：EnCodon 的 masked codon modeling

这幅图展示模型输入和训练目标。
输入是 codon token 序列，例如 `<CLS> ATG GCG <MASK> ... TGA <SEP>`。
Transformer encoder 根据上下文预测被 mask 的 codon。

这里和普通 DNA/RNA language model 的关键区别是：
token 不是单个碱基，而是 codon。
模型天然对齐翻译单位，因此更适合学习同义 codon 之间的上下文选择。

#### Fig. 1E：不同规模模型的验证损失

图中比较 `80M`、`600M`、`1B` 和 `1B-CDWT` 的 validation loss。
总体趋势是模型越大，loss 越低，收敛更好。
这给后续结果提供了基础：
codon grammar 的学习具有明显 scaling behavior。

### Fig. 2：模型学到的 codon grammar 和系统发育结构

![Fig. 2](./figures/fig2.png)

#### Fig. 2A：synonymous codon confusion

这一组矩阵看模型在预测 masked codon 时，
是否容易把同义 codon 混淆。
随着模型从 `80M` 扩展到 `1B`，
normalized confusion scores 降低。

这说明大模型不只是知道哪些 codon 编码同一个氨基酸，
还开始区分同义 codon 在不同上下文中的使用偏好。
这是论文所谓 codon grammar 的核心证据之一。

#### Fig. 2B：embedding UMAP

作者将模型 embedding 降维可视化，
并按序列类别或系统发育分组着色。
更大的模型在 embedding 空间中形成更清晰的生物分组结构。

这说明 EnCodon 表征中包含物种或类群相关的 codon usage 信息，
而不仅是简单的 nucleotide composition。

#### Fig. 2C 左：MLM loss 跨 taxonomy 的分布

这一部分比较不同模型在各类群上的 masked codon prediction loss。
大模型整体 loss 更低，
说明扩大参数规模提升了 codon 上下文预测能力。

#### Fig. 2C 中：KNN purity

KNN purity 衡量 embedding 空间中邻近序列是否来自相同或相近类群。
`1B-CDWT` 表现最好，
说明 codon-frequency weighted masking 有助于形成更有生物组织性的表征空间。

#### Fig. 2C 右：主成分与氨基酸疏水性的相关性

小模型的 top PCs 更容易和氨基酸疏水性这类基础生化属性相关。
更大模型的相关性下降，
作者将其解释为：大模型不只编码简单氨基酸属性，
还吸收了更复杂的 codon usage 和上下文调控信号。

### Fig. 3：missense variant 任务

![Fig. 3](./figures/fig3.png)

#### Fig. 3A-B：DDD 和 ASD de novo mutation

作者用 zero-shot scoring 比较 case 和 control missense variants。
评分方式是 reference codon 和 mutated codon 的 log-likelihood 差异。

EnCodon 在 DDD 和 ASD 数据上能较好地区分 case/control，
说明即使只在 CDS codon 序列上自监督训练，
模型也学到了一部分与蛋白功能约束和疾病风险相关的信号。

#### Fig. 3C-D：ClinVar missense 和 cancer hotspots

这两项使用 AUROC 评估分类能力。
EnCodon 明显优于多个 RNA / mRNA sequence model baseline，
但在部分任务上仍略低于 ESM2 这类蛋白语言模型。

这个结果符合直觉：
missense variant 会改变氨基酸，
蛋白语言模型直接建模氨基酸序列，因此天然占优；
但 EnCodon 仅靠 codon 序列仍能接近，说明 CDS 表征中隐含了蛋白功能约束。

#### Fig. 3E-G：fine-tuning 后的 missense variant 预测

作者进一步用 gnomAD missense variants fine-tune `EnCodon 1B`，
得到 `EnCodon 1B-FT`。
在 ASD 和 DDD 上，
fine-tuned EnCodon 与 AlphaMissense 等强监督模型相比也有竞争力。

这说明 EnCodon 不只是 zero-shot embedding 好用，
也可以作为下游 supervised variant effect prediction 的初始化模型。

### Fig. 4：synonymous variant 任务

![Fig. 4](./figures/fig4.png)

#### Fig. 4A：synonymous variant zero-shot 评分

这一幅说明任务设置：
对 ClinVar 中 pathogenic 和 benign synonymous variants 做 zero-shot 比较。
因为 synonymous mutation 不改变蛋白序列，
它们的功能影响通常更细微，也更难被传统蛋白模型捕捉。

#### Fig. 4B：控制混杂因素后的性能

作者做了 50 次 stratified subsampling，
控制 reference/alternate codon、基因位置、gene-level pLI 和 local mutation rate 等因素。
在这种更严格的比较下，
EnCodon 仍优于 RNA 和 mRNA baseline，
其中 `1B-CDWT` 表现最好。

这是论文最有辨识度的结果：
Codon-level model 的优势不只是 missense variant，
而是能捕捉不改变蛋白序列的同义突变效应。

### Fig. 5：mRNA translation 和 protein expression 任务

![Fig. 5](./figures/fig5.png)

#### Fig. 5A：translation efficiency

作者用预训练 embedding 训练 random forest regressor，
预测 mammalian cell 中的 mRNA translation efficiency。
EnCodon 模型整体优于 nucleotide-level baselines，
说明 codon-level 表征对翻译效率预测有直接价值。

#### Fig. 5B：mRFP protein expression

这一幅评估 mRFP protein expression 预测，
指标是预测值和实验表达量之间的 Spearman correlation。
`EnCodon 1B` 表现最好，
说明模型 embedding 包含与表达量相关的上下文信息。

有意思的是，`1B-CDWT` 在某些表达任务上不一定最高。
论文的解释是：
CDWT 表征受 GC content 等简单序列特征影响更小，
而某些表达数据中这些简单特征本身贡献较大。

## Key Insights

### 关键结果 1：codon usage 确实有可学习的上下文语法

如果同义 codon 真的是任意替换，
模型在 masked codon prediction 中不应该能系统区分它们。
但 EnCodon 的 confusion matrix、MLM loss 和 scaling 结果显示：
模型越大，越能预测哪个同义 codon 更适合当前上下文。

这支持论文的核心观点：
CDS 中存在一种超出氨基酸序列本身的 codon grammar。

### 关键结果 2：codon-level 模型能捕捉蛋白功能约束

EnCodon 没有直接以 amino acid sequence 作为输入，
但在 missense variant 任务上仍然有强表现。
这说明 CDS 序列中的 codon pattern 与蛋白功能、进化约束和疾病变异之间存在可学习联系。

不过在 missense 任务上，蛋白语言模型仍有天然优势。
因此 CodonFM 更像是蛋白模型的补充层：
它保留了 protein-level 信息，同时额外关注 codon-level regulation。

### 关键结果 3：同义突变是 CodonFM 最有特色的应用场景

同义突变不改变氨基酸，
蛋白语言模型通常无法直接感知。
EnCodon 在 ClinVar synonymous variant 任务上表现突出，
说明它能捕捉 codon choice 对临床变异效应的潜在影响。

这也是 CodonFM 相比一般 protein LM 或 nucleotide LM 的核心差异：
它的建模单位刚好落在遗传密码和翻译调控的交界处。

### 关键结果 4：对 mRNA 设计有直接意义

在 translation efficiency 和 mRFP expression 任务中，
EnCodon embedding 能作为有效特征。
这意味着它可以成为 mRNA 设计 pipeline 中的打分器或表征模型，
用于筛选更可能高表达或高翻译效率的 CDS。

和 `LinearDesign` 的区别是：
`LinearDesign` 显式优化 `MFE + CAI`，
而 `CodonFM` 学习的是天然 CDS 中隐含的 codon context。
两者未来可以互补：
一个提供可解释的物理/统计目标，
一个提供从大规模进化数据中学到的隐式语法评分。

## Limitations & Future Work

- **主要是计算验证**：论文结果以 benchmark 和 embedding analysis 为主，还需要更多 wet-lab perturbation 验证。
- **synonymous variant 数据有限**：有实验或临床标注的同义突变数量少，统计结果需要谨慎解释。
- **当前模型没有显式加入细胞上下文**：例如 cell-type-specific tRNA abundance、RNA modification、RBP binding 和 ribosome profiling context。
- **没有显式建模 RNA 二级结构动力学**：模型可能隐式捕捉部分结构相关信号，但没有像 LinearDesign 那样直接优化 MFE。
- **当前重点是 encoder 表征模型**：论文主要展示 EnCodon 系列，更强的生成式 codon design 还需要后续架构和实验闭环。

## Notes

- 当前目录主图位于 [figures](./figures/)。
- 图像由 `pdfimages` 直接从 PDF 内嵌图片抽取，未包含图注文字。
- 当前主文 PDF 为 [paper.pdf](./paper.pdf)。
