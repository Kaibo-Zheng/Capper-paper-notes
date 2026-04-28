# GEMORNA 与 mRNA 设计核心指标梳理

本文以 `AI4S/NucleicAcid/GEMORNA` 笔记为基础，归纳 mRNA 和 circRNA 设计中常用的评价指标。该内容有助于理解论文 *Deep generative models design mRNA sequences with enhanced translational capacity and stability* 的研究目标和评价体系，也可作为 AI4S 方向 mRNA 相关论文的通用评价参考。

以 GEMORNA 为例，mRNA 设计不仅关注 `CAI`、`MFE` 或 `MRL` 等单项指标，还需要在 `CDS`、`5'UTR` 和 `3'UTR` 组装为完整 RNA 后，进一步考察表达量、稳定性、表达持续时间以及治疗或疫苗相关功能。

## 1. 总体指标逻辑

治疗性 mRNA 通常由 `5' cap`、`5'UTR`、`CDS`、`3'UTR` 和 `poly(A)` 等模块组成。围绕这一结构，mRNA 设计任务可分为多个层次。`CDS` 设计关注在蛋白序列不变的前提下提高表达潜力，并减少不良编码模式；`UTR` 设计关注 `5'UTR` 和 `3'UTR` 对翻译起始效率、RNA 稳定性和表达持续性的影响；`full-length mRNA` 设计关注 `5'UTR`、`CDS` 和 `3'UTR` 组装后是否仍能提高蛋白表达及体内效果；`circRNA` 及相关功能场景则进一步考察环状 RNA、`CAR`、`EPO` 等任务中的持续表达能力和治疗相关功能。

从评价目标看，相关指标大致可分为计算筛选指标和实验终点指标。前者包括 `CAI`、`GC content`、`MFE`、`naturalness score` 和 `MRL` 等，主要用于候选序列生成、筛选和排序；后者包括蛋白表达 `fold-change`、表达持续性、小鼠抗体滴度、`EPO` 体内表达和 `CAR-T killing function` 等，更直接反映设计结果在具体任务中的效果。

在阅读和比较相关工作时，可优先关注治疗或疫苗功能指标，其次关注 `full-length mRNA` 的表达量与持续性，再进一步分析 `UTR`、`CDS` 层面的功能指标，以及序列组成和结构相关的代理指标。

## 2. 指标计算口径和来源

为了避免把不同类型的指标混在一起理解，可以先把它们分成三类。第一类是直接从序列计算的统计量，例如 `GC content`、`U percentage`、`CAI` 和 `rare codon rate`；第二类是由外部算法或模型给出的代理指标，例如 `MFE`、`naturalness score`、`PRED-5UTR` 预测的 `MRL` 和 `PRED-3UTR stability score`；第三类是实验读数或由实验读数归一化得到的指标，例如 `fold-change`、抗体滴度、累计表达和 `CAR-T killing function`。

下表给出本文后续常用指标的计算方式或来源。论文中没有完全公开实现细节的模型分数，应理解为“预测器输出”或“论文定义的归一化统计量”，不应误解为单一手工公式。

| 指标 | 怎么计算或怎么得到 | 主要来源和注意点 |
| --- | --- | --- |
| `GC content` | `(G + C) / N`，其中 `N` 是 RNA 序列长度。 | 直接由候选序列计算，通常按 `CDS`、`UTR` 或 full-length 序列分别统计。 |
| `U percentage` | `U / N`。 | 直接由序列计算；在治疗性 mRNA 中常作为尿嘧啶含量和潜在免疫识别风险的代理指标。 |
| `CAI` | `CAI = exp((1 / L) * sum_i log w_i)`，`w_i` 是第 `i` 个密码子相对同义密码子中最高使用频率密码子的权重。 | 需要宿主或参考高表达基因的密码子使用频率表；因此不同物种或参考表会得到不同 `CAI`。 |
| `rare codon rate` | `rare codon` 数量除以 `CDS` 长度；有些图中按核苷酸长度归一化，写作 `rare codon / nt`。 | 低频密码子的判定依赖参考密码子使用表和阈值。阅读论文图时要注意它是“比例”还是“每 nt 计数”。 |
| `codon pair quality` / `unwanted codon pair` | 扫描相邻密码子二联体，统计低频或不利的 codon pair，并按 `CDS` 长度归一化。 | 来自 codon pair usage 统计，而不是单个密码子频率；论文中常以 `unwanted codon pair / nt` 展示。 |
| `slippery site` | 用已知易引起核糖体移码的序列模式扫描 `CDS`，统计命中次数并按长度归一化。 | 属于 motif 检查指标；值越低通常越好，但它只覆盖已知模式。 |
| `MFE` / normalized `MFE` | 用 RNA 二级结构折叠算法预测最低自由能；normalized `MFE` 通常为 `MFE / N`。 | `MFE` 来自结构预测工具，不是实验测量。论文比较 `CDS` 或 `UTR` 时更常看长度归一化后的结构倾向。 |
| `naturalness score` | GEMORNA 先计算条件 log-likelihood：`M_s(x, y) = sum_t log p_theta(x_t; x_<t, y)`；再取长度归一化指数形式：`N_s(x, y) = exp(M_s(x, y) / L)`。 | 这是 `GEMORNA-CDS` 模型给出的零样本分数，表示在给定蛋白 `y` 下，`CDS` 序列 `x` 有多符合模型从哺乳动物天然 `CDS` 中学到的分布。 |
| `MRL` | 实验定义来自 `5'UTR` MPRA / ribosome load 数据；在 GEMORNA 中主要使用 `PRED-5UTR` 对候选 `5'UTR` 预测 `MRL`。 | `PRED-5UTR` 是论文训练的 GRU 预测器，训练标签来自带 `MRL` 标注的 `5'UTR` 数据；因此候选筛选阶段的 `MRL` 多数是预测值。 |
| `PRED-3UTR stability score` | 用 `PRED-3UTR` 对 `3'UTR` 输出稳定性相关分数。 | 论文中该预测器为 TextCNN，训练于公开实验数据中的 `3'UTR` 稳定性/降解相关标签；它反映的是预测稳定性贡献。 |
| `UTR novelty` / max identity | 将生成 `UTR` 与天然 `UTR` 数据库比对，记录最高序列 identity；最高 identity 越低，说明越不像直接复制训练集中某条序列。 | 论文中用 BLAST 计算 maximum identity score；该指标只说明相似度，不直接说明功能好坏。 |
| `reporter expression` | 转染后测 `Fluc`、`NanoLuc` 等 reporter 的发光或活性读数。 | 原始读数来自细胞实验；通常会按时间点、细胞系和对照序列进行归一化。 |
| `protein expression fold-change` | `fold-change = expression_design / expression_benchmark`，必须在相同细胞系、剂量、时间点和检测方法下比较。 | 文中的 `41-fold`、`15.9-fold`、`28-fold` 等数字都属于相对 benchmark 的比值，不是绝对表达量。 |
| `expression duration` / stability ratio | 常用后期读数除以前期读数，例如 `48 h / 24 h` 或 `144 h / 24 h`。 | 比值越高表示衰减越慢；它依赖采样时间点，不同实验之间不能直接混比。 |
| `cumulative expression` | 对多个时间点的表达读数做累计或近似积分，再与 benchmark 比较。 | 适合评价 `circRNA` 等长效表达体系；论文中的 `13.8-fold` 指累计表达相对 benchmark 的提升。 |
| antibody `titre` / `titer` | 血清做连续稀释后拟合曲线，取达到判定阈值的倒数稀释倍数。 | 论文中 endpoint titer 定义为“信号达到背景 2.1 倍”的倒数血清稀释度，并基于四参数 logistic 曲线拟合。 |
| `in vivo EPO expression` | 给药后在小鼠血清中测 `EPO` 蛋白或活性，再按同时间点 benchmark 归一化。 | 属于体内实验终点；文中的 `15-fold`、`121-fold` 等均是相对对照的体内表达提升。 |
| `CAR expression` | 通常用流式细胞术测 `CAR` 阳性率或 mean fluorescence intensity (`MFI`)。 | 论文中 `24 h` 表达提升来自 `MFI` 相对 benchmark 的 fold-change；持续性则看后续时间点的 `CAR` 阳性率。 |
| `CAR-T killing function` | 将表达 `CAR` 的 T 细胞与 CD19 阳性靶细胞共培养，统计靶细胞剩余量或杀伤比例。 | 这是功能终点，通常比 `CAR` 表达更接近治疗相关效果；论文的比较基于相同 E:T ratio 下的体外杀伤实验。 |

因此，阅读具体数值时要先问三个问题：这个指标是由序列直接计算、由模型预测，还是由实验读数得到；是否做了长度、时间点或 benchmark 归一化；比较对象是不是同一实验条件下的对照。

## 3. CDS 设计指标

`GEMORNA-CDS` 的任务是在给定目标蛋白序列的条件下，生成仍然编码同一蛋白、但更有利于表达的 mRNA `CDS`。

`CAI` 即 Codon Adaptation Index，用于衡量 `CDS` 的密码子使用模式是否接近宿主高表达基因的偏好。它先根据参考密码子使用表给每个密码子一个相对权重，再对整条 `CDS` 的权重取几何平均。该指标通常越高越有利，也是传统 `codon optimization` 中最常见的优化目标之一。但在 mRNA 设计中，高 `CAI` 并不必然对应最优表达，因为表达水平还受到 RNA 结构、局部上下文、`UTR` 组合及整体序列分布等因素影响。

`GC content` 指序列中 G 和 C 的比例，即 `(G + C) / N`。GC 含量会影响 RNA 二级结构稳定性、转录和翻译相关性质以及合成过程。过低或过高的 GC 比例均可能带来不利影响。因此，在 GEMORNA 中，`GC content` 更适合作为描述序列组成的指标，而不是唯一的优化目标。

`rare codon rate` 表示低频密码子的比例，通常按低频密码子数量除以 `CDS` 密码子总数计算；论文图中若写作 `rare codon / nt`，则表示按核苷酸长度归一化。低频密码子的判定来自宿主或参考密码子使用表。低频密码子比例过高可能降低翻译速度或影响蛋白产量，但低频密码子并非始终不利，因为局部翻译速度也可能参与蛋白折叠调控。GEMORNA 更关注生成序列的整体分布是否有利于表达，而不是简单消除所有低频密码子。

`U percentage` 指 RNA 序列中尿嘧啶 U 的比例，即 `U / N`。U 含量会影响 RNA 稳定性、免疫识别以及序列组成偏好。对于治疗性 mRNA 而言，过高的 U 含量通常不是理想状态。因此，该指标可用于辅助评价生成序列的质量。

`codon pair quality` 关注相邻密码子组合的性质，通常通过扫描相邻密码子二联体并统计不良或低频 `codon pair` 的出现次数得到。单个密码子的使用频率并不能完全解释翻译表现，密码子之间的相邻关系同样可能影响翻译稳定性。GEMORNA 相关结果表明，与传统 `codon optimization` 相比，该方法在规避不良 `codon pair` 方面具有一定优势，说明模型不仅学习单个密码子的偏好，也捕捉了更高阶的编码上下文。

`slippery site` 指可能导致核糖体移码或翻译异常的序列模式，计算时通常用已知 motif 规则扫描序列，并按序列长度统计命中率。对于治疗性 mRNA，应尽量降低此类序列模式出现的概率。对 GEMORNA 生成的 `CDS` 进行 `slippery site` 检查，有助于评估其安全性和表达准确性。

`MFE` 即 Minimum Free Energy，用于估计 RNA 二级结构的稳定性。它来自 RNA 折叠算法的结构预测结果，论文比较时常使用长度归一化后的 `MFE / N`。一般而言，`MFE` 数值越低，预测结构越稳定。但 GEMORNA 并非直接围绕 `MFE` 和 `CAI` 进行显式优化，`MFE` 在其中更多用于辅助比较生成序列的结构倾向。需要注意的是，最低 `MFE` 并不必然对应最高表达；过度稳定的结构可能阻碍核糖体扫描或翻译起始。

`naturalness score` 是 GEMORNA 中较具代表性的指标，可理解为模型对序列是否接近高质量天然编码序列分布的估计。论文中它来自 `GEMORNA-CDS` 对候选 `CDS` 的条件 log-likelihood，并取长度归一化后的指数形式，因此本质上是模型分数，不是单一物理量。相关笔记指出，该指标与表达量和稳定性表现具有较强相关性。其意义在于，GEMORNA 并不局限于 `CAI`、`GC content` 或 `MFE` 等少数人工规则，而是尝试学习高性能序列的整体分布特征。

## 4. UTR 设计指标

`GEMORNA-UTR` 分别生成 `5'UTR` 和 `3'UTR`。二者功能不同：`5'UTR` 主要影响翻译起始效率，`3'UTR` 更多参与 RNA 稳定性、表达持续时间及调控过程。

`MRL` 即 Mean Ribosome Load，常用于评价 `5'UTR` 对翻译起始和核糖体加载的影响。实验 `MRL` 标签通常来自大规模 `5'UTR` 翻译实验或 ribosome load 数据；在 GEMORNA 的候选筛选中，`MRL` 主要由 `PRED-5UTR` 预测得到。`MRL` 通常越高，说明翻译起始能力越强。因此，`MRL` 是 `5'UTR` 设计中的重要计算指标。

`PRED-5UTR` 是论文中用于评估 `5'UTR` 性能的预测器，主要预测 `5'UTR` 的翻译能力，对应 `MRL` 或类似的翻译起始代理指标。论文方法中该预测器使用带 `MRL` 标签的 `5'UTR` 数据训练，然后对天然或生成的 `5'UTR` 打分。该预测器用于生成后的候选筛选，也参与高性能 `UTR` 分布的微调。它并非最终实验结果，但会影响后续进入实验验证的候选序列范围。

`PRED-3UTR stability score` 用于评估 `3'UTR` 对 RNA 稳定性的贡献。它不是直接从序列长度或碱基比例计算出来的，而是 `PRED-3UTR` 根据公开实验数据训练后输出的稳定性相关预测分数。`3'UTR` 不直接编码蛋白，但会影响 RNA 在细胞内持续存在的时间。对于治疗性 mRNA，稳定性和持续表达是重要设计目标，因此该指标有助于筛选可能延长表达窗口的 `3'UTR`。

`UTR novelty` 或与天然序列的相似度，用于判断生成 `UTR` 是否只是复制训练集序列。论文中对应做法是将生成 `UTR` 与天然 `UTR` 数据库进行 BLAST 比对，并报告 maximum identity score；maximum identity 越低，说明越不像已有天然序列。较高的 `novelty` 说明生成序列与天然训练序列并不完全相同。但 `novelty` 不能脱离功能表现单独评价。GEMORNA 的结果表明，生成 `UTR` 虽然与天然 `UTR` 相似度较低，仍可获得较好的功能表现。

`UTR` 设计同样会关注 `MFE`。`5'UTR` 结构过于稳定可能影响核糖体扫描和翻译起始，`3'UTR` 结构则可能影响 RNA 稳定性以及调控蛋白或 RNA 的结合。因此，`MFE` 是有价值的结构代理指标，但不能替代表达实验。

GEMORNA 笔记还强调，最优 `UTR` 组合具有明显的 `target-dependent` 特征。某个 `5'UTR` 或 `3'UTR` 不一定适用于所有目标蛋白，`5'UTR`、`CDS` 和 `3'UTR` 之间存在组合效应。文中提到超过 80% 的 `UTR` 组合优于基准组合，但不存在简单的通用最优 `UTR`。这也说明 `full-length mRNA` 组装验证具有必要性。

## 5. Full-length mRNA 实验指标

`full-length mRNA` 实验是 GEMORNA 评价体系中的关键部分。单独 `CDS` 或 `UTR` 表现较好，并不意味着组装为完整 mRNA 后仍能保持优势。

`reporter expression` 通常通过 `Fluc`、`NanoLuc` 等 `reporter gene` 测量。相关读数反映生成 mRNA 产生目标蛋白的能力，原始数据是发光强度或蛋白活性，通常会在同一时间点下除以 `benchmark` 得到 `fold-change`。笔记中提到，`Fluc` 完整 mRNA 最高可实现 41-fold 提升，即对应设计的 reporter 读数约为 benchmark 的 41 倍。该指标可直接用于判断 `full-length` 设计是否有效。

`protein expression fold-change` 表示相对对照序列的蛋白表达提升倍数，计算式为 `expression_design / expression_benchmark`。例如，`Fluc full-length mRNA` 最高达到 41-fold，`GMR-FL-F5` 在 HepG2 中相对 `Benchmark-FL2` 达到 15.9-fold。该指标必须限定在相同递送条件、细胞系、剂量、检测时间和归一化方法下解释，反映设计序列是否能够产生更多目标蛋白。

`expression duration` 用于衡量 mRNA 或 RNA 构建在细胞或体内维持蛋白表达的时间。常见计算方式是比较不同时间点的表达读数，例如 `48 h / 24 h` 或 `144 h / 24 h`；也可以通过时间曲线观察表达衰减速度。对于疫苗任务，适当的表达持续性有助于抗原呈递；对于治疗蛋白任务，持续表达可能降低给药频率或扩大药效窗口。GEMORNA 在 `EPO` 和 `circRNA` 场景中均关注表达的强度和持续时间。

`COVID-19 vaccine antigen antibody titre` 是疫苗抗原任务中的核心功能指标。论文比较了 GEMORNA 设计、`BNT162b2` 风格对照和 LinearDesign 等方案。该指标来自小鼠血清 ELISA：血清连续稀释后拟合曲线，endpoint titer 取达到背景信号 2.1 倍阈值时的倒数稀释度。笔记中提到，`COVID-19 mRNA vaccine` 在小鼠中诱导的抗体滴度高于 `BNT162b2` 和 LinearDesign。与 `CAI` 或 `MFE` 等计算指标相比，抗体滴度更接近疫苗任务的功能终点。

`EPO expression` 用于评价治疗蛋白场景中的表达效果。体外实验关注细胞上清中的 `EPO` 蛋白或活性读数，体内实验关注小鼠血清中的 `EPO` 表达强度和持续时间；文中的 fold-change 同样按同时间点 benchmark 归一化。该任务说明 GEMORNA 不仅适用于疫苗抗原设计，也可迁移到治疗蛋白 mRNA 设计。

## 6. circRNA 与治疗功能指标

GEMORNA 还扩展到 `circRNA` 和 `CAR-T` 场景。这部分指标更侧重表达持续性和真实功能验证。

`cumulative expression` 表示一段时间内累计产生的蛋白总量，通常由多个时间点的表达读数求和或近似积分得到，再与 benchmark 的累计读数相除。由于 `circRNA` 通常具有更持久的表达特征，其累计表达可能明显高于线性 mRNA。笔记中提到，`EPO circRNA` 体外累计表达提升 13.8-fold，含义是指定观察窗口内累计 `EPO` 读数为 benchmark 的 13.8 倍。与单一时间点表达相比，该指标更能反映长效 RNA 的优势。

`144 h / 24 h expression ratio` 用于衡量后期表达相对于早期表达的保留程度，计算式为 `expression_144h / expression_24h`。比值越高，说明表达衰减越慢。笔记中提到，该比值最高达到 46.5%，而 `benchmark` 为 2.5%。这一指标对于 `circRNA` 尤其重要，因为表达持续性是 `circRNA` 设计的主要目标之一。

`in vivo EPO expression` 是治疗蛋白递送的体内功能验证，来自给药后小鼠血清中的 `EPO` 检测读数，并按同时间点 benchmark 归一化。笔记中提到，`EPO circRNA` 在小鼠体内的最强结果达到 121-fold。该结果说明设计优势不仅存在于细胞实验，也可在体内环境中体现。

`CAR expression` 用于评价 `CD19 CAR circRNA` 场景下 `CAR` 蛋白是否有效表达。论文中主要通过流式细胞术得到 `CAR` 阳性率或 `MFI`，再计算相对 benchmark 的 fold-change。笔记中提到，`CD19 CAR circRNA` 在 24 小时表达水平上相对两个对照分别达到 28-fold 和 5.6-fold，说明 RNA 设计能够显著提高 `CAR` 表达。

`CAR-T killing function` 是 `CAR` 场景中最接近真实功能的评价指标。它来自表达 `CAR` 的 T 细胞与 CD19 阳性靶细胞共培养后的杀伤实验，通常根据靶细胞剩余量、存活率或归一化杀伤比例计算。较高的 `CAR` 表达并不必然转化为更强的杀伤能力，因此还需要考察 `CAR-T` 对 CD19 阳性靶细胞的杀伤效果。GEMORNA 笔记指出，相关设计不仅提高 `CAR` 表达，也增强了细胞杀伤功能。

## 7. 指标之间的关系

GEMORNA 的指标体系可概括为从序列组成和结构代理指标，到预测器筛选，再到 `CDS` 与 `UTR` 组合，进一步到 `full-length mRNA` 表达，最终落实到体内持续性、免疫反应或治疗功能的多层评价链条。

理解该体系时，需要注意以下几点。`CAI` 较高并不必然带来高表达；`MFE` 较低也不一定意味着最优结构，过度稳定的 RNA 结构可能影响翻译；`naturalness score` 是 GEMORNA 的特色指标，旨在刻画高质量天然序列的整体分布；`MRL` 对 `5'UTR` 设计十分重要，但最终仍需通过 `full-length` 表达验证；在疫苗任务中，抗体滴度等免疫结果比计算代理指标更接近最终目标；在治疗蛋白任务中，体内表达强度和持续性比单纯体外 `reporter` 结果更具参考价值；在 `CAR-T` 场景中，最终应关注 `killing function`，而不是仅关注 `CAR` 表达量。

## 8. 核心指标概括

若对 mRNA 设计指标进行提炼，可重点关注以下项目：`naturalness score` 用于衡量生成 `CDS` 是否接近高质量天然编码分布；`CAI` 用于衡量 `codon` 使用是否接近高表达偏好；`GC content` 和 `U percentage` 反映序列组成特征；`rare codon rate` 反映低频密码子使用情况；`MFE` 用于估计 `CDS` 或 `UTR` 的 RNA 二级结构稳定性；`MRL` 用于衡量 `5'UTR` 的翻译起始和核糖体加载能力；`PRED-3UTR stability` 用于预测 `3'UTR` 对稳定性的贡献；`protein expression fold-change` 用于判断完整 mRNA 是否提高蛋白表达；`expression duration` 用于评价 `full-length mRNA` 或 `circRNA` 表达是否更持久；`antibody titre` 用于判断疫苗抗原是否诱导更强免疫反应；`in vivo EPO expression` 用于评价治疗蛋白在体内的表达效果；`CAR-T killing function` 用于判断表达提升是否能够转化为细胞治疗中的真实杀伤功能。

## 9. 总结

以 GEMORNA 为例，mRNA 设计的核心评价体系并不局限于 `CAI`、`MFE` 或 `MRL` 等单项指标，而是涵盖从序列代理指标到实验终点的多层指标。真正支撑设计有效性的证据在于，生成的 `CDS`、`UTR` 和 `full-length RNA` 能够在表达量、稳定性、表达持续时间、疫苗免疫反应及治疗相关功能等方面优于基准方案。
