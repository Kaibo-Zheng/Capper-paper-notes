# AI Scientist

## Paper Info

- **Title**: Towards end-to-end automation of AI research
- **Authors**: Chris Lu, Cong Lu, Robert Tjarko Lange, Yutaro Yamada, Shengran Hu, Jakob Foerster, David Ha, Jeff Clune
- **Venue**: Nature 2026, Volume 651
- **Date**: 2026-03-25
- **DOI**: [10.1038/s41586-026-10265-5](https://doi.org/10.1038/s41586-026-10265-5)
- **Paper**: [paper.pdf](./paper.pdf)
- **Code**:
  - [SakanaAI/AI-Scientist](https://github.com/SakanaAI/AI-Scientist)
  - [SakanaAI/AI-Scientist-v2](https://github.com/SakanaAI/AI-Scientist-v2)

## Motivation

这篇论文讨论的不是某个具体科学任务，而是一个更大的问题：
能不能把 AI research 的完整流程自动化。

过去的 AI 系统已经能帮助完成很多局部任务，
例如生成 hypothesis、写 literature review、实现代码、分析实验结果，
但这些能力通常是分散的。
真正困难的是让一个系统从选题、查新、实验、写作到审稿形成闭环。

一句话总结：
`The AI Scientist` 试图把机器学习研究变成一个端到端 agent workflow，
让 AI 自动提出 idea、写代码、跑实验、画图、写论文，并用自动审稿器评估结果。

## Method

论文中的系统可以拆成两个核心组件：

1. **The AI Scientist**
   - 自动生成研究方向和 hypothesis。
   - 调用 Semantic Scholar 和 web search 做 novelty checking。
   - 写实验代码、运行实验、记录结果和错误。
   - 生成 plots，并用 VLM 检查图表质量。
   - 根据实验日志和图表写完整 LaTeX 论文。

2. **The Automated Reviewer**
   - 模拟 NeurIPS 风格审稿流程。
   - 对论文给出 soundness、presentation、contribution、overall score 和 confidence。
   - 输出 strengths、weaknesses、questions、ethical concerns 和 accept/reject decision。
   - 使用 **5-run ensemble**，再让模型扮演 area chair 汇总 meta-review。

作者评估了两种 AI Scientist 模式：

### Template-based

系统从人类提供的代码模板开始，
例如一个能复现基础训练流程的已有 codebase。
AI 在此基础上提出改动、实现实验、调参、做 ablation、写论文。

这种模式更稳定，但探索空间受初始模板限制。

### Template-free

系统不依赖固定起始代码库，
而是从更抽象的研究 proposal 出发，
通过 agentic tree search 组织实验探索。

其流程包括四个阶段：

1. preliminary investigation
2. hyperparameter tuning
3. research agenda execution
4. ablation studies

每个 stage 内部用并行树搜索扩展实验节点，
再由 LLM evaluator 选择最有前途的节点进入下一阶段。

## Key Insights

### 关键结果 1：完整研究流程被组织成一个可运行的 agent pipeline

Fig. 1 的重要性在于，它不是展示单个强 prompt，
而是展示一个多阶段研究系统：

```text
Ideation -> Experimentation -> Write-up -> Paper AI review
```

实验阶段又进一步拆成 preliminary investigation、hyperparameter tuning、
main research execution 和 ablation studies。

我的理解是：
这篇论文真正讨论的不是“LLM 会不会写论文”，
而是如何把研究过程拆成可以被 agent 执行、检查和迭代的工程系统。

### 关键结果 2：Automated Reviewer 与人类审稿一致性达到可比较水平

作者用 OpenReview 中的 ICLR 论文数据评估自动审稿器，
并与 NeurIPS 2021 human reviewer consistency 做比较。

在 2017-2024 数据上：

- balanced accuracy: **0.69 ± 0.04**
- F1: **0.62 ± 0.09**
- AUC: **0.69 ± 0.09**

在 2025 cutoff 之后的数据上：

- balanced accuracy: **0.66 ± 0.03**
- F1: **0.67 ± 0.09**
- AUC: **0.65 ± 0.10**

这个结果说明 Automated Reviewer 至少可以作为大规模自动评估的 proxy。
但它仍然不是可靠替代人类审稿的最终裁判，
因为它可能继承模型偏差、审稿噪声和论文表述风格偏好。

### 关键结果 3：生成论文质量随基础模型进步而提升

论文用 Automated Reviewer 评价不同底座模型生成的 AI Scientist papers。
结果显示，paper score 与模型发布时间存在显著正相关：

- `R^2 = 0.517`
- `P < 0.00001`

这意味着 The AI Scientist 的能力很大程度受底座模型限制。
随着 foundation model 变强，同一个 agent scaffold 也会自然变强。

这点是论文里最值得关注的趋势判断：
当前系统还不稳定，但它处在一个可能随模型能力快速抬升的轨道上。

### 关键结果 4：test-time compute 能提高研究质量

Fig. 3 展示了 template-free 模式下 agentic tree search 的 compute scaling。
当实验节点数增加时，Automated Reviewer 给出的 paper score 也提升。

这说明研究自动化不只是“换一个更强模型”，
还包括如何把更多 inference-time compute 转化为更好的实验搜索。

换句话说，未来 AI research agent 的能力可能同时来自两条路线：

- 更强底座模型
- 更深、更宽、更会剪枝的研究搜索过程

### 关键结果 5：ICLR workshop 真实 peer review 实验是全文最强证据

作者在获得 ICLR 2025 领导层、ICBINB workshop 组织者和 IRB 批准后，
将 3 篇 template-free AI Scientist 生成论文提交到 workshop peer review。

关键设定：

- workshop 是 ICLR 2025 的 `I Can't Believe It's Not Better`。
- 审稿人被告知有少量 AI-generated submissions，但不知道具体是哪篇。
- 3 篇 AI 论文进入 43 篇 workshop 投稿中。
- 整个科学流程从 ideation、coding 到 manuscript writing 没有人类修改。

结果：

- 其中一篇平均分 **6.33**，单项分数为 **6 / 7 / 6**。
- 该论文超过 workshop 平均接收阈值。
- 组织者表示，如果不是按预设协议撤稿，该论文大概率会被接收。
- 该 workshop 接收率约 **70%**，而 ICLR 2025 主会接收率约 **32%**。

这不是说 AI Scientist 已经达到顶会主会水平。
但它证明了一个重要里程碑：
完全 AI 生成的机器学习研究论文已经可以通过较低门槛但真实的 peer review。

### 关键结果 6：当前系统的失败模式仍然很明显

论文非常明确地列出了问题：

- idea 过于 naive 或发展不充分
- 方法严谨性不足
- 实验实现错误
- 图表重复或展示质量问题
- citation hallucination
- 论文写作中存在事实或格式错误
- workshop 级别可以偶尔过线，但还达不到主会论文标准

作者团队内部评估也认为：
虽然一篇论文达到了 workshop bar，
但三篇都没有达到 ICLR main conference bar。

这点很关键。
这篇论文不是在宣称“AI 已经能替代 AI researcher”，
而是在证明端到端自动化研究开始变成可实测、可扩展的问题。

### 我的结论

如果只用一句话评价这篇论文：

> AI Scientist 的意义不在于生成了一篇 workshop 级论文，而在于把“自动做研究”从演示性 prompt 推进成了可以执行、评估、扩展并接受真实 peer review 检验的 agent pipeline。

它更像一个研究自动化平台雏形，
而不是一个已经成熟的 autonomous scientist。

## Limitations & Future Work

这篇论文的边界很重要：

- **当前只覆盖计算型 ML research**：实验都能在计算机上完成，离自动化湿实验科学还有距离。
- **论文质量不稳定**：3 篇投稿只有 1 篇过 workshop bar，且未达到主会标准。
- **仍有人类筛选介入**：虽然最终论文没有人工修改，但作者在生成过程中手动筛选了最有希望的输出。
- **Automated Reviewer 不是最终真值**：它适合大规模比较，但不能替代真实同行评议。
- **存在学术生态风险**：可能加重审稿负担、制造低质量论文、滥用他人想法、虚增科研履历。
- **安全风险未完全解决**：如果扩展到化学、生物或工程实验，自动化 agent 可能设计危险实验。

后续值得追的方向：

1. 建立明确的 AI-generated research disclosure 和审稿规范。
2. 将 automated reviewer 与人类专家反馈结合，而不是完全替代人类。
3. 改进实验实现验证，减少代码错误和 hallucination。
4. 从 ML 计算实验扩展到可控、安全的自动化实验平台。
5. 研究如何让 agent 产生真正深层的新概念，而不是局部 incremental idea。

## Notes

- 当前主文 PDF 为 [paper.pdf](./paper.pdf)。
- 本文更适合归入 `Agents / Research Automation`，而不是 `AI4S` 下的具体科学建模方向。
