# GEMORNA

## Paper Info

- **Title**: Deep generative models design mRNA sequences with enhanced translational capacity and stability
- **Authors**: He Zhang, Hailong Liu, Yushan Xu, Haoran Huang, Yiming Liu, Jia Wang, Yan Qin, Haiyan Wang, Lili Ma, Zhiyuan Xun, Xuzhuang Hou, Timothy K. Lu, Jicong Cao
- **Venue**: Science, **390**, eadr8470 (2025-11-06)
- **DOI**: [10.1126/science.adr8470](https://doi.org/10.1126/science.adr8470)
- **Paper**: [paper.pdf](./paper.pdf)

## Motivation

这篇论文聚焦一个很现实的瓶颈：mRNA 疗法已经被验证可行，但很多场景仍受限于
“表达强度不够高、持续时间不够长”。

传统优化方法往往只优化局部指标（如 CAI、GC 含量、局部结构等），
或者依赖“预测模型 + 遗传算法”做间接搜索，容易卡在局部最优。
作者想解决的问题是：能不能直接用生成模型在巨大序列空间里一次性生成
高表达、长持续、可用于治疗场景的 mRNA 序列。

一句话总结：GEMORNA 想把 mRNA 设计从“手工规则优化”推进到“端到端生成设计”。

## Method

作者把完整 mRNA 设计拆成三个层次：CDS 生成、UTR 生成、全长组合验证。
1. **GEMORNA-CDS（编码区）**
   - 使用 Transformer **encoder-decoder** 架构。
   - 把“蛋白序列 -> CDS 序列”建模成类似机器翻译任务：
     encoder 表征蛋白语义，decoder 生成满足氨基酸约束的密码子序列。
   - 推理时支持 sampling / greedy / beam search，不同采样偏置会影响 CAI 等性质。

2. **GEMORNA-UTR（非编码区）**
   - 使用 Transformer **decoder-only** 架构，更适合 de novo 生成 UTR。
   - 先在天然 UTR 上预训练，再用高 MRL 的 5'UTR 和高稳定性的 3'UTR 做微调。
   - 目标是让生成 UTR 既保持生物合理性，又能朝高翻译效率/高稳定性方向偏移。

3. **全长 mRNA 组合与实验闭环**
   - 将 AI 生成的 5'UTR + CDS + 3'UTR 组合成 full-length mRNA。
   - 在细胞与小鼠中做表达强度、表达持续性、免疫原性等验证。
   - 同样扩展到 circRNA（环状 RNA）设计，并在 CAR-T 场景测试功能效果。

### 论文里给出的关键训练规模

- CDS 训练集：超过 **100 万** 蛋白-CDS 对，来自 **115** 个哺乳动物物种。
- UTR 预训练集：约 **800 万** 5'UTR + **200 万** 3'UTR。
- UTR 微调集：约 **80 万** 5'UTR + **20 万** 3'UTR。

### 论文里给出的模型配置（方法学细节）

- GEMORNA-CDS：12 层 encoder + 12 层 decoder，8 头注意力，hidden size 128。
- GEMORNA-UTR：12 层 decoder、12 头注意力；5'UTR hidden 144，3'UTR hidden 288。

## Key Insights

### 关键结果 1：CDS/UTR 不是“只像天然序列”，而是“可控地更强”

- 在报告基因（Fluc）实验中，AI 生成 CDS 对比 biLSTM-CRF 方案可达 **20-fold** 提升，
  对比商业载体序列（pGL4.11）可达 **4.8-fold** 提升（48h）。
- 生成 UTR 与天然 UTR 具有较低同源性，但性能可持续优于多种 benchmark（含商业产品）。
### 关键结果 2：全长 mRNA 的收益比“单模块优化”更显著

- 在全长 Fluc mRNA 上，最佳 GEMORNA 设计相对 benchmark 可达 **41-fold** 表达提升。
- 同一模块在不同细胞条件下仍保持优势（文中给出 HepG2 约 **15.9-fold** 提升）。

这说明作者不是只把某一段序列做强，而是把 5'UTR/CDS/3'UTR 联合设计后得到系统级收益。

### 关键结果 3：治疗场景验证是这篇文章最硬的部分

- COVID-19 mRNA 疫苗任务中，文中报告抗体滴度约为 BNT162b2 的 **2 倍**。
- EPO 治疗 mRNA 构建体在不同设置下达到 **15- to 150-fold** 的表达提升。

这使结果不再停留在“体外指标漂亮”，而是走向了更接近药物开发的验证层级。

### 关键结果 4：平台可扩展到 circRNA 和细胞治疗场景

- circRNA-EPO 在体外累计表达可达 **13.8-fold** 提升；在小鼠体内可见最高约 **121-fold** 提升。
- CD19 CAR circRNA 在人原代 T 细胞中，24h 表达可达 benchmark 的 **28-fold**（另一基线约 **5.6-fold**），
  且 CAR 阳性持续时间更长。

### 我的结论

如果用一句话评价这篇工作：

> GEMORNA 的关键贡献不是“又一个 RNA 语言模型”，而是把可生成、可组合、可实验闭环验证的 mRNA 设计流程真正打通了。

它把“生成式 AI 在生物序列设计中的价值”从概念验证推进到更工程化、可转化的层面。

## Limitations & Future Work

作者在 Discussion 里给出的限制很实在：

- **数据瓶颈**：模型还可以从更多“外源序列表达/稳定性高通量数据”中受益。
- **可解释性不足**：深度学习模型仍偏黑盒，隐式学到的机制难直接解释。
- **场景专用化空间**：可继续做组织/疾病特异模型，提升临床应用针对性。

我认为后续最关键的三件事是：

1. 把模型训练与更系统的湿实验主动学习闭环结合，持续提升命中率。
2. 在免疫原性、安全性、制造约束等真实开发指标上做多目标联合优化。
3. 提升机制可解释性，让“为什么这条序列更优”能被实验机制反向验证。

