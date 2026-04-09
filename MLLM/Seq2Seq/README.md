# Seq2Seq (2014)

## Paper Info

- **Title**: Sequence to Sequence Learning with Neural Networks
- **Authors**: Ilya Sutskever, Oriol Vinyals, Quoc V. Le
- **Venue**: NeurIPS 2014 (Advances in Neural Information Processing Systems 27)
- **ArXiv**: [1409.3215](https://arxiv.org/abs/1409.3215)
- **Paper**: [paper.pdf](./paper.pdf)

## Motivation

这篇论文要解决的是一个当时非常关键的问题：
传统 DNN 更适合固定维度输入输出，但机器翻译这类任务是“变长序列 -> 变长序列”，
很难直接套用。

作者的目标是给出一个尽量通用、端到端、尽量少任务先验假设的序列映射框架，
让模型自己学习从输入序列编码语义，再解码成目标序列。

一句话总结：这篇工作把“序列到序列学习”从特定技巧推进成了可复用的统一范式。

## Method

核心架构是经典的 **Encoder-Decoder**：

1. 用一个深层 LSTM 编码输入序列，得到固定长度向量表示。
2. 用另一个深层 LSTM 基于该向量逐步解码目标序列。
3. 用左到右 beam search 进行推理解码。

### 关键工程配置（论文原文）

- Deep LSTM：**4 层**，每层 **1000 cells**，词向量维度 **1000**。
- 词表：源语言 **160,000**，目标语言 **80,000**，OOV 统一映射为 `UNK`。
- 训练：SGD（无 momentum），初始学习率 **0.7**，总计 **7.5 epochs**，batch **128**。
- 使用梯度范数裁剪（阈值为 5）稳定训练。

### 这篇论文最有名的技巧

- **源序列反转（reverse source sentence）**：
  只反转源句词序，不反转目标句。作者发现这会显著优化训练难度，
  因为它在源端与目标端之间引入更多短程依赖，帮助 SGD 更快建立对齐关系。

## Key Insights

### 关键结果 1：直接翻译已经超过当时强 SMT 基线

- WMT14 英法翻译任务上：
  - SMT baseline：**33.30 BLEU**
  - 单个 forward LSTM（beam=12）：**26.17**
  - 单个 reversed LSTM（beam=12）：**30.59**
  - 5 个 reversed LSTM ensemble（beam=12）：**34.81**

这说明“深层神经网络端到端翻译”首次在强基线面前显示出明确竞争力。

### 关键结果 2：与 SMT 结合的重排序效果更强
- 对 baseline 的 1000-best 做重排序：
  - single forward LSTM：**35.61**
  - single reversed LSTM：**35.85**
  - 5 个 reversed LSTM ensemble：**36.5**
- 当时文中引用的 SOTA 约 **37.0**，说明神经方法已非常接近最强传统系统。

### 关键结果 3：反转源序列带来“超高性价比”提升

- 反转后，测试 perplexity 从 **5.8 -> 4.7**。
- 直接解码 BLEU 从 **25.9 -> 30.6**。

这几乎是整篇论文最有影响力的训练技巧之一，后续很多早期 NMT 实践都直接沿用。

### 关键结果 4：长句性能并未明显崩塌

- 文中显示对长句的性能退化并不严重，
  尤其在 35 词以内基本没有明显下降。
- 这在当时对“RNN 难处理长依赖”的普遍担忧下，是非常重要的经验结论。

### 我的结论

如果只看一句话：

> Seq2Seq 2014 的历史意义不在于“最终分数碾压”，而在于它把 Encoder-Decoder 变成了后续神经生成模型的标准接口。

包括后来的 attention、Transformer、以及多模态生成框架，本质上都在这个接口上演进。

## Limitations & Future Work

从今天回看，这篇论文也有很清晰的局限：

- **固定长度瓶颈**：把整句压到单个向量，再解码，长句信息容易损失。
- **词级词表 + UNK**：对 OOV 和稀有词处理较弱。
- **计算成本高**：单模型约 380M 参数，ensemble 成本更高。
- **缺少显式对齐机制**：还没有 attention，解释性与细粒度对齐能力有限。

我认为这篇工作后续最自然的三条演进路径（也基本成为了历史事实）：

1. 引入 attention，缓解固定向量瓶颈。
2. 引入子词建模（BPE/SentencePiece）降低 OOV 问题。
3. 用更并行、更稳定的架构（Transformer）替代纯 RNN 编解码。
