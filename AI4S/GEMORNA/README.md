# GEMORNA

## Paper Info

- **Title**: Deep generative models design mRNA sequences with enhanced translational capacity and stability
- **Authors**: He Zhang, Hailong Liu, Yushan Xu, Haoran Huang, Yiming Liu, Jia Wang, Yan Qin, Haiyan Wang, Lili Ma, Zhiyuan Xun, Xuzhuang Hou, Timothy K. Lu, Jicong Cao
- **Venue**: Science, **390**, eadr8470
- **Date**: 2025-11-06
- **DOI**: [10.1126/science.adr8470](https://doi.org/10.1126/science.adr8470)
- **Paper**: [paper.pdf](./paper.pdf)
- **Supplementary**: [supplementary_materials.pdf](./supplementary_materials.pdf)

## TL;DR

这篇论文在做一个更接近真实药物开发流程的任务：

**给定你想表达的蛋白，直接生成一条更适合做治疗或疫苗的 mRNA/circRNA 序列，使其表达更高、持续更久、功能更强。**

作者提出的 `GEMORNA` 将问题拆成两部分：

- `GEMORNA-CDS`: 给定蛋白序列，生成编码同一蛋白但更优的 `CDS`
- `GEMORNA-UTR`: 从头生成更强的 `5'UTR` 和 `3'UTR`

然后把这些模块组合成完整 mRNA，并在 `luciferase`、`COVID-19 vaccine antigen`、`EPO`、`CD19 CAR`、`circRNA` 等任务上做体外和体内验证。

这篇工作的价值不只是“又做了一个 RNA language model”，而是把 **生成模型 + 序列设计 + 实验筛选** 这条链真正打通了。

## 从零理解这个任务

如果刚接触这个方向，可以先记住一条主线：

```text
DNA -> mRNA -> Protein
```

治疗性 mRNA 的目标是：把一条人工设计的 RNA 送进细胞，让细胞替你生产目标蛋白。

一条典型的 mRNA 可以粗略写成：

```text
5' cap | 5'UTR | CDS | 3'UTR | poly(A)
```

其中最关键的三个序列部分是：

- `5'UTR`: 不编码蛋白，但影响翻译起始效率
- `CDS`: 真正编码蛋白的区域
- `3'UTR`: 不编码蛋白，但影响稳定性、寿命和调控

这篇论文关心的核心问题是：

**同一个蛋白可以由很多不同的 RNA 序列编码出来，但这些序列在细胞里的效果差异很大。能否让生成模型直接设计出更像“药物分子”的 RNA 序列？**

### 为什么这件事有优化空间

- 多数氨基酸对应多个同义密码子，所以 `CDS` 可以有很多种写法
- `5'UTR` 和 `3'UTR` 也有大量可选设计
- 同样编码同一蛋白，不同序列的翻译效率、稳定性、免疫原性可能完全不同

所以这不是“蛋白预测任务”，而是：

**面向治疗应用的 RNA 序列生成与优化任务**

## 论文到底在做什么

作者把任务分成三个层次：

1. **CDS 设计**
   - 输入：目标蛋白序列
   - 输出：编码同一蛋白、但更适合高表达的 CDS

2. **UTR 设计**
   - 输出：新的 `5'UTR` 和 `3'UTR`
   - 目标：让同样的 CDS 表达更强、更持久

3. **Full-length mRNA 设计**
   - 将 `5'UTR + CDS + 3'UTR` 组合成完整 mRNA
   - 用真实实验验证表达量、持续时间和治疗相关效果

后面作者又把这套思路扩展到了 `circRNA`，证明生成式设计不仅适用于普通线性 mRNA，也适用于更稳定但更难设计的环状 RNA。

## 方法理解

### 1. GEMORNA-CDS

`CDS` 任务本质上是：

**在“目标蛋白固定”的条件下，生成一条满足氨基酸约束的密码子序列。**

因此作者把它建模成类似机器翻译的问题：

- 输入“源语言”: 蛋白序列
- 输出“目标语言”: CDS 密码子序列

模型采用 `Transformer encoder-decoder`：

- `encoder` 读入蛋白序列
- `decoder` 在蛋白约束下生成 CDS

这很合理，因为这里不是无条件生成，而是严格的条件生成。

### 2. GEMORNA-UTR

UTR 的情况和 CDS 不一样：

- UTR 不直接编码蛋白
- 不存在“唯一正确”的 UTR
- 更像是在生成一段可工作的调控元件

因此作者使用 `decoder-only` 的自回归生成模型，先在大量天然 UTR 上预训练，再向高性能 UTR 分布做微调。

其中：

- `PRED-5UTR` 用来预测 `MRL`，近似反映翻译起始能力
- `PRED-3UTR` 用来预测稳定性

### 3. 训练规模

主文和补充材料给出的训练数据规模大致是：

- `GEMORNA-CDS`: 超过 **100 万** 条天然 protein-CDS 配对，来自 **115** 个哺乳动物物种
- `GEMORNA-UTR` 预训练: 约 **800 万 5'UTR** 和 **200 万 3'UTR**
- `GEMORNA-UTR` 微调: 约 **80 万 5'UTR** 和 **20 万 3'UTR**

### 4. 作者想强调的核心点

传统方法往往是手工优化少数指标，比如：

- `CAI`
- `GC content`
- `U percentage`
- `MFE`

GEMORNA 试图学习的是更整体的高性能分布，而不只是单独把某一个指标堆高。

作者还提出了一个 `naturalness score`，可以理解成：

**这条序列在模型看来有多像哺乳动物偏好的高质量编码序列。**

## Main Figures

下面这 5 张图已经从主文 PDF 中重新裁成了无图注版本。

### Fig. 1

![Fig. 1](./figures/fig1.png)

这张图讲的是问题定义。

- `A`: 同一个蛋白可以对应海量不同的 mRNA 设计
- `B`: GEMORNA 的作用是把巨大的总搜索空间压缩到“更可能高性能”的候选空间，再交给实验去验证

要点：

- 作者不是在枚举搜索所有序列
- 而是在学一个“高潜力生成空间”

### Fig. 2

![Fig. 2](./figures/fig2.png)

这张图是 `CDS` 部分。

- `A-B`: `GEMORNA-CDS` 的训练和推理结构图
- `C-D`: 与随机序列、天然序列、CAI 优化序列、LinearDesign 等比较，展示多个优化相关指标的分布
- `E`: 指标与实验结果的相关性
- `F-G`: 只改 `CDS` 时的表达和稳定性实验

要点：

- 只改 `CDS`，表达就能显著变化
- GEMORNA 生成的 CDS 在多个维度上都更像高性能序列
- 作者认为 `naturalness score` 与表达和稳定性最相关

### Fig. 3

![Fig. 3](./figures/fig3.png)

这张图是 `UTR` 部分。

- `A-B`: `GEMORNA-UTR` 的训练和推理结构
- `C`: 用预测器筛选高质量 UTR 做微调
- `D`: 生成 UTR 的 novelty、MRL、MFE 分布
- `E-F`: 生成的 5'UTR 与 benchmark 对比
- `G`: 不同细胞系之间结果相关
- `H-M`: 5'UTR 和 3'UTR 组合实验

这张图里最值得记住的结论有三条：

- 生成的 UTR 和天然 UTR 相似度低，但功能可以更强
- 5'UTR 对表达调控的影响尤其显著
- UTR 的最优组合强烈依赖目标蛋白，不存在普适万能 UTR

文中一个很重要的数字是：

- 跨不同蛋白目标时，UTR 组合表现相关性很低，`r^2 = 0.096`

这说明 UTR 设计是明显的 `target-dependent` 问题。

### Fig. 4

![Fig. 4](./figures/fig4.png)

这张图是 `full-length mRNA` 部分。

- `A`: 验证对象总览
- `B-C`: Fluc 完整 mRNA 的表达结果
- `D-H`: COVID-19 vaccine antigen 的表达和小鼠免疫结果
- `I-L`: EPO 完整 mRNA 的体外和体内结果

这张图的意义是：

**单个模块的优势没有在组合后消失，而是能够落到完整药物分子层面。**

主文中比较醒目的结果包括：

- `Fluc` 完整 mRNA 最高达到 **41-fold** 提升
- `GMR-FL-F5` 在 HepG2 中相对 `Benchmark-FL2` 达到 **15.9-fold**
- COVID-19 mRNA vaccine 在小鼠中诱导的抗体滴度高于 `BNT162b2` 和 `LinearDesign`
- EPO full-length 设计在小鼠中也表现出更强和更持久的表达

### Fig. 5

![Fig. 5](./figures/fig5.png)

这张图是 `circRNA` 和 `CAR-T` 扩展。

- `A-B`: circRNA 设计拓扑
- `C-E`: NanoLuc circRNA 的表达和持久性
- `F-H`: EPO circRNA 的体外和体内结果
- `I-M`: CD19 CAR circRNA 的表达、持续时间和杀伤功能

这部分说明：

**GEMORNA 不只适用于线性 mRNA，也能扩展到更稳定但更难设计的 circRNA。**

文中比较重要的数字包括：

- EPO circRNA 体外累计表达提升 **13.8-fold**
- `144 h / 24 h` 表达比最高达到 **46.5%**，benchmark 只有 **2.5%**
- 小鼠体内 EPO circRNA 最强结果达到 **121-fold**
- CD19 CAR circRNA 在 24 小时表达上，相对两个对照分别达到 **28-fold** 和 **5.6-fold**

## 主要结果汇总

### CDS 设计

- GEMORNA 生成的 CDS 具有更高的 `CAI`、更高的 `GC`、更低的 rare codon rate、较低的 `U percentage`
- 相比传统 codon optimization，GEMORNA 更能避免不良 codon pair、slippery site 等问题
- 在 luciferase 实验中，只换 CDS 就能带来显著表达提升

### UTR 设计

- 生成的 UTR 与天然序列相似度低，说明不是简单复读训练集
- 在主文实验中，部分 GEMORNA `5'UTR` 达到或超过 `BNT162b2`
- 超过 **80%** 的 UTR 组合优于基准组合

### Full-length mRNA

- 在 `Fluc`、`COVID-19 vaccine antigen`、`EPO` 等任务上都展示了优势
- 说明这套方法不是仅在一个 reporter gene 上有效
- 已经开始接近真实药物开发中的设计和筛选逻辑

### circRNA

- 表达更持久
- 体内优势更明显
- 在 CAR-T 功能实验中不仅提高表达，还带来更强的细胞杀伤能力

## Supplementary Materials 在补什么

补充材料文件见 [supplementary_materials.pdf](./supplementary_materials.pdf)。

它的价值主要在于把主文里的很多关键结论补得更扎实。

### Supplementary Text

补充文字主要做了三件事：

1. 正式写出 full-length mRNA 设计空间的数学表达
2. 写清 `GEMORNA-CDS` 和 `GEMORNA-UTR` 的训练目标
3. 解释不同解码策略为什么会生成不同风格的序列

### Figs. S1-S15

可按主题来读：

- `Fig. S1-S5`: CDS 部分的补图
- `Fig. S6-S8`: UTR 与预测器部分的补图
- `Fig. S9-S10`: Full-length mRNA 的额外验证
- `Fig. S11-S15`: circRNA 与 CAR-T 的扩展验证

其中比较关键的补充点包括：

- `S2`: 不同解码策略会改变 CAI、MFE、naturalness 等分布
- `S3`: GEMORNA 会主动避开更不稳定的 codon
- `S6`: `PRED-5UTR` 的预测效果与已有方法比较
- `S8`: 把稳定 motif 强行加入 3'UTR 不一定继续提升表达
- `S9`: COVID vaccine 在更低剂量 `1 µg` 条件下的结果
- `S10`: 完整 mRNA 任务扩展到 NanoLuc
- `S14-S15`: CAR-T 表达与杀伤功能的更细验证

### Tables and Data

- `Table S1`: 主文所有线性 mRNA 构建的 `5'UTR / CDS / 3'UTR` 组合
- `Table S2`: 所有 circRNA 构建的组件组合
- `Data S1-S4`: 记录了序列、可视化原始数据、相关性数据和 5'UTR in silico 数据说明

这些内容对复现论文中的命名、构建方案和对照关系很有帮助。

## 我对这篇文章的理解

### 它最重要的贡献是什么

我认为这篇论文最重要的地方不是单个数字多高，而是它把范式推进了一步：

**从“给 RNA 打分”推进到“直接生成高质量候选，再用实验筛选”。**

更具体地说，它做到了：

- 不只优化 `CDS`
- 也不只做 `UTR`
- 而是把 `CDS + UTR + full-length + circRNA` 串成了一条连续设计链

### 为什么这篇工作比普通方法更强

因为真实的 mRNA 设计不是单指标优化。

只盯着某个指标，例如：

- `CAI`
- `GC`
- `MFE`

通常不够。真正影响表达和稳定性的因素存在复杂耦合，很多还不是人能轻易写成显式规则的。

GEMORNA 的价值就在于：它试图把这些复杂关系吸收到生成分布里，再通过实验去验证是否真的有用。

### 为什么作者要做这么多不同任务

因为他们想证明这不是一个局限在某个 toy task 上的小技巧。

他们使用：

- `Fluc` 和 `NanoLuc`: 量化表达强弱
- `COVID-19 spike`: 验证疫苗场景
- `EPO`: 验证治疗蛋白场景
- `CD19 CAR`: 验证细胞治疗场景

这相当于在不同应用面前做泛化测试。

### 我认为它的局限

作者自己在讨论部分也承认了一些问题，我基本同意：

- 模型仍然偏黑箱，机制解释不强
- 许多实验规模仍然不大，常见是 `n = 3` 体外、`n = 4` 或 `n = 5` 小鼠
- 最优 UTR 组合明显依赖 target，说明“通用最优设计”并不存在
- 未来如果要真正走向更强的工程化应用，还需要更系统的高通量实验闭环

### 我的总体评价

如果用一句话概括这篇工作：

> GEMORNA 的关键贡献不是“又一个 RNA 语言模型”，而是把生成式 AI 在 mRNA/circRNA 设计中的工程价值做到了足够可信。

它已经不只是停留在算法指标，而是通过多种体外和体内实验，把“生成模型能不能真正帮助 RNA 药物设计”这件事回答到了一个比较强的程度。

## Notes

- 本目录下主图无图注版本位于 [figures](./figures/)
- 当前主文配图包括 `fig1.png` 到 `fig5.png`
- 补充材料已经统一命名为 [supplementary_materials.pdf](./supplementary_materials.pdf)
