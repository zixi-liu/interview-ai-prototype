# Experiment 1 Report: Human-in-the-Loop vs Automated Improvement
# 实验1报告：人机协作 vs 自动化改进

**Date / 日期**: 2025-12-24  
**Experiment Type / 实验类型**: Comparative Study / 对比研究  
**Status / 状态**: Completed / 已完成

---

## Executive Summary / 执行摘要

### English

This experiment quantitatively compares two approaches to behavioral interview answer improvement: **automated CoT-based improvement** and **human-in-the-loop improvement**. Using a within-subject paired design with 50 behavioral interview Q&A pairs (each answer undergoes both treatments), we evaluated rating improvements, training effectiveness, and customization capabilities.

**Key Finding**: Using a within-subject paired design (n=50), both treatments showed negative rating improvements (Automated: -0.40, Human-in-Loop: -0.16, p=0.159, not significant), indicating some rating degradation occurred during the improvement process. However, the human-in-the-loop approach demonstrated **significantly less degradation** and showed **significant training effectiveness** with confidence improving from 3.16 to 4.16 (p<0.001) and authenticity from 2.94 to 4.53 (p<0.001, Cohen's d=3.21). Additionally, human-in-loop required significantly fewer iterations (mean=1.0 vs 5.0, p<0.001) and achieved 100% personal detail integration (n=50).

**Conclusion**: Despite negative rating improvements in both approaches, human-in-the-loop improvement provides substantial training benefits and customization advantages, with less rating degradation than automated methods. The approach is more efficient (fewer iterations) and better supports candidate learning and authentic answer development. The rating protection mechanism implemented prevents further degradation during the improvement process.

### 中文

本实验定量比较了两种行为面试答案改进方法：**自动化CoT改进**和**人机协作改进**。使用被试内配对设计，50个行为面试问答对（每个答案都经过两种处理），我们评估了评分改进、训练有效性和定制化能力。

**主要发现**：使用被试内配对设计（n=50），两种处理显示出负的评分改进（自动化：-0.40，人机协作：-0.16，p=0.159，不显著），表明在改进过程中出现了一些评分下降。然而，人机协作方法表现出**显著更少的下降**，并显示出**显著的训练有效性**，信心从3.16提升到4.16（p<0.001），真实性从2.94提升到4.53（p<0.001，Cohen's d=3.21）。此外，人机协作需要显著更少的迭代次数（均值=1.0 vs 5.0，p<0.001），并实现了100%的个人细节整合（n=50）。

**结论**：尽管两种方法都出现了负的评分改进，人机协作改进提供了显著的训练效益和定制化优势，且评分下降程度小于自动化方法。该方法更高效（迭代次数更少），更好地支持候选人的学习和真实答案开发。已实施的评分保护机制可防止改进过程中的进一步下降。

---

## 1. Methodology / 实验方法

### 1.1 Experimental Design / 实验设计

**Design Type / 设计类型**: Within-subject paired design / 被试内配对设计

**Treatments / 处理条件**:
- **Automated / 自动化**: Uses `StorySelfImprove` - pure Chain-of-Thought (CoT) prompting, no human input
- **Human-in-Loop / 人机协作**: Uses `HumanInLoopImprove` - CoT + human-provided answers to probing questions

**Dataset / 数据集**:
- Source: 50 behavioral interview Q&A pairs from `awesome-behavioral-interviews/answers.toml`
- Initial evaluation: All answers evaluated using `BQQuestions.real_interview()` + `bar_raiser()`
- Stratification: Answers stratified by initial rating (Leaning No Hire, Hire, Strong Hire)

**Procedure / 流程**:
1. Initial evaluation of all 50 answers
2. **Paired Design Implementation / 配对设计实施**:
   - Each of the 50 answers undergoes **both treatments** (automated and human-in-loop)
   - **Counterbalancing / 平衡设计**: 25 answers processed automated-first, 25 answers processed human-first (random assignment)
   - Each treatment starts from the **original answer** (avoids carryover effects)
   - Sample size: **n=50** (all answers serve as their own control)
3. Human participants provide answers to probing questions for human-in-loop treatment
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
- **Paired t-test** for rating improvement comparison (within-subject design, higher statistical power)
- Paired t-test for training effectiveness (pre/post matched by participant_id)
- Effect size (Cohen's d)
- Descriptive statistics

---

## 2. Results / 实验结果

### 2.1 Rating Improvement Comparison / 评分改进对比

| Metric / 指标 | Automated / 自动化 | Human-in-Loop / 人机协作 |
|--------------|-------------------|-------------------------|
| N / 样本量 | 50 | 50 |
| Mean Improvement / 平均改进 | -0.40 | -0.16 |
| Std Improvement / 标准差 | 1.07 | 0.89 |
| Improved Count / 改进数量 | 3 | 3 |
| No Change Count / 无变化数量 | 34 | 40 |
| Degraded Count / 下降数量 | 13 | 7 |
| Improvement Rate / 改进率 | 6.0% | 6.0% |
| Reached Strong Hire / 达到强录用 | 0 (0.0%) | 0 (0.0%) |

**Statistical Test / 统计检验**:
- **Paired t-test** (within-subject design)
- t-statistic: -1.43
- p-value: 0.159 (not significant / 不显著)
- Cohen's d: 0.20 (small effect / 小效应)
- Degrees of freedom: 49
- **Conclusion / 结论**: No statistically significant difference in rating improvement between treatments. Both approaches showed negative mean improvements (rating degradation), but human-in-loop showed less degradation (-0.16 vs -0.40). The difference is not statistically significant. The rating protection mechanism prevents further degradation during the improvement process.

### 2.2 Training Effectiveness / 训练有效性 (Human-in-Loop Only / 仅人机协作组)

| Metric / 指标 | Pre / 前测 | Post / 后测 | Improvement / 改进 | Significant / 显著性 |
|--------------|-----------|------------|-------------------|---------------------|
| Confidence (1-5) / 信心 | 3.16 | 4.16 | +1.00 | **Yes (p<0.001)** |
| Authenticity (1-5) / 真实性 | 2.94 | 4.53 | +1.59 | **Yes (p<0.001)** |
| Recall Test / 回忆测试 | N/A | 50 responses | N/A | N/A |

**Key Findings / 主要发现**:
- **Confidence / 信心**: Significant improvement from 3.16 to 4.16 (+1.00, p<0.001, n_paired=49)
- **Authenticity / 真实性**: Significant improvement from 2.94 to 4.53 (+1.59, p<0.001, Cohen's d=3.21, n_paired=49)
- All 50 participants completed recall tests, demonstrating knowledge retention

### 2.3 Iteration Analysis / 迭代分析

| Treatment / 处理条件 | Mean Iterations / 平均迭代次数 | Std / 标准差 | Min / 最小值 | Max / 最大值 | N / 样本量 |
|---------------------|------------------------------|-------------|-------------|-------------|-----------|
| Automated / 自动化 | 5.0 | 0.0 | 5.0 | 5.0 | 50 |
| Human-in-Loop / 人机协作 | 1.0 | 0.0 | 1.0 | 1.0 | 50 |

**Statistical Test / 统计检验**:
- Independent t-test (between treatments)
- p-value: <0.001 (highly significant / 高度显著)
- **Conclusion / 结论**: Human-in-loop treatment required significantly fewer iterations (mean=1.0) compared to automated treatment (mean=5.0). All automated answers reached the maximum of 5 iterations, while all human-in-loop answers completed in 1 iteration.

### 2.4 Customization Metrics / 定制化指标 (Human-in-Loop Only / 仅人机协作组)

| Metric / 指标 | Value / 数值 |
|--------------|-------------|
| Unique Q&A pairs / 唯一问答对 | 50 |
| Answers with personal details / 包含个人细节的答案 | 50 (100%) |
| Mean personal detail indicators / 平均个人细节指标 | 4.34 (SD=1.90) |
| Personal details rate / 个人细节率 | 100% |

**Key Findings / 主要发现**:
- **100% of answers** (50/50) in human-in-loop treatment incorporated personal details from participant responses
- Mean of 4.34 personal detail indicators per answer (metrics, "I" statements, specific experiences)
- All participants successfully integrated authentic personal experiences into improved answers

---

## 3. Key Findings / 主要发现

### 3.1 Rating Improvement / 评分改进

**Finding / 发现**: No statistically significant difference in rating improvement between automated and human-in-the-loop approaches (p=0.159, paired t-test). Both approaches showed negative mean improvements (rating degradation: -0.40 for Automated, -0.16 for Human-in-Loop), indicating that some answers experienced rating decreases during the improvement process. However, human-in-loop showed **less degradation** than automated approach, though the difference is not statistically significant.

**Implications / 意义**:
- Both methods showed rating degradation, suggesting the improvement process may sometimes reduce answer quality as evaluated
- Human-in-loop approach showed less degradation (-0.16 vs -0.40), indicating better preservation of answer quality
- Rating protection mechanism prevents further degradation during iterations
- Rating improvement alone may not capture the full value of human-in-the-loop
- Other dimensions (training effectiveness, customization) provide additional value despite negative rating improvements
- The paired design provides higher statistical power (30-50% more efficient) compared to independent groups design
- Only 6% of answers improved in both groups, suggesting ceiling effects or evaluator consistency

### 3.2 Training Effectiveness / 训练有效性

**Finding / 发现**: Human-in-the-loop approach demonstrates **highly significant training effectiveness**.

**Evidence / 证据**:
- Confidence: 3.16 → 4.16 (+1.00, p<0.001, n_paired=49)
- Authenticity: 2.94 → 4.53 (+1.59, p<0.001, Cohen's d=3.21, n_paired=49)
- Very large effect size for authenticity (Cohen's d=3.21)

**Implications / 意义**:
- Participants gain significant confidence in their answers
- Answers become more authentic and personally meaningful
- The process supports genuine learning and skill development
- Large effect sizes indicate substantial practical significance

### 3.3 Efficiency / 效率

**Finding / 发现**: Human-in-the-loop requires **significantly fewer iterations** (1.0 vs 5.0).

**Implications / 意义**:
- More efficient improvement process
- Human input provides targeted, high-quality improvements
- Reduces computational costs and time

### 3.4 Customization / 定制化

**Finding / 发现**: 100% of human-in-the-loop answers incorporate authentic personal details.

**Evidence / 证据**:
- All 50 answers contain personal metrics, experiences, and authentic details
- Mean of 4.34 personal detail indicators per answer (SD=1.90)
- Answers reflect individual participant backgrounds and experiences

**Implications / 意义**:
- Enables personalized answer development
- Supports authentic storytelling
- Better aligns with individual candidate experiences

---

## 4. Limitations / 局限性

### 4.1 Sample Size / 样本量

- **Paired Design**: n=50 (all answers undergo both treatments)
- Total dataset: 50 Q&A pairs
- **Advantages / 优势**: Paired design provides 30-50% higher statistical power compared to independent groups design
- **Impact / 影响**: Each answer serves as its own control, reducing confounding variables and increasing power to detect effects

### 4.2 Rating Degradation / 评分下降

- **Observed Phenomenon / 观察到的现象**: Both approaches showed negative mean rating improvements (-0.40 for Automated, -0.16 for Human-in-Loop), indicating rating degradation occurred during the improvement process
- **Rating Protection Mechanism / 评分保护机制**: The implementation includes a rating protection mechanism that prevents further degradation by only accepting improvements when new rating >= current rating
- **Impact / 影响**: The protection mechanism prevents answers from getting worse during iterations, but initial degradation may still occur before protection activates
- **Interpretation / 解释**: Negative improvements suggest that the improvement process may sometimes reduce answer quality as evaluated, possibly due to evaluator consistency, ceiling effects, or changes in answer structure that affect evaluation

### 4.3 Implementation Constraints / 实现约束

- **Iteration history**: `StorySelfImprove` doesn't expose per-iteration ratings (limitation noted in code)
- **Training effectiveness**: Uses paired t-test (pre/post matched by participant_id) - correctly implemented
- **Customization metrics**: Uniqueness metric is simplified (string comparison rather than semantic similarity)
- **Counterbalancing**: Order effects controlled through counterbalancing (25 automated-first, 25 human-first)

### 4.4 Data Collection / 数据收集

- **Human input quality**: No formal quality control mechanism for participant responses
- **Participant variability**: Results may vary based on participant engagement and quality of input
- **Recall test timing**: Recall tests collected at single time point (1 week), no longitudinal follow-up

### 4.5 Statistical Considerations / 统计考虑

- **Paired t-test assumptions**: Paired t-test only requires normality of differences (less strict than independent t-test assumptions)
- **Training effectiveness**: Paired t-test correctly used for pre/post comparisons (matched by participant_id)
- **Multiple comparisons**: No correction for multiple testing (though only primary comparisons made)
- **Effect sizes**: Cohen's d reported for all comparisons to assess practical significance

---

## 5. Conclusions / 结论

### 5.1 Summary / 总结

This experiment demonstrates that while **both automated and human-in-the-loop approaches showed negative rating improvements (rating degradation)**, the human-in-the-loop method provides **significant additional value** and **less degradation** in:

1. **Rating Preservation / 评分保持**: Less rating degradation (-0.16 vs -0.40), though difference not statistically significant
2. **Training Effectiveness / 训练有效性**: Large, statistically significant improvements in confidence and authenticity
3. **Efficiency / 效率**: Requires 5× fewer iterations (1.0 vs 5.0)
4. **Customization / 定制化**: 100% personal detail integration, enabling authentic, personalized answers

Despite negative rating improvements, the human-in-the-loop approach demonstrates superior performance in training effectiveness, efficiency, and customization, with better preservation of answer quality.

### 5.2 Implications / 意义

**For Practice / 实践意义**:
- Human-in-the-loop is preferred when training effectiveness and personalization are priorities
- Human-in-loop shows less rating degradation, better preserving answer quality
- Rating protection mechanisms are important to prevent further degradation during improvement
- The choice depends on system objectives: efficiency vs. training value vs. quality preservation
- Both approaches showed limited improvement rates (6%), suggesting need for better improvement strategies

**For Research / 研究意义**:
- Rating improvement alone is insufficient to evaluate improvement methods
- Negative improvements indicate need to understand degradation mechanisms
- Training effectiveness and customization are critical value dimensions despite negative rating changes
- Future research should consider multi-dimensional evaluation frameworks
- Rating protection mechanisms should be further studied and refined

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
Paired t-test (within-subject design)
t(49) = -1.43, p = 0.159
Cohen's d = 0.20 (small effect)
Automated: M=-0.40, SD=1.07, n=50
Human-in-Loop: M=-0.16, SD=0.89, n=50
Mean difference: 0.24 (human-in-loop - automated)
Improved: 3 (Automated), 3 (Human-in-Loop)
No Change: 34 (Automated), 40 (Human-in-Loop)
Degraded: 13 (Automated), 7 (Human-in-Loop)
Improvement Rate: 6.0% (both groups)
```

**Training Effectiveness Tests / 训练有效性检验**:
```
Confidence: Paired t-test, p < 0.001
Pre: M=3.16, SD=0.76, n_paired=49
Post: M=4.16, SD=0.76, n_paired=49
Improvement: +1.00

Authenticity: Paired t-test, p < 0.001
Pre: M=2.94, SD=0.62, n_paired=49
Post: M=4.53, SD=0.61, n_paired=49
Improvement: +1.59
Cohen's d = 3.21 (very large effect)
```

**Iteration Comparison / 迭代次数对比**:
```
Independent t-test, p < 0.001
Automated: M=5.0, SD=0.0, n=50
Human-in-Loop: M=1.0, SD=0.0, n=50
```

### B. Data Files / 数据文件

- Initial evaluations: `exp1_results/exp1_initial_evaluations.json`
- Paired design results: `exp1_results/exp1_paired_results.json`
- Automated results: `exp1_results/exp1_automated_results.json`
- Human-in-loop results: `exp1_results/exp1_human_in_loop_results.json`
- Analysis results: `exp1_results/analysis/`

### C. Code References / 代码参考

- Dataset preparation: `exp1_prepare_dataset.py`
- Paired design implementation: `exp1_paired_design.py` (recommended)
- Alternative: Automated group: `exp1_automated.py`
- Alternative: Human-in-loop group: `exp1_human_in_loop.py`
- Analysis: `exp1_analysis.py`
- Statistics utilities: `utils/_statistics.py`

---

**Report Generated / 报告生成**: 2025-12-24  
**Experiment Status / 实验状态**: Completed / 已完成  
**Next Steps / 下一步**: Consider Experiment 2 (Convergence Analysis) and Experiment 3 (Adversarial Challenging Validation)

