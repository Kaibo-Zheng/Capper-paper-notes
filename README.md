# Capper's Paper Notes

A structured collection of research notes on vision-language models, vision-language-action / embodied AI, AI agents, NLP, and AI for Science, with personal insights and critical analysis.

## Categories

| Category | Description |
|----------|-------------|
| **Multimodal Large Language Models (MLLMs)** | Research on large language models and their multimodal extensions, including scaling laws, vision-language alignment, representation learning, and generation. |
| **Vision-Language-Action / Embodied AI** | Research on agents that perceive, reason, and act in physical or simulated environments, including robotics, manipulation, navigation, and VLA systems. |
| **AI Agents / Research Automation** | Research on autonomous agents, agentic workflows, tool use, automated experimentation, and research automation systems. |
| **AI for Science (AI4S)** | Research on applying AI to scientific discovery, currently organized around nucleic acid and protein modeling/design. |
| **Natural Language Processing (NLP)** | Research on language modeling, sequence transduction, machine translation, and other core NLP methods and systems. |
| **Research Practice** | Notes on research workflow, academic writing, collaboration, and day-to-day execution. |

## Note Format

Each note should ideally include:

- **Paper Info**: title, authors, venue, year, and links
- **Abstract**: the original abstract or a concise summary in your own words
- **Motivation**: what problem the paper is trying to solve
- **Method**: a high-level summary of the core approach
- **Key Insights**: personal understanding, takeaways, and critical analysis
- **Limitations & Future Work**: weaknesses, open questions, and possible extensions

## Research Practice

> 来源：曾哥会议记录。这里整理为科研方法论备忘，作为读论文、做实验、写论文之外的通用工作准则。

### 科研特性

- 好奇心
- 自驱力
- 洞察力
- 坚持
- 努力
- 卷

### 科研能力

- 代码能力
- 英语阅读
- 抗压能力
- 数理基础
- 归纳总结
- 辩证能力
- 创新思维
- 实践能力
- 写作能力
- 持续学习

### 科研步骤

1. 选定方向。
2. 阅读文章。
3. 寻找 idea：大胆猜测，小心求证。
4. 实验验证。
5. 写文章投稿。

### 科研目标

- 顶会。
- 顶刊。

### 学术写作规则

- 写作目的：接受。
- 写作要讲究效率。

### 论文结构

论文的基本结构通常包括：

- title
- abstract
- introduction
- related work
- proposed method
- experiment

写作和实验展示时重点关注：

- 模型性能。
- 推理速度。
- 总结好的词汇和表达。
- 期刊摘要可以长一些。
- 多参考最佳论文，尤其是 oral 论文。

### 日常工作节奏

- 早起罗列小任务。
- 上午做输入型工作。
- 下午做产出型工作。
- 睡前复盘。

### 如何寻找 Idea

基本路径：

1. 发现问题。
2. 设计方案。
3. 进行实验。

注意：完成上一步之前，不应该开始下一步。

### 研究方法提醒

- 做 survey。
- 从树中总结规律。

> 纸上得来终觉浅，绝知此事要躬行。

## Reading List

> TODO: keep expanding this list.

### Multimodal Large Language Models

| Paper | Venue | Note |
|-------|-------|------|
| GAN | NeurIPS 2014 | [MLLM/GAN](./MLLM/GAN/README.md) |
| Transformer | NeurIPS 2017 | [MLLM/Transformer](./MLLM/Transformer/README.md) |
| RAG | NeurIPS 2020 | [MLLM/RAG](./MLLM/RAG/README.md) |
| CLIP | ICML 2021 | [MLLM/CLIP](./MLLM/CLIP/README.md) |
| Densing Law of LLMs | Nature Machine Intelligence 2025 | [MLLM/DensingLaw](./MLLM/DensingLaw/README.md) |

### Vision-Language-Action / Embodied AI

| Paper | Venue | Note |
|-------|-------|------|
| pi0.6 | arXiv 2025 | [VLA/pi0.6](./VLA/pi0.6/README.md) |

### AI Agents / Research Automation

| Paper | Venue | Note |
|-------|-------|------|
| ReAct | ICLR 2023 | [Agents/ReAct](./Agents/ReAct/README.md) |
| AI Scientist | Nature 2026 | [Agents/AI-Scientist](./Agents/AI-Scientist/README.md) |

### AI for Science

#### Nucleic Acid

Ordered roughly from earlier to later work.

| Paper | Venue | Note |
|-------|-------|------|
| LinearDesign | Nature 2023 | [AI4S/NucleicAcid/LinearDesign](./AI4S/NucleicAcid/LinearDesign/README.md) |
| UTR-LM | Nature Machine Intelligence 2024 | [AI4S/NucleicAcid/UTR-LM](./AI4S/NucleicAcid/UTR-LM/README.md) |
| mRNABERT | Nature Communications 2025 | [AI4S/NucleicAcid/mRNABert](./AI4S/NucleicAcid/mRNABert/README.md) |
| mRNA2vec | AAAI 2025 | [AI4S/NucleicAcid/mRNA2vec](./AI4S/NucleicAcid/mRNA2vec/README.md) |
| CodonFM | Preprint 2025 | [AI4S/NucleicAcid/CodonFM](./AI4S/NucleicAcid/CodonFM/README.md) |
| GEMORNA | Science 2025 | [AI4S/NucleicAcid/GEMORNA](./AI4S/NucleicAcid/GEMORNA/README.md) |
| DNA-Diffusion | Nature Genetics 2026 | [AI4S/NucleicAcid/DNA-Diffusion](./AI4S/NucleicAcid/DNA-Diffusion/README.md) |
| RMSAGen | AAAI 2026 | [AI4S/NucleicAcid/RMSAGen](./AI4S/NucleicAcid/RMSAGen/README.md) |
| SOLD | AAAI 2026 | [AI4S/NucleicAcid/SOLD](./AI4S/NucleicAcid/SOLD/README.md) |

#### Protein

Ordered roughly from earlier to later work.

| Paper | Venue | Note |
|-------|-------|------|
| HEAL | Bioinformatics 2023 | [AI4S/Protein/HEAL](./AI4S/Protein/HEAL/README.md) |
| GOBoost | Bioinformatics 2025 | [AI4S/Protein/GOBoost](./AI4S/Protein/GOBoost/README.md) |

### Natural Language Processing

| Paper | Venue | Note |
|-------|-------|------|
| Seq2Seq | NeurIPS 2014 | [NLP/Seq2Seq](./NLP/Seq2Seq/README.md) |

## License

[MIT](./LICENSE)
