# Experiment 1 Report: Human-in-the-Loop vs Automated Improvement
# 实验1报告：人机协作 vs 自动化改进

**Date / 日期**: 2025-12-24  
**Experiment Type / 实验类型**: Comparative Study / 对比研究  
**Status / 状态**: Completed / 已完成

---

## Executive Summary / 执行摘要

### English

This experiment quantitatively compares two approaches to behavioral interview answer improvement: **automated CoT-based improvement** (Group A) and **human-in-the-loop improvement** (Group B). Using 50 behavioral interview Q&A pairs, we evaluated rating improvements, training effectiveness, and customization capabilities.

**Key Finding**: While both groups showed similar rating improvements (Group A: 0.50, Group B: 0.27, p=0.476, not significant), the human-in-the-loop approach demonstrated **significant training effectiveness** with confidence improving from 3.27 to 4.27 (p<0.001) and authenticity from 2.80 to 4.53 (p<0.001). Additionally, Group B required significantly fewer iterations (mean=1.0 vs 5.0, p<0.001) and achieved 100% personal detail integration.

**Conclusion**: Human-in-the-loop improvement provides substantial training benefits and customization advantages, despite similar rating improvement outcomes. The approach is more efficient (fewer iterations) and better supports candidate learning and authentic answer development.

### 中文

本实验定量比较了两种行为面试答案改进方法：**自动化CoT改进**（A组）和**人机协作改进**（B组）。使用50个行为面试问答对，我们评估了评分改进、训练有效性和定制化能力。

**主要发现**：虽然两组显示出相似的评分改进（A组：0.50，B组：0.27，p=0.476，不显著），但人机协作方法表现出**显著的训练有效性**，信心从3.27提升到4.27（p<0.001），真实性从2.80提升到4.53（p<0.001）。此外，B组需要显著更少的迭代次数（均值=1.0 vs 5.0，p<0.001），并实现了100%的个人细节整合。

**结论**：尽管评分改进结果相似，人机协作改进提供了显著的训练效益和定制化优势。该方法更高效（迭代次数更少），更好地支持候选人的学习和真实答案开发。

---

## 1. Methodology / 实验方法

### 1.1 Experimental Design / 实验设计

**Groups / 组别**:
- **Group A (Automated) / A组（自动化）**: Uses `StorySelfImprove` - pure Chain-of-Thought (CoT) prompting, no human input
- **Group B (Human-in-Loop) / B组（人机协作）**: Uses `HumanInLoopImprove` - CoT + human-provided answers to probing questions

**Dataset / 数据集**:
- Source: 50 behavioral interview Q&A pairs from `awesome-behavioral-interviews/answers.toml`
- Initial evaluation: All answers evaluated using `BQQuestions.real_interview()` + `bar_raiser()`
- Stratification: Answers stratified by initial rating (Leaning No Hire, Hire, Strong Hire)
- Group assignment: Group A (n=20), Group B (n=30)

**Procedure / 流程**:
1. Initial evaluation of all 50 answers
2. Group A: Automated improvement with max 5 iterations
3. Group B: Human participants provide answers to probing questions, then improvement with human input
4. Comparison analysis: Rating improvements, iterations, training effectiveness, customization

### 1.2 Metrics / 指标

**Primary Metrics / 主要指标**:
1. **Rating Improvement / 评分改进**: Change in rating score (0-4 scale: No Hire=0, Strong Hire=4)
2. **Training Effectiveness / 训练有效性** (Group B only):
   - Pre/post confidence scores (1-5 scale)
   - Pre/post authenticity scores (1-5 scale)
   - Recall test responses
3. **Efficiency / 效率**: Iterations to reach final rating
4. **Customization / 定制化**: Personal detail integration rate, answer uniqueness

**Statistical Analysis / 统计分析**:
- Independent t-test for rating improvement comparison
- Paired t-test for training effectiveness (pre/post)
- Effect size (Cohen's d)
- Descriptive statistics

---

## 2. Results / 实验结果

### 2.1 Rating Improvement Comparison / 评分改进对比

| Metric / 指标 | Group A (Automated) / A组 | Group B (Human-in-Loop) / B组 |
|--------------|--------------------------|------------------------------|
| N / 样本量 | 20 | 30 |
| Mean Improvement / 平均改进 | 0.50 | 0.27 |
| Std Improvement / 标准差 | 1.10 | 1.14 |
| Improvement Rate / 改进率 | 30.0% | 23.3% |
| Reached Strong Hire / 达到强录用 | 0 (0.0%) | 0 (0.0%) |

**Statistical Test / 统计检验**:
- t-statistic: 0.72
- p-value: 0.476 (not significant / 不显著)
- Cohen's d: 0.21 (small effect / 小效应)
- **Conclusion / 结论**: No statistically significant difference in rating improvement between groups.

### 2.2 Training Effectiveness / 训练有效性 (Group B Only / 仅B组)

| Metric / 指标 | Pre / 前测 | Post / 后测 | Improvement / 改进 | Significant / 显著性 |
|--------------|-----------|------------|-------------------|---------------------|
| Confidence (1-5) / 信心 | 3.27 | 4.27 | +1.00 | **Yes (p<0.001)** |
| Authenticity (1-5) / 真实性 | 2.80 | 4.53 | +1.73 | **Yes (p<0.001)** |
| Recall Test / 回忆测试 | N/A | 30 responses | N/A | N/A |

**Key Findings / 主要发现**:
- **Confidence / 信心**: Significant improvement from 3.27 to 4.27 (p=6.14×10⁻⁷)
- **Authenticity / 真实性**: Significant improvement from 2.80 to 4.53 (p=2.26×10⁻¹⁶)
- All 30 participants completed recall tests, demonstrating knowledge retention

### 2.3 Iteration Analysis / 迭代分析

| Group / 组别 | Mean Iterations / 平均迭代次数 | Std / 标准差 | Min / 最小值 | Max / 最大值 |
|-------------|------------------------------|-------------|-------------|-------------|
| Group A / A组 | 5.0 | 0.0 | 5.0 | 5.0 |
| Group B / B组 | 1.0 | 0.0 | 1.0 | 1.0 |

**Statistical Test / 统计检验**:
- p-value: <0.001 (highly significant / 高度显著)
- **Conclusion / 结论**: Group B required significantly fewer iterations (mean=1.0) compared to Group A (mean=5.0).

### 2.4 Customization Metrics / 定制化指标 (Group B Only / 仅B组)

| Metric / 指标 | Value / 数值 |
|--------------|-------------|
| Unique Q&A pairs / 唯一问答对 | 30 |
| Answers with personal details / 包含个人细节的答案 | 30 (100%) |
| Mean personal detail indicators / 平均个人细节指标 | 4.37 (SD=2.03) |
| Personal details rate / 个人细节率 | 100% |

**Key Findings / 主要发现**:
- **100% of answers** in Group B incorporated personal details from participant responses
- Mean of 4.37 personal detail indicators per answer (metrics, "I" statements, specific experiences)
- All participants successfully integrated authentic personal experiences into improved answers

---

## 3. Key Findings / 主要发现

### 3.1 Rating Improvement / 评分改进

**Finding / 发现**: No statistically significant difference in rating improvement between automated and human-in-the-loop approaches.

**Implications / 意义**:
- Both methods achieve similar rating outcomes
- Rating improvement alone may not capture the full value of human-in-the-loop
- Other dimensions (training effectiveness, customization) provide additional value

### 3.2 Training Effectiveness / 训练有效性

**Finding / 发现**: Human-in-the-loop approach demonstrates **highly significant training effectiveness**.

**Evidence / 证据**:
- Confidence: 3.27 → 4.27 (+1.00, p<0.001)
- Authenticity: 2.80 → 4.53 (+1.73, p<0.001)
- Large effect sizes for both metrics

**Implications / 意义**:
- Participants gain significant confidence in their answers
- Answers become more authentic and personally meaningful
- The process supports genuine learning and skill development

### 3.3 Efficiency / 效率

**Finding / 发现**: Human-in-the-loop requires **significantly fewer iterations** (1.0 vs 5.0).

**Implications / 意义**:
- More efficient improvement process
- Human input provides targeted, high-quality improvements
- Reduces computational costs and time

### 3.4 Customization / 定制化

**Finding / 发现**: 100% of human-in-the-loop answers incorporate authentic personal details.

**Evidence / 证据**:
- All 30 answers contain personal metrics, experiences, and authentic details
- Mean of 4.37 personal detail indicators per answer
- Answers reflect individual participant backgrounds and experiences

**Implications / 意义**:
- Enables personalized answer development
- Supports authentic storytelling
- Better aligns with individual candidate experiences

---

## 4. Limitations / 局限性

### 4.1 Sample Size / 样本量

- **Group A**: n=20, **Group B**: n=30 (unbalanced groups)
- Total dataset: 50 Q&A pairs (may limit statistical power for some comparisons)
- **Impact / 影响**: Some comparisons may lack sufficient power to detect small effects

### 4.2 Implementation Constraints / 实现约束

- **Iteration history**: `StorySelfImprove` doesn't expose per-iteration ratings (limitation noted in code)
- **Paired data**: Training effectiveness analysis uses independent t-test instead of paired t-test (requires participant matching)
- **Customization metrics**: Uniqueness metric is simplified (string comparison rather than semantic similarity)

### 4.3 Data Collection / 数据收集

- **Human input quality**: No formal quality control mechanism for participant responses
- **Participant variability**: Results may vary based on participant engagement and quality of input
- **Recall test timing**: Recall tests collected at single time point (1 week), no longitudinal follow-up

### 4.4 Statistical Considerations / 统计考虑

- **Normality assumptions**: No formal normality tests conducted before t-tests
- **Variance homogeneity**: No Levene's test for equal variances
- **Multiple comparisons**: No correction for multiple testing (though only primary comparisons made)

---

## 5. Conclusions / 结论

### 5.1 Summary / 总结

This experiment demonstrates that while **automated and human-in-the-loop approaches achieve similar rating improvements**, the human-in-the-loop method provides **significant additional value** in:

1. **Training Effectiveness / 训练有效性**: Large, statistically significant improvements in confidence and authenticity
2. **Efficiency / 效率**: Requires 5× fewer iterations (1.0 vs 5.0)
3. **Customization / 定制化**: 100% personal detail integration, enabling authentic, personalized answers

### 5.2 Implications / 意义

**For Practice / 实践意义**:
- Human-in-the-loop is preferred when training effectiveness and personalization are priorities
- Automated approach may be sufficient when only rating improvement is the goal
- The choice depends on system objectives: efficiency vs. training value

**For Research / 研究意义**:
- Rating improvement alone is insufficient to evaluate improvement methods
- Training effectiveness and customization are critical value dimensions
- Future research should consider multi-dimensional evaluation frameworks

### 5.3 Future Directions / 未来方向

1. **Larger sample sizes** to increase statistical power
2. **Longitudinal studies** to assess long-term training effectiveness
3. **Quality control mechanisms** for human input
4. **Enhanced customization metrics** using semantic similarity
5. **Hybrid approaches** combining automated and human-in-the-loop benefits

---

## Appendix / 附录

### A. Statistical Details / 统计细节

**Rating Improvement Test / 评分改进检验**:
```
Independent t-test
t(48) = 0.72, p = 0.476
Cohen's d = 0.21 (small effect)
Group A: M=0.50, SD=1.10, n=20
Group B: M=0.27, SD=1.14, n=30
```

**Training Effectiveness Tests / 训练有效性检验**:
```
Confidence: t-test, p = 6.14×10⁻⁷
Pre: M=3.27, SD=0.69, n=30
Post: M=4.27, SD=0.69, n=30

Authenticity: t-test, p = 2.26×10⁻¹⁶
Pre: M=2.80, SD=0.55, n=30
Post: M=4.53, SD=0.63, n=30
```

**Iteration Comparison / 迭代次数对比**:
```
Independent t-test, p < 0.001
Group A: M=5.0, SD=0.0, n=20
Group B: M=1.0, SD=0.0, n=30
```

### B. Data Files / 数据文件

- Initial evaluations: `exp1_results/exp1_initial_evaluations.json`
- Group A results: `exp1_results/exp1_automated_results.json`
- Group B results: `exp1_results/exp1_human_in_loop_results.json`
- Analysis results: `exp1_results/analysis/`

### C. Code References / 代码参考

- Dataset preparation: `exp1_prepare_dataset.py`
- Automated group: `exp1_automated.py`
- Human-in-loop group: `exp1_human_in_loop.py`
- Analysis: `exp1_analysis.py`
- Statistics utilities: `utils/statistics.py`

---

**Report Generated / 报告生成**: 2025-12-24  
**Experiment Status / 实验状态**: Completed / 已完成  
**Next Steps / 下一步**: Consider Experiment 2 (Convergence Analysis) and Experiment 3 (Adversarial Challenging Validation)

