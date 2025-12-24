# Research Ideas & Findings

> For context engineering - Core research ideas and empirical findings from Story-Improve system

## 研究目标

基于Story-Improve系统，研究Chain-of-Thought (CoT) Prompting在行为面试评估场景中的应用，识别其局限性并提出增强方案。

## 核心发现

### Finding 1: Human-in-the-Loop显著提升训练效果和定制化

**发现类型：** Idea + 实证发现

**核心观察：**
- Story-Improve使用CoT Prompting进行面试答案改进
- **对比发现**：Human-in-the-loop方式（`HumanInLoopImprove`）比纯自动化CoT（`StorySelfImprove`）效果更好
- **关键优势**：
  - ✅ **培训意义**：能真正起到培训作用，帮助候选人反思真实经历
  - ✅ **定制化**：可以根据个人背景和经验水平定制答案
  - ✅ **真实性**：使用候选人的真实经历细节，而非LLM生成的虚构内容

**技术实现：**
- 自动化方式：`advance/self_improve.py:14-107` (`StorySelfImprove`)
- Human-in-loop方式：`advance/self_improve.py:109-397` (`HumanInLoopImprove`)
- 关键方法：`BQAnswer.improve_with_probing_answers()` - 使用用户真实回答而非LLM生成

**研究价值：**
- 证明在面试培训场景中，human-in-the-loop比纯自动化更有价值
- 为面试培训系统设计提供实证依据

---

### Finding 2: CoT Prompting在面试场景中快速收敛

**发现类型：** 实证发现

**核心观察：**
- Story-Improve使用CoT Prompting进行迭代改进
- **收敛行为**：迭代1次和迭代100次效果没有显著区别
- **具体表现**：
  - 第1次迭代：显著改进（如 "Leaning No Hire" → "Hire"）
  - 第2-5次迭代：边际改进或无明显改进
  - 第6-100次迭代：无测量到的改进

**技术实现：**
- 实现位置：`advance/self_improve.py:81-106` (`StorySelfImprove.run()`)
- 迭代机制：递归迭代，最多5次（实际测试到100次也无改进）
- 评估方法：使用`BQQuestions.real_interview()` + `BQQuestions.bar_raiser()`

**可能原因：**
1. 面试评估标准明确（FAANG rubrics），有界解空间
2. CoT推理在第一轮就能识别所有主要gap
3. 后续迭代只能解决不影响评级的次要问题

**研究价值：**
- 揭示CoT在结构化评估任务中的收敛特性
- 为资源优化提供依据（单次迭代可能足够）

---

### Finding 3: 需要Adversarial Challenging机制才能达到真实评估效果

**发现类型：** Idea + 实证发现

**核心观察：**
- 纯CoT Prompting在面试评估场景下会产生**过于乐观的评估**
- **关键发现**：需要加入"随机主观challenging"（adversarial challenging）才能还原真实面试官行为
- **实现机制**：`bar_raiser()`函数实现negativity bias模型

**技术实现：**
- 实现位置：`prompts.py:454-492` (`BQQuestions.bar_raiser()`)
- 核心机制：
  1. **Negativity Bias Model**: "Assume no skill unless explicitly demonstrated"
  2. **Ownership Tracing**: 只奖励明确由候选人驱动的行动
  3. **Scope Validation**: 挑战有限影响范围的例子
  4. **Data-Driven Requirement**: 缺少metrics时降级评级
  5. **Industry Context**: 模拟2025年竞争激烈的招聘环境

**对比观察：**
- **无bar_raiser()**：评估倾向于"Hire"或"Strong Hire"（过于乐观）
- **有bar_raiser()**：评估更接近真实面试官评级
- **真实面试官行为**：防御性评估（假设弱点直到证明相反）
- **LLM默认行为**：乐观评估（假设优势除非明确弱）

**研究价值：**
- 揭示LLM评估系统需要domain-specific的adversarial机制
- 证明negativity bias在面试评估中的必要性
- 为真实评估系统设计提供机制参考

---

## 研究贡献总结

1. **Human-in-the-Loop增强**：实证证明human-in-the-loop在面试培训场景中的优势
2. **收敛行为分析**：揭示CoT在结构化评估任务中的快速收敛特性
3. **Adversarial机制**：提出并验证negativity bias模型对真实评估的必要性

## 技术架构

**核心系统：** Story-Improve
- `advance/self_improve.py`: 改进机制实现
- `prompts.py`: Prompt模板和评估机制
- `interview_analyzer.py`: LLM集成和分析

**关键组件：**
- `StorySelfImprove`: 纯CoT自动化改进
- `HumanInLoopImprove`: Human-in-the-loop改进
- `BQQuestions.bar_raiser()`: Adversarial challenging机制

## 研究问题

1. Human-in-the-loop集成如何影响CoT-based面试答案改进的效果？
2. CoT Prompting在面试评估场景中的收敛行为是什么？
3. 使用LLM实现真实面试评估需要什么机制？

## 下一步工作

- [ ] 定量实验验证（与人类评估者对比）
- [ ] 扩展到其他面试类型和评估标准
- [ ] 分析`bar_raiser()`各组件对真实性的贡献
- [ ] 探索自动化和人工输入的最优平衡
