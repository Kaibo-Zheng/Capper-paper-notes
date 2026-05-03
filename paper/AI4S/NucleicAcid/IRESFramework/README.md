# IRESFramework

## Paper Info

- **Title**: Programmable RNA translation through deep learning-driven IRES discovery and de novo generation
- **Authors**: Yanyi Chu, Di Yin, Dan Yu, Guangxue Xu, Junze Zhang, Xiaotong Wang, Yue Shen, Yupeng Li, Ning Zhao, Yi Zhu, Jason Zhang, Hani Goodarzi, Mengdi Wang, Le Cong
- **Venue**: Nature Machine Intelligence 2026, Volume 8, 559-574
- **Date**: 2026-04-24
- **DOI**: [10.1038/s42256-026-01213-z](https://doi.org/10.1038/s42256-026-01213-z)
- **Paper**: [paper.pdf](./paper.pdf)
- **Code**: [a96123155/IRES_Prediction_Design](https://github.com/a96123155/IRES_Prediction_Design)
- **Data / Archive**: [Zenodo 10.5281/zenodo.15081323](https://doi.org/10.5281/zenodo.15081323)

## Abstract

这篇论文提出一个面向 `IRES` 的端到端 AI 框架，把三个原本分散的任务连在一起：识别 IRES、通过定向突变诱导或改变 IRES 功能、从头生成新的 IRES 序列。IRES 即 internal ribosome entry site，是能介导 cap-independent translation initiation 的 RNA 顺式作用元件，在 mRNA、circRNA、合成生物学和 RNA therapeutics 中都有价值。

论文的三部分分别是：`IRES-LM` 用 UTR-LM 和 RNA-FM 的集成模型识别 IRES；`IRES-EA` 用 IRES-LM 作为打分器，通过 evolutionary algorithm 对现有序列做功能诱导；`IRES-DM` 用 conditional denoising diffusion model 从噪声中生成新 IRES。最关键的是，作者不仅做了离线 benchmark，还用两批各 12,000 条序列的 MPRA 做大规模实验验证：EA 突变序列中 98.4% 获得可检测 IRES 活性，DM 生成序列中 99.3% 获得可检测 IRES 活性。

## Motivation

传统 mRNA 翻译通常依赖 5' cap 介导的起始机制，而 IRES 可以在没有 5' cap 的情况下招募核糖体并启动翻译。这对几类场景很重要：多顺反子表达、circRNA 翻译、压力状态下的翻译调控、RNA 疫苗和治疗性 payload 的表达增强。

难点在于，IRES 的序列-结构-功能关系并不清楚。已有工具如 `IRESfinder`、`IRESpy` 和 `DeepCIP` 多依赖 k-mer 或手工特征，且常常只适配 linear mRNA 或 circRNA 中的一类场景。另一方面，能不能把一个 non-IRES 序列改成 IRES，或者直接生成全新的功能性 IRES，也一直缺少可扩展的计算-实验闭环。

这篇论文的核心问题可以概括为：

1. 能否用 task-aligned RNA foundation models 学到跨 IRES 类型的判别特征？
2. 能否把 IRES 识别器变成序列优化器里的 fitness model？
3. 能否用生成模型扩展天然 IRES 之外的功能序列空间？

## Method

### 1. IRES-LM: consensus language model for IRES prediction

`IRES-LM` 是两个模型的 ensemble：`IRES-UTRLM` 和 `IRES-RNAFM`。作者选择 UTR-LM 和 RNA-FM 的原因是二者都与 5'UTR 或 non-coding RNA 功能建模更相关；相比之下，偏结构对齐的 RNA-BERT、ERNIE-RNA 以及更通用的 Evo-2 在这个任务上迁移效果较弱。

训练数据包含 **46,774** 条 binary-labelled sequences，其中 **9,172** 条为 IRES，**37,602** 条为 non-IRES。数据来自 Weingarten-Gabbay et al.、IRESbase、IRESite、Rfam 和 IRESpred 训练集。数据集中最长序列为 1,731 nt，但超过 80% 的序列长度是 174 nt。

模型结构上，UTR-LM 分支使用 6 层 Transformer、128 维 embedding；RNA-FM 分支使用 12 层 Transformer、640 维 embedding。两个分支都在 `[CLS]` 表征上接一个简单 MLP 做二分类。训练目标包括 masked nucleotide recovery 和 IRES / non-IRES classification。

关键结果：

- ensemble 后 `IRES-LM` 达到 `AUC = 0.78`、`AUPR = 0.62`、`F1 = 0.51`。
- 相比已有方法，AUC 和 F1 约提升 15%，AUPR 相比 DeepCIP 约提升 10%。
- 在 21 条已实验验证的 circRNA IRES 上，`IRES-LM` 识别出 21/21；DeepCIP、IRESfinder、IRESpy 分别识别出 15、9、7 条。
- 在 homology-controlled cluster-level cross-validation 下仍保持稳健，说明性能不完全来自相似序列泄漏。

### 2. IRES-EA: mutation-guided functional induction

`IRES-EA` 把 `IRES-LM` 变成 evolutionary algorithm 的打分器，用于定向突变。它既可把 non-IRES 往 IRES 方向优化，也可理论上把 IRES 往 non-IRES 方向破坏。论文主要展示前者。

流程可以拆成三步：

1. **Masking**：在 seed sequence 上选择要突变的位置，可随机选、按连续片段选、按 IRES-LM attention 权重选，也可用自定义碱基替换规则。
2. **Recovery / sampling**：用 IRES-LM 对 masked sites 给出 A/G/C/U 恢复概率，生成多个候选突变序列。
3. **Selection**：按候选序列的 predicted IRES probability 选择更好的序列作为下一轮 seed。

作者先在 **37,293** 条 174 nt 的 non-IRES 序列上做计算评估，每条最多允许 9 个突变位点。结果中 **60%** 序列被预测转换为 IRES，且 **5%** 的序列 predicted IRES probability 超过 0.9。

实验验证分两层。第一层是 EMCV 和 CVB3 IRES 的 bicistronic luciferase assay，用来观察少量突变体是否保留或增强活性，并结合 secondary structure 分析高活性突变体是否保持 wild-type-like folding。第二层是大规模 MPRA：从 6,730 条 negative wild-type sequences 派生出 **12,000** 条突变序列，用 mCherry-IRES-eGFP 双荧光 reporter 和 FACS-seq 分 4 个 bin 读出 IRES 活性。

MPRA 中 activity score 按归一化 read counts 的 bin 加权平均计算：

```text
activity score = sum_i i * n'_i / sum_i n'_i
```

其中 `i = 1..4`，bin 1 为 negative，bin 2-4 为逐渐增强的 positive bins。论文将 `activity score >= 2.0` 定义为 functional IRES。

IRES-EA 的 MPRA 结果：

- 12,000 条中 **11,930** 条有足够 barcode coverage。
- 平均 activity score 为 **2.45**。
- **98.4%**，即 11,746 条序列，达到 `activity score >= 2.0`。
- 62.6% 为 low activity，33.1% 为 medium activity，2.7% 为 high activity。
- bin 4 fraction 与 activity score 的相关性为 `r = 0.88`，支持 FACS-seq 读数可靠。

### 3. IRES-DM: de novo generation by conditional DDPM

`IRES-DM` 用 denoising diffusion probabilistic model 从噪声生成 RNA 序列。序列先转成 one-hot latent vector，forward process 按预设 schedule 加 Gaussian noise；reverse process 用 U-Net 预测噪声并逐步去噪。模型以 IRES / non-IRES label 为条件，因此可以条件生成 IRES 序列。

论文实现了两个版本：

- **Variable-length IRES-DM**：用全部 9,172 条 positive IRES 训练，生成长度 `<=200 nt` 的序列。
- **Fixed-length IRES-DM**：用 7,348 条长度正好为 174 nt 的 IRES 训练，用于标准长度生成。

每个版本又有两种训练策略：

- **Reward-guided**：引入 IRES-LM 作为 reward model。
- **Direct-training**：直接优化生成目标，不依赖 reward model，计算更省。

对比上，variable-length IRES-DM 优于 `GenerRNA`，尤其是去重后有效序列更多；fixed-length IRES-DM 优于随机序列生成，在 `IRES probability > 0.5` 的过滤条件下保留约 2,100 条，而随机序列约 952 条。

更重要的是 MPRA 验证。作者从四种生成设置构建 **12,000** 条生成序列的 library，其中包括 174 nt fixed-length 的 direct / reward-guided 模型，以及 variable-length 的 direct / reward-guided 模型。FACS-seq 回收 **11,887** 条有足够 coverage 的序列。

IRES-DM 的 MPRA 结果：

- **99.3%**，即 11,796 / 11,887 条序列，达到 `activity score >= 2.0`。
- 平均 activity score 为 **2.50**。
- 174 nt fixed-length 和 variable-length 模型都接近 99% success rate。
- direct-training 和 reward-guided 的差异很小，说明生成能力不完全依赖某一种训练策略。
- 生成序列可与 BiP IRES 只有 **27.6%** sequence identity，但保持相似二级结构，说明模型可能学到结构层面的功能约束，而不只是复制天然序列。

### 4. High-activity motifs

作者进一步把 EA 和 DM 的 MPRA 结果合并，分析与高 IRES 活性相关的 k-mer motif。由于 3-5 mer 信息量偏低、8 mer 以上统计功效不足，论文主要分析 6-mer 和 7-mer。

结果显示：

- 共识别 **36** 个 high-activity related 6-mer motifs，其中 13 个为 design-enriched，23 个为 natural-prevalent。
- 共识别 **22** 个 high-activity related 7-mer motifs，其中 19 个为 design-enriched，3 个为 natural-prevalent。
- 每条序列中 high-activity motifs 数量越多，平均 activity score 越高，提示这些 motif 可能存在加性或协同效应。

这里的 `design-enriched` 很有意思：它们在天然 IRES 中并不常见，却在 AI 生成的高活性序列中富集。这说明模型不是只复现天然高频模式，也可能探索到了天然进化没有充分采样的功能序列区域。

## Key Insights

### 1. 这篇论文的价值不只是 IRES classifier

如果只看 `IRES-LM`，这篇论文像是一个更好的 IRES 识别器。但真正的贡献在于把 classifier 放进了 design loop：`IRES-LM` 既是识别模型，又是 `IRES-EA` 的 fitness function，也是 `IRES-DM` 的 reward / filter 组件。这样一来，IRES 不再只是被动标注对象，而变成可以被诱导、生成和筛选的 translation regulatory element。

### 2. Task-aligned pretraining 比单纯模型规模更关键

论文比较了 UTR-LM、RNA-FM、RNA-BERT、ERNIE-RNA 和 Evo-2。结果显示，与 5'UTR 或 non-coding RNA 功能更相关的模型迁移最好；更通用或预训练目标不匹配的模型，即使规模更大，也不一定适合 IRES 识别。这点对 AI4S 很典型：foundation model 的价值取决于预训练信号是否贴近目标生物学问题。

### 3. MPRA 验证是本文最强的证据

很多 RNA 生成论文停留在离线指标、预测器分数或少量 wet-lab 验证。这篇文章较强的地方在于两批 12,000 条级别的 MPRA，且 EA 和 DM 各自独立验证。虽然大多数 positive 序列属于 low / medium activity，而不是 high activity，但这种规模的实验读数足以说明模型不是只在打分器上刷分。

### 4. 结构约束被间接学到，但还没有被显式控制

IRES 功能强依赖 RNA folding 和结构元件。论文展示了模型表示与 MFE、splicing score 有相关性，也展示了低 sequence identity 但结构相似的生成例子。不过当前 EA 和 DM 并没有把结构作为强约束直接优化，更多是通过训练分布和 IRES-LM 信号间接获得。这也是后续工作的主要空间。

### 5. 它和 UTR-LM / GEMORNA 的关系

`UTR-LM` 关注 5'UTR 的通用表征和功能预测；`GEMORNA` 关注 full-length mRNA 和 circRNA 的治疗相关序列生成；这篇 IRESFramework 则更聚焦于 cap-independent translation 元件。它可以看作 mRNA / circRNA 设计工具箱里的一个模块：当任务需要 polycistronic expression、circRNA translation 或不依赖 cap 的表达控制时，IRES 设计就变成关键子问题。

## Limitations & Future Work

- **训练长度分布偏窄**：数据集中超过 80% 是 174 nt 序列，虽然模型能泛化到部分 variable-length 序列，但低活性生成序列中更长序列富集，短于 174 nt 的序列最高活性也受限。
- **结构控制仍不够显式**：IRES-EA 和 IRES-DM 尚未直接把 RNA secondary / tertiary structure 作为硬约束或多目标优化项。
- **实验场景仍然有限**：MPRA 主要在 reporter system 和 HEK293T 相关体系中完成，距离不同细胞类型、不同 payload、体内递送和真实治疗场景仍有距离。
- **IRES-LM 既当裁判又当优化信号**：EA 和 reward-guided DM 都依赖 IRES-LM，可能放大预测器偏差。MPRA 已经缓解这个问题，但后续设计仍需要更多独立实验反馈。
- **高活性比例仍有提升空间**：大多数成功序列只是达到 detectable activity，真正 high / very-high activity 的比例较小；后续应该更关注强活性而非仅可检测。
- **motif 机制还需要验证**：design-enriched motifs 是很好的发现线索，但是否具有可迁移、可组合、可解释的生物机制，还需要系统扰动实验。

后续值得追的方向：

1. 将 structure prediction / folding constraints 接入 EA 和 DM，形成 sequence + structure 的联合设计。
2. 用主动学习把 MPRA 反馈闭环到模型更新，而不是只做一次性生成和筛选。
3. 针对具体 cell type、stress condition、circRNA context 或 therapeutic payload 做条件化 IRES 设计。
4. 把 IRES 设计与 full-length RNA design pipeline 结合，评估其对真实表达持续性、免疫反应和 payload function 的影响。

## Figure Roadmap

- **Fig. 1**: 总框架，串联 `IRES-LM`、`IRES-EA`、`IRES-DM` 和 MPRA 验证流程。
- **Fig. 2**: 三个模型模块的方法细节，包括 consensus language model、evolutionary mutation 和 conditional diffusion。
- **Fig. 3**: IRES-LM 的 benchmark、ablation 和 circRNA IRES 泛化结果。
- **Fig. 4**: IRES-EA 的突变流程、计算转换率和 12,000 条突变序列 MPRA。
- **Fig. 5**: IRES-DM 的生成质量、GenerRNA / random 对比、结构相似案例和 12,000 条生成序列 MPRA。
- **Fig. 6**: high-activity related 6-mer / 7-mer motif 的富集与累积效应。

## Assets

- 主文 PDF: [paper.pdf](./paper.pdf)
