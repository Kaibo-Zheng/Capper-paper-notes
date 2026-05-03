# RT-2

## Paper Info

- **Title**: RT-2: Vision-Language-Action Models Transfer Web Knowledge to Robotic Control
- **Authors**: Anthony Brohan, Noah Brown, Justice Carbajal, Yevgen Chebotar, Xi Chen, Krzysztof Choromanski, Tianli Ding, Danny Driess, Avinava Dubey, Chelsea Finn, et al.
- **Venue**: CoRL 2023
- **Project**: [robotics-transformer2.github.io](https://robotics-transformer2.github.io/)
- **Paper**: [paper.pdf](./paper.pdf)

## Abstract

`RT-2` 是一篇把大规模 vision-language model 直接改造成机器人闭环控制策略的代表性工作。
它不把 VLM 只当作高层 planner 或 object recognizer，而是让模型直接输出低层 robot action。

一句话总结：
`RT-2` 的核心是把机器人动作离散化成 text tokens，让 web-scale VQA/vision-language 数据和 robot trajectory 数据进入同一个序列建模框架，从而把 VLM 的语义知识迁移到机器人控制中。

## Motivation

机器人学习长期面临一个现实矛盾：

- 真实机器人交互数据昂贵，远远达不到互联网图文数据的规模。
- 大型 VLM 已经从 web-scale 数据中学到丰富的物体、语言、视觉和常识知识。
- 但传统做法通常只把 VLM 放在高层规划或语义识别位置，底层控制仍由单独策略完成。

论文想回答的问题是：

> 能不能把 VLM 直接纳入低层闭环控制，让同一个模型既理解视觉语言语义，又能输出机器人动作？

这也是 `RT-2` 和很多早期 language-to-robot pipeline 的区别：它不是“语言模型规划，控制器执行”的两段式系统，而是把 action 本身也放进 token space 里联合训练。

## Method

### 1. Vision-Language-Action Formulation

`RT-2` 把机器人控制看成一种特殊的语言生成任务。
输入是图像和自然语言指令，输出不是普通文本，而是表示机器人动作的 token 序列。

动作包括：

- end-effector 位置位移
- 旋转位移
- gripper extension
- episode termination command

连续动作维度被离散化成 token，模型生成后再 de-tokenize 回机器人控制命令。

### 2. Co-Fine-Tuning

训练时，作者不是只用机器人数据微调 VLM，而是做 co-fine-tuning：

- robot trajectory data：图像、指令、动作 token
- Internet-scale vision-language tasks：例如 VQA、image-text reasoning

这样做的目的很明确：
既要让模型学会动作输出格式，又要避免只在有限 robot data 上微调导致 web-scale 语义能力退化。

### 3. Model Backbones

论文基于已有大型 VLM 构造 VLA：

- `RT-2-PaLI-X`
- `RT-2-PaLM-E`

关键点是：RT-2 尽量复用已有 VLM 参数和预训练能力，而不是从零设计一个新的机器人专用多模态架构。

### 4. Chain-of-Thought for Robotic Reasoning

论文还展示了带 chain-of-thought prompt 的 RT-2。
模型可以先生成中间推理文本，再生成动作 token。
例如根据“累了的人适合喝什么”推断应该拿 energy drink，或根据“临时锤子”推断应该拿 rock。

这说明 RT-2 的一部分能力来自语言模型已有的语义推理，而不是单纯从 robot demonstrations 中学到。

## Key Insights

### 关键结果 1：动作 token 化把 VLM 和 robot policy 接到了同一个接口

RT-2 最重要的设计不是复杂控制结构，而是把 action 表示成 token。
这样自然语言回答和机器人动作都变成序列输出，VLM 的 decoder 可以同时服务两类任务。

这个选择带来的好处是工程上非常直接：

- 不需要给机器人动作单独加专用 head。
- 可以使用现有 VLM 的训练和推理框架。
- 可以把语言任务和动作任务混在同一训练数据里。

### 关键结果 2：web knowledge 能迁移到低层控制

论文报告 RT-2 在 seen tasks 上保持和 RT-1 相近或更好的表现，同时在 unseen objects、unseen backgrounds、unseen environments 上有明显提升。
原文总结中指出，RT-2 在多种 generalization evaluation 上相对最强 baseline 有约 `2x` 提升，相对更弱 baseline 可达到约 `6x`。

这说明模型不只是记住了机器人数据里的物体和指令，而是能利用 VLM 预训练中学到的视觉语义知识。

### 关键结果 3：出现了 robot data 中没有直接标注的语义行为

RT-2 能执行一些需要语义理解的指令，例如：

- 把物体放到指定数字或图标上。
- 拿起最小或最大的物体。
- 选择和其他物体不同的对象。
- 根据关系或常识选择目标。

这些能力不是单纯的运动泛化，而是语义条件下的技能重组。
这也是论文把它称作 emergent capabilities 的原因。

### 关键结果 4：模型规模和 co-fine-tuning 都很关键

消融实验显示，直接从头训练或只用 robot data 都不如利用大型 VLM 并进行 co-fine-tuning。
更大的模型通常带来更强的 generalization，说明 VLA 的能力不仅来自机器人数据，也来自 web-scale pretraining 的语义容量。

### 关键结果 5：RT-2 仍然受限于机器人动作分布

论文也指出，RT-2 对超出 robot data 的新运动模式仍然不稳，例如擦拭、复杂工具使用或新的物体动力学。
换句话说，web-scale VLM 可以迁移语义知识，但不能凭空学会没有数据支撑的物理控制技能。

### 我的结论

如果只用一句话评价 RT-2：

> RT-2 的意义在于把 VLM 从机器人系统的高层语义模块推进到底层闭环策略本身，证明 web-scale 视觉语言预训练可以通过 action tokenization 迁移到真实机器人控制。

它是 VLA 路线的关键节点：在 RT-1 的机器人 transformer 基础上，RT-2 进一步证明“机器人动作也可以成为语言模型的输出空间”。

## Limitations & Future Work

- **动作能力受 robot data 限制**：模型可以重组语义，但新运动技能仍需要真实机器人数据支持。
- **低层控制精度有限**：离散化 action token 简洁统一，但也带来动作分辨率和实时控制约束。
- **推理成本高**：大型 VLM 做闭环控制需要满足机器人实时性，对部署系统要求高。
- **失败模式仍明显**：对 unseen object dynamics、复杂接触、工具使用等场景泛化不足。
- **语义推理不等于物理理解**：模型能回答或推理某些常识，不代表能稳定执行对应物理操作。
- **数据闭环还不完整**：RT-2 主要展示预训练迁移和联合微调，还不是部署后持续自我改进的 RL 系统。

后续值得关注的方向包括：

1. 更大规模、更开放的 robot trajectory 数据。
2. 更高频、更精细的 action representation。
3. 将 VLA 与真实世界 RL / intervention learning 结合。
4. 让模型显式建模失败恢复、接触动力学和长期任务状态。
5. 降低推理成本，让大型 VLA 更容易部署在真实机器人系统中。

## Reproduction Notes

复现或复刻 RT-2 思路时，需要优先确认：

- 机器人动作空间如何离散化成 token。
- robot trajectory 数据和 VQA/web 数据的混合比例。
- 是否保留 VLM 的原始语言/视觉任务来避免能力遗忘。
- 推理时 action token 如何 de-tokenize 成控制命令。
- 控制频率、延迟和模型推理速度是否满足闭环要求。
- 评估是否区分 seen tasks、unseen objects、unseen backgrounds、unseen environments 和 emergent skill tasks。

这篇工作难点不在“把动作写成 token”这个想法本身，而在大规模 VLM、机器人数据、实时控制系统和评估协议的整体工程闭环。
