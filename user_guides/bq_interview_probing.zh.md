# BQ 面试追问功能用户指南

> **语言**: [中文](bq_interview_probing.zh.md) | [English](bq_interview_probing.en.md)

## 概述

BQ 面试追问功能通过模拟真实的 FAANG 行为面试，在您给出初始回答后进行追问。它使用**智能追问代理**和**学习型停止策略**来精确判断何时停止追问——就像真正的面试官一样。

### 核心特性

1. **真实面试模拟**: 模拟 FAANG 面试官追问细节的方式
2. **学习型停止策略**: 基于面试数据训练的 ML 模型决定何时停止（88% 准确率）
3. **回答分类**: 自动分类您的回答（优秀、模糊、部分等）
4. **缺口追踪**: 识别并追踪回答中需要补充的缺口
5. **级别感知**: 根据 Junior-Mid / Senior / Staff 级别调整期望

---

## 工作原理

### 追问流程

```
用户输入: BQ 问题 + 初始回答 + 级别
              ↓
┌─────────────────────────────────────────────────────────────────┐
│  步骤 1: 初始评估                                               │
│  - 根据级别期望评估回答                                         │
│  - 识别缺口（缺少指标、模糊的归属等）                           │
│  - 生成初始追问问题                                             │
│  - 给出初步评级                                                 │
└─────────────────────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────────────────────┐
│  步骤 2: 追问循环                                               │
│                                                                 │
│  每一轮:                                                        │
│    1. 向用户提出追问问题                                        │
│    2. 用户回答                                                  │
│    3. 分类回答类型:                                             │
│       • ANSWER_GOOD - 具体，有指标/归属                         │
│       • ANSWER_PARTIAL - 有些细节但不完整                       │
│       • ANSWER_VAGUE - 笼统，缺少具体内容                       │
│       • ASKS_QUESTION - 用户需要澄清                            │
│       • SAYS_IDK - 用户没有答案                                 │
│       • PUSHBACK - 用户质疑问题                                 │
│                                                                 │
│    4. ══► 学习型停止策略 ◄══                                    │
│       │  应该 停止 还是 继续？                                  │
│       │                                                         │
│       │  输入（10 个特征）:                                     │
│       │  • gaps_remaining, gaps_resolved                        │
│       │  • turn_count, good_responses, vague_responses          │
│       │  • idk_count, pushback_count, friction_ratio            │
│       │  • is_senior, is_staff                                  │
│       │                                                         │
│       │  停止条件:                                               │
│       │  • 收集到足够的优质回答                                 │
│       │  • 高摩擦（候选人无法回答）                             │
│       │  • 所有缺口已解决                                       │
│       │  • 达到最大轮数                                         │
│                                                                 │
│    5. 如果 继续 → 生成上下文相关的追问                          │
│       如果 停止 → 结束追问                                      │
└─────────────────────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────────────────────┐
│  步骤 3: 最终评估                                               │
│  - 汇总所有问答对                                               │
│  - 根据追问结果更新评级                                         │
│  - 生成综合反馈                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 学习型停止策略

停止策略使用**逻辑回归模型**，基于 30+ 个合成面试会话和教师标签进行训练。它达到 **88% 准确率**，而基于规则的启发式方法只有 60%。

#### 特征重要性

| 特征 | 权重 | 解释 |
|------|------|------|
| `good_responses` | +3.04 | 更多实质性回答 → 停止 |
| `turn_count` | +0.99 | 对话后期 → 停止 |
| `gaps_resolved` | +0.97 | 更多缺口已解决 → 停止 |
| `is_senior` | +0.77 | Senior 级别 → 更早停止 |
| `vague_responses` | +0.68 | 多个模糊回答 → 停止（收益递减）|
| `gaps_remaining` | -0.66 | 剩余缺口更少 → 停止 |
| `pushback_count` | +0.36 | 候选人抵触 → 停止 |

#### 决策示例

```
状态: 第4轮, good_responses=2, gaps_remaining=1, friction=10%

学习策略: 停止（92% 置信度）
原因: "收集了2个实质性回答，仅剩1个小缺口"
```

---

## 使用方法

### 前置条件

1. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

2. **设置 API 密钥**
   - 创建 `.env` 文件并添加 OpenAI API 密钥
   ```
   OPENAI_API_KEY=sk-...
   ```

### CLI 使用

#### 分析 BQ 问题

```bash
python main.py
```

然后选择 `[2] Practice BQ Question` 并选择一个问题。

#### 编程使用

```python
import asyncio
from interview_analyzer import AgenticInterviewer
from prompts import BQQuestions

async def main():
    question = "请告诉我一个你面对挑战性项目的经历。"
    answer = """
    我在公司主导了从单体架构到微服务的迁移。
    挑战在于我们必须在迁移过程中保持系统正常运行。
    我与团队一起规划了分阶段迁移方案。
    我们成功完成了迁移并提高了系统可靠性。
    """
    level = "Senior"

    # 步骤 1: 获取初始评估
    prompt = BQQuestions.real_interview(
        question=question,
        answer=answer,
        level=level
    )
    # ... 调用 LLM 获取评估 ...

    # 步骤 2: 初始化追问代理
    interviewer = AgenticInterviewer(model="gpt-4o-mini", max_turns=8)
    result = interviewer.initialize(
        question=question,
        answer=answer,
        evaluation=evaluation,
        level=level
    )

    if result["action"] == "STOP":
        print("无需追问 - 回答已完整！")
        return

    # 步骤 3: 追问循环
    while interviewer.should_continue():
        probe = interviewer.get_current_probe()
        print(f"\n面试官: {probe}")

        user_response = input("你的回答: ")

        decision = await interviewer.step(user_response)

        if decision["action"] == "STOP":
            print("\n面试官: 谢谢，我已经获得足够的信息了。")
            break

    # 步骤 4: 获取最终问答对
    qa_pairs = interviewer.get_qa_pairs()
    for q, a in qa_pairs:
        print(f"问: {q}")
        print(f"答: {a}\n")

asyncio.run(main())
```

### API 参考

#### `AgenticInterviewer`

**初始化**

```python
interviewer = AgenticInterviewer(
    model="gpt-4o-mini",  # 使用的 LLM 模型
    max_turns=8           # 最大追问轮数
)
```

**方法**

| 方法 | 描述 |
|------|------|
| `initialize(question, answer, evaluation, level)` | 设置面试会话 |
| `should_continue()` | 检查是否需要更多追问 |
| `get_current_probe()` | 获取当前要问的问题 |
| `step(user_response)` | 处理用户回答并决定下一步 |
| `get_qa_pairs()` | 获取会话中的所有问答对 |
| `get_decisions()` | 获取所有决策历史 |

**`step()` 返回值**

```python
{
    "response_type": "ANSWER_GOOD",  # 用户回答的分类
    "action": "PROBE_SAME",          # PROBE_SAME, PROBE_NEXT, STOP, REDIRECT
    "agent_message": "...",          # 下一个问题或结束语
    "reasoning": "...",              # 做出此决策的原因
    "classification": {
        "response_type": "ANSWER_GOOD",
        "confidence": "HIGH",
        "runner_up_type": null
    },
    "state_update": {
        "gaps_resolved": ["ownership"],
        "gaps_unresolvable": []
    }
}
```

---

## 回答类型

系统对每个用户回答进行分类：

| 类型 | 描述 | 示例 |
|------|------|------|
| `ANSWER_GOOD` | 具体，有指标/归属 | "我个人通过...将延迟降低了40%" |
| `ANSWER_PARTIAL` | 有些细节但不完整 | "我参与了优化工作..." |
| `ANSWER_VAGUE` | 笼统，缺少具体内容 | "我们显著改善了情况" |
| `ASKS_QUESTION` | 用户需要澄清 | "你是指技术挑战还是人员挑战？" |
| `SAYS_IDK` | 用户没有答案 | "我没有这方面的好例子" |
| `PUSHBACK` | 用户质疑问题 | "我认为这个问题不太相关" |
| `OFF_TOPIC` | 用户跑题 | "说到这个，我曾经..." |
| `NEW_INFO` | 透露新信息 | "其实我忘了提到..." |

---

## 示例会话

```
问题: 请告诉我一个你在舒适区之外工作的经历。

初始回答: 我主导了一个涉及多个部门的跨职能项目...
[缺失: 具体冲突例子、指标、个人归属]

───────────────────────────────────────────────────────────────────
第 1 轮
───────────────────────────────────────────────────────────────────
面试官: 你能给我一个具体的冲突例子，以及你是如何解决的吗？

你: 团队之间关于优先级有一些分歧...

分类: ANSWER_VAGUE（缺少具体内容）
策略决策: 继续（仍有缺口，低摩擦）

───────────────────────────────────────────────────────────────────
第 2 轮
───────────────────────────────────────────────────────────────────
面试官: 你能详细说明一个具体的分歧吗？
        冲突是关于什么的，你做了什么？

你: 市场团队想要功能A，开发团队想要功能B。
    我根据对关键路径的分析提出了60/40的分配方案。
    我先获得了经理的支持，然后向团队展示。

分类: ANSWER_GOOD（具体，展示归属）
策略决策: 继续（还有缺口需要解决）

───────────────────────────────────────────────────────────────────
第 3 轮
───────────────────────────────────────────────────────────────────
面试官: 结果如何？你有关于影响的指标吗？

你: 项目提前2周交付。团队满意度从季度调查的6.2提升到8.1。
    我学到了在向团队提出方案之前，要先进行一对一沟通。

分类: ANSWER_GOOD（有指标，有反思）
策略决策: 停止（88% 置信度）← 学习策略触发

面试官: 谢谢，我已经获得足够的信息了。
```

---

## 最佳实践

### 对于用户

1. **具体化**: 包含数字、日期、人名、技术
2. **展示归属**: 用"我"而不是"我们"——你做了什么？
3. **遵循 STAR**: 情境 → 任务 → 行动 → 结果
4. **包含指标**: 尽可能量化你的影响
5. **反思**: 分享你学到了什么，以及会有什么不同做法

### 对于开发者

1. **定期重新训练**: 收集更多会话后运行 `--train`
2. **监控准确率**: 检查策略是否过早/过晚停止
3. **添加摩擦示例**: 生成更多 IDK/PUSHBACK 会话以保持平衡

---

## 故障排除

### 常见问题

1. **策略总是说继续**
   - 检查模型文件是否存在: `policy/stop_policy_model.pkl`
   - 验证模型已加载: `interviewer.stop_policy.learned.model_loaded`

2. **追问质量低**
   - 确保初始评估识别了正确的缺口
   - 检查 `level` 参数是否匹配候选人经验

3. **追问结束过早**
   - 置信度阈值可能太低（默认: 0.7）
   - 在 `HybridStopPolicy.confidence_threshold` 中调整

---

## 相关功能

- **自动补全**: 使用 `advance/auto_completion.py` 补全部分回答
- **自我改进**: 使用 `advance/self_improve.py` 迭代改进回答
- **构建故事**: 使用 BQ 追问帮助从零构建 STAR 故事

---

## 技术细节

### 停止策略训练

学习策略的训练使用：
1. 使用 `bootstrap_training.py` 生成的合成面试会话
2. GPT-4o 确定最佳停止点的教师标签
3. 基于 10 个状态特征的逻辑回归

重新训练：
```bash
# 生成更多训练数据
python policy/bootstrap_training.py --synthetic 50

# 使用 GPT-4o 重新标注（可选）
python policy/bootstrap_training.py --relabel

# 训练模型
python policy/bootstrap_training.py --train
```

### 模型性能

| 模型 | 准确率 | 停止召回率 |
|------|--------|-----------|
| **学习策略** | **88%** | **92%** |
| 启发式基线 | 60% | 17% |
| LLM 零样本 | 56% | 8% |

---

## 支持

如有问题：
1. 查看 `examples/` 目录中的示例
2. 查看 `prompts.py` 中的提示模板
3. 查看策略文档: `policy/README.md`
