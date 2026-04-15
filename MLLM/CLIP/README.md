# CLIP

## Paper Info

- **Title**: Learning Transferable Visual Models From Natural Language Supervision
- **Authors**: Alec Radford, Jong Wook Kim, Chris Hallacy, Aditya Ramesh, Gabriel Goh, Sandhini Agarwal, Girish Sastry, Amanda Askell, Pamela Mishkin, Jack Clark, Gretchen Krueger, Ilya Sutskever
- **Venue**: ICML 2021 (PMLR 139)
- **ArXiv**: [2103.00020](https://arxiv.org/abs/2103.00020)
- **Paper**: [paper.pdf](./paper.pdf)
- **Code**: [openai/CLIP](https://github.com/OpenAI/CLIP)

## Motivation
这篇论文试图解决一个很直接但影响很大的问题：传统视觉模型高度依赖固定类别标签，
一旦任务类别变化，就需要重新标注、重新训练，泛化成本很高。

CLIP 的核心想法是把监督信号从“人工类别标签”切换到“互联网图文对”：
如果模型能直接学会“图像和自然语言描述是否匹配”，那么语言就可以作为通用接口，
在不额外训练分类头的前提下做零样本迁移。

一句话总结：CLIP 不是只想做一个更强的 ImageNet 分类器，
而是想把视觉模型变成“可被自然语言编程”的通用感知器。

## Method

作者的方法可以拆成五步：
1. **构建 WebImageText (WIT) 预训练数据**
   - 规模约 **4 亿** 图文对。
   - 用约 **50 万** 查询词覆盖广泛视觉概念，每个 query 最多取 2 万样本以缓解长尾失衡。
2. **双塔编码器**
   - 图像编码器：ResNet 或 ViT。
   - 文本编码器：Transformer。
   - 两个塔分别输出 embedding，再投影到同一语义空间并做 L2 归一化。
3. **对比学习目标**
   - 在一个 batch 内构造 `N x N` 图文相似度矩阵。
   - 最大化真实配对相似度，最小化错误配对相似度。
   - 使用图到文、文到图两个方向的对称交叉熵损失。
4. **零样本分类**
   - 把每个类别名写成文本提示词。
   - 计算图像和各类别文本 embedding 相似度，取最高者作为预测类别。
5. **模型扩展与训练**
   - 从 `RN50` 扩展到 `RN50x64`，以及 `ViT-B/32`、`ViT-B/16`、`ViT-L/14`。
   - 论文报告中最强模型为 `ViT-L/14@336px`。

核心训练形式可以概括为：

```text
logits = (I_e @ T_e.T) * exp(t)
loss   = (CE(logits, labels, axis=0) + CE(logits, labels, axis=1)) / 2
```

## Key Insights

### 关键结果
- 在 aYahoo / ImageNet / SUN 三个零样本基准上，CLIP 达到 **98.4 / 76.2 / 58.5**，
  明显高于早期 Visual N-Grams（72.4 / 11.5 / 23.0）。
- 在 27 个数据集的对比里，零样本 CLIP 在 **16/27** 个任务上超过
  “ResNet50 特征 + 线性分类器”的监督基线。
- 论文强调模型在自然分布偏移下更鲁棒：在 ImageNet 主集同精度前提下，
  对 ImageNetV2 / ImageNet-A / ImageNet-R / ObjectNet / ImageNet-Sketch
  有明显相对提升（文中给出的代表性增益为 +5.8%、+74.4%、+51.2%、+39.7%、+35.0%）。

### 为什么 CLIP 影响这么大

- 它把“类别标签空间”替换成“语言空间”，让视觉任务定义更灵活。
- 它证明了“互联网弱监督 + 对比学习 + 大规模训练”在视觉领域也成立，
  与 NLP 的 web-scale 预训练范式形成对应。
- 它提供了统一迁移接口：同一个预训练模型可以覆盖分类、检索、OCR、动作识别等多种任务。

### 我的结论

如果只用一句话评价这篇论文：

> CLIP 的真正贡献不是某个单点指标，而是把“用自然语言驱动视觉模型迁移”这件事做成了可复用范式。

这也是后续大多数视觉-语言模型（包括开放词汇检测、图文检索、VLM 对齐方案）
都在不同程度上继承 CLIP 思路的核心原因。

## Limitations & Future Work

论文自己给出的限制非常值得重视：
- **离真正 SOTA 仍有距离**：作者估计要达到其评测套件的全面 SOTA，
  可能还需要约 **1000x** 训练计算量，当前硬件下不可行。
- **严格零样本并不“纯”**：开发过程中仍会查询验证集表现做决策。
- **评测集可能有共适配风险**：27 个任务集合并非专门为广义零样本设计，
  结论存在 benchmark 选择偏差。
- **文本提示词敏感**：自然语言接口很灵活，但复杂任务难以只靠 prompt 精确定义。
- **偏差与安全问题**：文中展示了标签集合变化会显著改变有害分类率
  （如某设置下 32.3%，加入 `child` 后降到 8.7%），并讨论了隐私/监控风险。

我认为后续最值得追的方向是：

1. 提升数据与训练效率，降低 web-scale 预训练门槛。
2. 让“零样本到少样本”过渡更平滑，减少 few-shot 反直觉性能下降。
3. 强化偏差评估与安全约束，把“可用”变成“可控可审计”。

