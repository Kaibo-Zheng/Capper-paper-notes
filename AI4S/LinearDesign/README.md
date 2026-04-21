# LinearDesign

## Paper Info

- **Title**: Algorithm for optimized mRNA design improves stability and immunogenicity
- **Authors**: He Zhang, Liang Zhang, Ang Lin, Congcong Xu, Ziyu Li, Kaibo Liu, Boxiang Liu, Xiaopin Ma, Fanfan Zhao, Huiling Jiang, Chunxiu Chen, Haifa Shen, Hangwen Li, David H. Mathews, Yujian Zhang, Liang Huang
- **Venue**: Nature 2023, Volume 621
- **DOI**: [10.1038/s41586-023-06127-z](https://doi.org/10.1038/s41586-023-06127-z)
- **Paper**: [paper.pdf](./paper.pdf)
- **Code**: [LinearDesignSoftware/LinearDesign](https://github.com/LinearDesignSoftware/LinearDesign)

## Motivation

这篇论文要解决的是 mRNA 疫苗和治疗性 mRNA 设计里的核心组合优化问题：
给定目标蛋白，如何选择一条既编码同一个蛋白、又更稳定、更高表达的 mRNA CDS 序列。

传统 codon optimization 主要优化密码子使用偏好，例如 `CAI`，
但它并不能系统探索高二级结构稳定性的区域。
问题难点在于同义密码子导致搜索空间爆炸：
以 SARS-CoV-2 spike protein 为例，长度为 1,273 个氨基酸，
候选 mRNA 数量约 **2.4 x 10^632**。

一句话总结：
`LinearDesign` 把 mRNA CDS 设计转化成计算语言学中的 lattice parsing 问题，
从而在巨大同义编码空间中高效寻找兼顾 `MFE` 和 `CAI` 的序列。

## Method

作者的方法有三个关键设计：

1. **用 DFA 表示同义密码子空间**
   - 每个氨基酸对应一个 codon DFA。
   - 将所有 codon DFA 串联后得到整条蛋白的 mRNA DFA。
   - DFA 的每条 start-end path 对应一条可行 CDS 序列。

2. **用 lattice parsing 同时折叠所有候选序列**
   - RNA folding 可以写成类似 context-free grammar 的解析问题。
   - 单条序列 folding 是普通 parsing。
   - DFA 上的所有候选序列 folding 则变成 lattice parsing。

3. **用 weighted DFA 联合优化稳定性和密码子偏好**
   - 稳定性目标使用 `MFE`。
   - 密码子偏好用 `CAI`，并将 `log CAI` 分解到单个 codon 上。
   - 联合目标大致为：

```text
MFE - lambda * |protein| * log(CAI)
```

`lambda = 0` 时只优化稳定性，`lambda = infinity` 时退化为只优化 CAI。
通过调节 `lambda`，可以在稳定性和翻译效率之间形成一条可选边界。

## Main Figures

### Fig. 1：问题设定与算法直觉

![Fig. 1](./1.png)

这张图把全文核心压缩成一个对比：
同一个 spike protein 对应约 `2.4 x 10^632` 条候选 mRNA，
传统 codon optimization 只能沿着 CAI 方向移动，
而 LinearDesign 试图在 `MFE-CAI` 二维空间里找到以前不可达的高稳定设计区域。

### Fig. 2：DFA 和 lattice parsing 如何落到 mRNA 设计

![Fig. 2](./2.png)

这张图是方法核心：
用 DFA 表示所有同义 codon 组合，再把 RNA folding grammar 和 DFA 做交叉解析。
关键不是“搜索更快一点”，而是把指数级候选空间压缩成可以动态规划求解的结构。

### Fig. 3：MFE-CAI 设计边界与计算效率

![Fig. 3](./3.png)

Fig. 3 说明两件事：
一是 exact search 在实际长度范围内近似二次复杂度，beam search 近似线性；
二是 `MFE` 和 `CAI` 的可行边界可以由 `lambda` 连续扫出来，
这给实验候选选择提供了一个明确的 trade-off 曲线。

### Fig. 4：COVID-19 spike mRNA 实验验证

![Fig. 4](./4.png)

这是全文最重要的实验图。
它把 spike mRNA 的稳定性、细胞表达、抗体和 T cell response 放在同一个设计空间中，
显示低 MFE 与高 CAI 的折中序列能带来更高半衰期、更强蛋白表达和更高免疫反应。

### Fig. 5：VZV gE mRNA 的泛化验证

![Fig. 5](./5.png)

Fig. 5 用 VZV gE protein 验证方法不是 spike-specific。
结果也提醒读者：最低 MFE 不一定是表达最优点，
真正有效的区域通常是稳定性和 codon optimality 的折中区。

## Key Insights

### 关键结果 1：把巨大 mRNA 设计空间变成可计算的 lattice

最重要的方法贡献是形式化。
作者没有枚举所有同义序列，而是用 DFA 紧凑表示候选空间，
再通过 lattice parsing 一次性在这个空间上求最优。

在 SARS-CoV-2 spike protein 上，
`LinearDesign` 可以在约 **11 分钟**内找到高稳定性设计；
而直接枚举在计算上完全不可行。

### 关键结果 2：稳定性优化和 codon optimization 不是一回事

Fig. 3 里很清楚地展示了 `MFE` 和 `CAI` 的二维设计空间。
传统 codon optimization 会提升 CAI，但只能轻微改善稳定性；
而 `LinearDesign` 可以直接探索以前难以到达的低 MFE 区域。

以 spike CDS 为例：

- `Optimal-CAI`: **-1382.8 kcal/mol**, paired **63.1%**
- `lambda = 4`: **-2031.8 kcal/mol**, paired **75.3%**
- `lambda = 0`: **-2487.3 kcal/mol**, paired **83.6%**

这说明 MFE 优化能把序列推向更紧凑、更双链化的结构空间。
但作者也没有简单选择最低 MFE，而是保留了与 CAI 的折中。

### 关键结果 3：COVID-19 spike mRNA 的体外和体内验证很强

作者设计了 7 条 LinearDesign spike mRNA 序列 `A-G`，
并用 codon-optimized benchmark `H` 对照。

在 10 mM Mg2+ 缓冲液中：

- `A` 的半衰期为 **20.0 h**
- `H` 的半衰期为 **3.9 h**

在 HEK293 细胞蛋白表达中：

- `A` 相对 `H` 约 **2.9x**
- `D/G` 相对 `H` 约 **2.3x**

在小鼠免疫中：

- `A-D` 相对 `H` 的 anti-spike IgG 提升 **57x 到 128x**
- 中和抗体提升 **9x 到 20x**

这部分是全文最关键的证据：
算法设计出来的序列不是只在 MFE 上好看，而是能转化为稳定性、表达和免疫原性的提升。

### 关键结果 4：与 BNT-162b2 风格序列的 head-to-head 比较

作者还构造了一个接近 BNT-162b2 CDS 的对照序列，
但统一使用相同 UTR 和天然未修饰核苷酸。
结果显示 `A` 和 `C` 在体外稳定性、HEK293 蛋白表达和小鼠抗体诱导上均显著高于该 BNT 对照。

这里要注意解释边界：
这不是直接比较商业疫苗产品本身，
因为修饰核苷酸、递送体系、UTR 和抗原设计都被控制或改变了。
但它说明 CDS 结构优化本身可以提供强信号。

### 关键结果 5：VZV gE mRNA 证明方法不只适用于 spike

作者将方法扩展到 VZV gE 蛋白，并设计 `gE-A` 到 `gE-E`。

关键结果：

- `gE-A` 半衰期 **66.5 h**，而 `gE-Ther` 为 **10.9 h**
- 多数 LinearDesign 序列在 HEK293 表达上高于 `gE-Ther` 和 `gE-WT`
- `gE-B / gE-C / gE-E` 在小鼠中诱导显著更高 anti-gE IgG

有意思的是，最低 MFE 的 `gE-A` 并不是表达最佳。
表现最好的往往是 MFE 和 CAI 同时落在有利区域的序列。

这强化了一个设计原则：
**最稳定不等于最优，联合优化比单目标极值更可靠。**

### 我的结论

如果只用一句话评价这篇论文：

> LinearDesign 的真正贡献是把 mRNA CDS 设计从经验式 codon optimization 推进成了有形式化目标、有全局搜索能力、并经过体内验证的算法设计问题。

它是 mRNA 设计领域里非常典型的“算法思想直接改变实验候选空间”的工作。

## Limitations & Future Work

- **只优化 CDS，不直接优化 UTR**：UTR 工程仍然需要单独处理，后续更适合与 UTR 设计方法组合。
- **MFE 不是全部生物学**：MFE 与稳定性相关，但细胞内降解、翻译、免疫识别还受更多因素影响。
- **需要避免过长双链结构**：过度稳定的长茎结构可能触发 innate immune response，论文也通过约束避开了这类设计。
- **未纳入修饰核苷酸能量模型**：商业 mRNA 产品常用修饰核苷酸，未来需要对应的结构能量模型支持。
- **最佳设计通常是折中点**：VZV 实验说明最低 MFE 不一定对应最佳表达，后续应纳入更多多目标评价。

后续最值得看的方向是：

1. 将 `CDS stability / CAI / UTR / modified nucleotides` 放进统一优化框架。
2. 与生成模型结合，用实验反馈进一步校正多目标权重。
3. 从疫苗抗原扩展到抗体、细胞因子、酶替代等治疗性蛋白 mRNA。

## Notes

- 当前目录主图为 [1.png](./1.png) 到 [5.png](./5.png)，对应论文主文 Fig. 1 到 Fig. 5。
- `e1.png` 到 `e8.png` 为 Extended Data figures。
- 当前主文 PDF 为 [paper.pdf](./paper.pdf)。
