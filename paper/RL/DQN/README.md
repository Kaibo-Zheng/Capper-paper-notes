# DQN

## Paper Info

- **Title**: Human-level control through deep reinforcement learning
- **Authors**: Volodymyr Mnih, Koray Kavukcuoglu, David Silver, Andrei A. Rusu, Joel Veness, Marc G. Bellemare, Alex Graves, Martin Riedmiller, Andreas K. Fidjeland, Georg Ostrovski, Stig Petersen, Charles Beattie, Amir Sadik, Ioannis Antonoglou, Helen King, Dharshan Kumaran, Daan Wierstra, Shane Legg, Demis Hassabis
- **Venue**: Nature 2015
- **DOI**: [10.1038/nature14236](https://doi.org/10.1038/nature14236)
- **Paper**: [paper.pdf](./paper.pdf)

## Abstract

这篇文章提出 **Deep Q-Network (DQN)**，目标是让强化学习智能体直接从高维视觉输入中学习控制策略。它把经典 Q-learning 和深度卷积神经网络结合起来：CNN 从 Atari 游戏画面中提取状态表示，并输出每个可选动作的 Q 值；智能体再选择估计回报最高的动作。

核心贡献不是“会玩某一个游戏”，而是证明同一套端到端算法、网络结构和超参数，可以只依赖像素和游戏分数，在 49 个 Atari 2600 游戏上学到强策略。DQN 在 43 个游戏上超过此前最好的强化学习方法，并在 29 个游戏上达到超过人类测试员 75% 的归一化分数。

一句话总结：DQN 把“从原始像素到动作”的强化学习管线做通了，是深度强化学习从概念走向可用系统的标志性工作。

## Motivation

DQN 之前，强化学习在复杂环境中主要卡在两个问题上：

- **状态表示难**：传统 Atari 强化学习方法往往依赖手工特征，或者只适用于低维、完全可观测状态。
- **神经网络训练不稳定**：Q-learning 使用非线性函数近似器时容易发散，因为样本序列强相关、策略更新会改变数据分布、Q 值和 TD target 又互相耦合。

论文想解决的问题是：

> 能不能让一个智能体只看屏幕像素和奖励信号，就自动学出可用的视觉表示和动作策略？

这也是它的历史意义：DQN 不是单纯换了一个更大的函数近似器，而是给出了一个足够稳定的训练配方，让深度网络可以和 off-policy temporal-difference learning 结合。

## Method

### 1. 强化学习目标

智能体在每一步观察图像 `s_t`，选择动作 `a_t`，得到奖励 `r_t`。目标是最大化折扣累计回报：

```text
R_t = r_t + gamma * r_{t+1} + gamma^2 * r_{t+2} + ...
```

DQN 学习动作价值函数：

```text
Q(s, a) = taking action a at state s 后，未来能获得的最大期望折扣回报
```

训练时使用 Bellman target：

```text
y = r + gamma * max_a' Q_target(s', a')
```

然后最小化当前网络预测值和 target 之间的 TD error：

```text
Loss = (y - Q(s, a))^2
```

如果 `s'` 是终止状态，则 target 只取 `r`。

### 2. 输入预处理

Atari 原始输入是 `210 x 160` 彩色视频，DQN 做了几步统一预处理：

- 取当前帧和上一帧的逐像素最大值，缓解 Atari sprite 闪烁问题。
- 提取亮度通道并缩放到 `84 x 84`。
- 堆叠最近 `4` 帧，形成 `84 x 84 x 4` 输入，让网络能感知速度和运动方向。
- 使用 frame skipping / action repeat，智能体每隔若干帧选择一次动作，中间重复上一个动作。

这一步很关键：单帧图像不足以判断球、敌人或子弹的运动方向，4 帧堆叠是用简单工程方式补上部分可观测性。

### 3. Q-network 架构

网络输入是 `84 x 84 x 4`，输出是每个合法动作对应的 Q 值。这样一次 forward pass 就能得到所有动作价值，不需要对每个动作单独跑一遍网络。

```text
Input: 84 x 84 x 4
Conv1: 32 filters, 8 x 8, stride 4, ReLU
Conv2: 64 filters, 4 x 4, stride 2, ReLU
Conv3: 64 filters, 3 x 3, stride 1, ReLU
FC:    512 units, ReLU
Output: one scalar Q-value per valid action
```

不同游戏的动作数不同，论文里的有效动作数在 `4` 到 `18` 之间。

### 4. 稳定训练的两个核心机制

#### Experience Replay

DQN 把交互得到的转移存进 replay memory：

```text
(state, action, reward, next_state)
```

训练时不是直接用最新连续样本，而是从 replay memory 中均匀采样 minibatch。这样有三个作用：

- 打破连续帧之间的强相关性。
- 让同一条经验可以被多次利用，提高数据效率。
- 平滑策略变化造成的数据分布漂移。

论文使用最近 `1,000,000` 帧作为 replay memory，minibatch size 为 `32`。

#### Target Network

如果 target 也由正在更新的网络实时计算，训练会形成“自己追自己”的不稳定反馈。DQN 因此维护一个延迟更新的目标网络 `Q_target`：

```text
y = r + gamma * max_a' Q_target(s', a')
```

目标网络参数每隔 `C` 步从当前 Q-network 复制一次，中间保持固定。这个延迟可以显著降低振荡和发散风险。

### 5. 训练细节

论文中对所有游戏使用同一套网络结构、训练算法和超参数：

- 优化器：RMSProp
- 折扣因子：`gamma = 0.99`
- minibatch size：`32`
- replay memory：`1,000,000` 最近帧
- 训练长度：`50,000,000` 帧，约等于 `38` 天游戏经验
- 探索策略：`epsilon-greedy`
- `epsilon`：从 `1.0` 线性降到 `0.1`，之后保持 `0.1`
- 评估时：`epsilon = 0.05`
- 奖励裁剪：正奖励裁剪为 `+1`，负奖励裁剪为 `-1`，零奖励不变
- TD error clipping：将更新误差裁剪到稳定范围，进一步减少梯度爆炸和发散

奖励裁剪让同一套学习率能跨游戏使用，但也会丢失奖励大小信息。例如得 1 分和得 100 分在训练信号上都变成 `+1`。

## Experiments

实验平台是 Atari 2600，共 49 个游戏。DQN 的输入只包括：

- 屏幕像素
- 游戏分数变化形成的奖励
- 当前游戏可用动作集合

它不知道游戏规则、物体类别、动作语义，也没有使用专门为 Atari 设计的手工特征。

论文用随机策略作为 `0%`，专业人类测试员作为 `100%`，归一化分数为：

```text
100 * (DQN score - random score) / (human score - random score)
```

关键结果：

- 在 43 个游戏上超过此前强化学习方法。
- 在 29 个游戏上达到超过人类测试员 `75%` 的分数。
- 在一些反应型、视觉模式明显的游戏上非常强，例如 Breakout、Boxing、Video Pinball。
- 在需要长期规划、复杂探索或稀疏奖励的游戏上仍然明显不足。

论文还做了消融实验，说明 replay memory、target network 和 CNN 表示学习都是性能的重要来源。去掉这些组件后，训练稳定性和最终分数都会显著下降。

## Key Insights

### 关键结果 1：从像素到动作的端到端 RL 被跑通了

DQN 的突破在于它不再要求人工设计状态特征。网络直接从图像学习表示，强化学习损失直接驱动视觉特征为控制任务服务。

这和普通监督学习的图像分类不同：DQN 的表示不是为了识别物体标签，而是为了预测“当前状态下采取某个动作，未来会得到多少奖励”。

### 关键结果 2：成功来自算法和工程稳定性的组合

DQN 不是只靠 CNN，也不是只靠 Q-learning。真正让它可用的是几个稳定化技巧同时成立：

- replay memory 降低样本相关性。
- target network 降低 target 抖动。
- reward clipping 统一不同游戏的奖励尺度。
- error clipping 控制 TD 更新幅度。
- frame stack 给网络提供短期运动信息。

这些设计后来成为深度强化学习算法的基础模板。

### 关键结果 3：一个网络同时输出所有动作 Q 值，效率很高

论文没有把 `(state, action)` 拼起来作为网络输入，再对每个动作分别 forward。它让 CNN 共享视觉特征，在输出层为每个动作给一个 Q 值。

这个设计很实用：Atari 每一步最多十几个动作，一次 forward 就能选择 `argmax_a Q(s, a)`。

### 关键结果 4：DQN 学到的是任务相关表示

论文用 t-SNE 和 value visualization 展示了网络最后隐藏层的表示。相似游戏状态会聚在一起，且某些高价值状态会被网络提前预测出来。

这说明 DQN 学到的不是简单记忆画面，而是和未来奖励有关的状态抽象。当然，这种抽象仍然局限在单个游戏训练出来的策略中，并不是跨游戏的通用世界模型。

### 我的理解

DQN 的核心价值可以概括为：

> 它把深度视觉表示学习、Q-learning、经验回放和目标网络组合成一个稳定闭环，让智能体第一次能在一批复杂视觉控制任务上从原始像素直接学策略。

它的贡献偏系统性：每个组件单看都不神秘，但组合后解决了当时最关键的训练不稳定问题。后来的 Double DQN、Dueling DQN、Prioritized Replay、Distributional RL、Rainbow 等工作，基本都是沿着 DQN 暴露出的缺陷继续改。

## Limitations & Future Work

- **样本效率低**：每个游戏训练 `50M` 帧，约 `38` 天游戏经验，人类远不需要这么多交互。
- **没有跨任务迁移**：虽然同一套超参数用于 49 个游戏，但每个游戏仍然单独训练一个 agent。
- **探索能力弱**：`epsilon-greedy` 对稀疏奖励、长程依赖和需要深度探索的游戏不够。
- **奖励裁剪有副作用**：裁剪提高稳定性，但会抹掉奖励大小差异，可能让策略偏离真实任务目标。
- **Q-learning 仍有估计偏差**：`max_a Q(s, a)` 容易过估计动作价值，后续 Double DQN 专门处理这个问题。
- **只使用短期历史**：4 帧堆叠只能处理有限的部分可观测性，不能替代长期记忆。
- **不是通用智能**：DQN 在 Atari 上很强，但没有语言、推理、长期计划、跨环境泛化和可解释目标建模能力。

后续值得关注的方向包括：

1. 提高样本效率，例如 model-based RL、offline RL 或更好的 replay 机制。
2. 改进探索策略，处理稀疏奖励和长程任务。
3. 加入记忆和层级策略，处理更复杂的部分可观测环境。
4. 跨任务共享表示或策略，实现真正的多任务泛化。
5. 从单纯 value-based 方法扩展到 actor-critic、policy gradient 和现代深度 RL 系统。

## Reproduction Notes

复现这篇文章时优先确认以下细节：

- 使用 Atari Learning Environment 或兼容环境。
- 输入预处理是否严格包含 max over frames、灰度/亮度通道、`84 x 84` resize、4 帧堆叠。
- action repeat / frame skipping 是否和论文一致。
- replay memory 容量、warm-up、采样方式是否一致。
- target network 更新频率是否正确。
- reward clipping、TD error clipping、RMSProp 参数是否一致。
- evaluation 是否使用 `epsilon = 0.05`、30 次 episode、不同 no-op 初始条件。

这篇文章的复现难点不在公式，而在训练细节。只要少掉 replay、target network、reward clipping 或正确的 Atari preprocessing，训练曲线都可能完全不稳定。
