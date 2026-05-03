# PPO

## Paper Info

- **Title**: Proximal Policy Optimization Algorithms
- **Authors**: John Schulman, Filip Wolski, Prafulla Dhariwal, Alec Radford, Oleg Klimov
- **Venue**: arXiv 2017
- **ArXiv**: [1707.06347](https://arxiv.org/abs/1707.06347)
- **Paper**: [paper.pdf](./paper.pdf)

## Abstract

`PPO` 是现代深度强化学习里最常用的 policy gradient / actor-critic 方法之一。
它的目标是在保留 `TRPO` 稳定性的同时，去掉二阶近似、conjugate gradient 和显式 trust region 约束，让算法可以直接用一阶优化器和 minibatch SGD 训练。

一句话总结：
`PPO` 的核心是用 clipped surrogate objective 限制新旧策略的概率比变化，让策略可以对同一批 rollout 做多轮更新，同时避免单次 policy update 过大。

## Motivation

在 PPO 之前，深度强化学习里的几类方法各有明显短板：

- `DQN` 主要适合离散动作空间，对连续控制不自然。
- vanilla policy gradient 简单但样本效率低，且多轮复用同一批 trajectory 时容易更新过头。
- `TRPO` 用 KL 约束控制策略变化，稳定性好，但实现复杂、计算开销高，也不容易和参数共享、dropout、辅助任务等工程结构结合。

论文想解决的问题是：

> 能不能得到一种接近 TRPO 稳定性、但像普通神经网络训练一样简单的一阶 policy optimization 方法？

PPO 的重要性就在这里：它不是追求理论上最精确的 trust region，而是给出了一个足够稳、足够简单、足够通用的工程折中。

## Method

### 1. Policy Ratio

PPO 从旧策略 `pi_old` 采样数据，然后更新新策略 `pi_theta`。
关键量是新旧策略在已采样动作上的概率比：

```text
r_t(theta) = pi_theta(a_t | s_t) / pi_old(a_t | s_t)
```

如果 `r_t` 远离 `1`，说明新策略相比采样策略变化很大。
policy gradient 的普通 surrogate objective 可以写成：

```text
L = E_t [ r_t(theta) * A_t ]
```

其中 `A_t` 是 advantage estimate。
问题是，如果直接最大化这个目标，多轮 SGD 可能会把策略推得太远，导致性能崩掉。

### 2. Clipped Surrogate Objective

PPO-Clip 的核心目标为：

```text
L_clip = E_t [
  min(
    r_t(theta) * A_t,
    clip(r_t(theta), 1 - epsilon, 1 + epsilon) * A_t
  )
]
```

直觉可以分两种情况理解：

- 当 `A_t > 0` 时，动作比平均更好，算法希望增加它的概率，但最多鼓励到 `r_t = 1 + epsilon`。
- 当 `A_t < 0` 时，动作比平均更差，算法希望降低它的概率，但最多鼓励到 `r_t = 1 - epsilon`。

`min` 让目标变成一个 pessimistic surrogate：当策略变化已经带来足够收益时，不再继续奖励更激进的更新；当变化让目标变差时，仍然把坏影响计入 loss。

### 3. PPO-Penalty

论文也讨论了另一种形式：在 surrogate objective 中加入 KL penalty，并动态调整 penalty coefficient。
但实验显示 clipped objective 更简单、表现更好，因此后来默认说 `PPO` 时通常指 `PPO-Clip`。

### 4. Actor-Critic Training

实际训练中，PPO 通常会联合优化：

- clipped policy objective
- value function loss
- entropy bonus

并使用 advantage estimation，论文实验中常配合 `GAE(lambda)`。
训练流程是：

1. 用当前策略与环境交互，收集一批 trajectories。
2. 估计 return 和 advantage。
3. 在这批数据上做多轮 minibatch SGD。
4. 更新策略后重新采样数据，进入下一轮。

这使 PPO 仍然是 on-policy 方法，但比 vanilla policy gradient 更充分地利用每批 rollout。

## Key Insights

### 关键结果 1：clip 是一个工程上很强的 trust region 近似

PPO 没有像 TRPO 那样显式求解 KL 约束优化问题，而是通过 probability ratio clipping 给每个样本的更新贡献设上限。
这个近似不严格等价于 trust region，但足够简单，并且和现代深度学习框架高度兼容。

### 关键结果 2：可以对同一批数据做多轮更新

vanilla policy gradient 通常不适合对同一批 trajectory 反复优化，因为策略会快速偏离采样分布。
PPO 通过限制 `r_t` 的有效范围，让多 epoch minibatch training 变得可行，从而提高样本利用率。

### 关键结果 3：在连续控制和 Atari 上都有竞争力

论文在 MuJoCo、Roboschool humanoid 和 Atari 上评估 PPO。
结果显示，PPO 在连续控制中优于多种在线 policy gradient baseline；在 Atari 上也显著优于 A2C，接近或优于 ACER，同时算法结构更简单。

这说明 PPO 的价值不只是某个环境上的调参结果，而是跨离散动作和连续动作都有实用性。

### 关键结果 4：PPO 的流行来自“稳定性 + 简洁性”

PPO 后来成为 RLHF、机器人控制、游戏智能体和各类 RL baseline 的默认选择，原因不是它理论最强，而是它的综合工程属性好：

- 实现短。
- 容易并行采样。
- 对超参数相对鲁棒。
- 可以直接接神经网络 actor-critic。
- 不需要复杂二阶优化。

### 我的结论

如果只用一句话评价 PPO：

> PPO 是把 TRPO 的“不要让策略更新太远”改造成神经网络训练友好版本的算法，它牺牲一部分严格理论形式，换来了极高的工程可用性。

它非常适合作为默认强化学习起点，但也要记住它仍然是 on-policy 方法，样本效率和探索能力并没有从根本上解决。

## Limitations & Future Work

- **仍然样本效率有限**：PPO 可以复用一批 rollout 做多轮更新，但本质仍然接近 on-policy，真实机器人等高成本场景会很贵。
- **clip 不等价于全局 trust region**：逐样本 probability ratio clipping 不能严格保证整体策略 KL 在合理范围内。
- **对 advantage 估计敏感**：reward scaling、value function quality、GAE 参数都会明显影响训练效果。
- **探索机制弱**：entropy bonus 只能提供有限随机性，对稀疏奖励和长程探索不够。
- **超参数仍然重要**：`epsilon`、batch size、epoch 数、learning rate、value loss 权重、entropy 系数都会影响稳定性。
- **容易被当成黑盒 baseline**：PPO 看似简单，但实现细节差异会导致结果差很多。

后续值得关注的方向包括：

1. 更高样本效率的 off-policy actor-critic 和 offline RL。
2. 更好的 exploration 与 reward shaping。
3. 更稳健的 large policy optimization，尤其是在 RLHF 和 VLA 训练中。
4. 对 PPO 训练细节的标准化复现，例如 advantage normalization、value clipping、KL early stopping 等工程变体。

## Reproduction Notes

复现 PPO 时优先确认：

- `r_t` 的计算是否使用旧策略 log-prob 缓存。
- advantage 是否 normalize。
- 是否使用 GAE，以及 `gamma/lambda` 设置。
- 每批 rollout 做多少个 epochs、minibatch size 多大。
- policy loss、value loss、entropy bonus 的权重。
- 是否做 reward normalization、observation normalization。
- 是否记录 approximate KL、clip fraction 和 entropy。

PPO 的公式很短，但训练曲线高度依赖实现细节。只看最终 reward 不够，最好同时监控 KL、clip fraction、value loss 和 entropy。
