# Venue Selection & Submission Timeline

> Optimized for NIW/EB1A immigration goals: prioritize speed-to-publication, venue prestige, and topic relevance to AI fairness/policy.

---

## 1. Venue Ranking

### Tier 1: Primary Targets (Best Fit)

| Venue | Fit Score | Why | Deadline (approx.) | Notification | Format |
|-------|-----------|-----|--------------------|--------------|----- |
| **FAccT 2027** | 10/10 | AI fairness + accountability; directly addresses hiring AI auditing | Jan 2027 | Mar 2027 | 10 pages + refs |
| **EMNLP 2026** | 8/10 | Top empirical NLP venue; strong LLM-as-Judge community | Jun 2026 | Sep 2026 | 8 pages + refs |
| **AIES 2027** | 8/10 | AAAI/ACM AI Ethics + Society; directly relevant | Feb 2027 | Apr 2027 | 8 pages + refs |

### Tier 2: Strong Alternatives

| Venue | Fit Score | Why | Deadline (approx.) | Format |
|-------|-----------|-----|--------------------|----- |
| **CHI 2027** | 7/10 | HCI + human-AI decision making framing | Sep 2026 | 10 pages |
| **NAACL 2027** | 7/10 | NLP venue; empirical study track | Jan 2027 | 8 pages |
| **NeurIPS 2026 Datasets & Benchmarks** | 7/10 | Benchmark track; good for the dataset contribution | May 2026 | 9 pages |

### Tier 3: Workshops & Short Papers (Fast Publication)

| Venue | Why | Deadline |
|-------|-----|----------|
| **EMNLP 2026 Workshop on NLP and AI for HR** | Niche audience, fast turnaround | Aug 2026 |
| **FAccT 2027 Workshop** | If main track rejected, pivot to workshop | Jan 2027 |
| **ACL 2027 Findings** | Good visibility, slightly lower bar than main | Feb 2027 |

### Preprint (Immediate)

| Platform | Why | Timeline |
|----------|-----|----------|
| **arXiv (cs.CL + cs.AI)** | Timestamp priority, immediate visibility, citation accumulation | ASAP |

---

## 2. Recommended Strategy

### Primary Path: arxiv → EMNLP 2026 → FAccT 2027

```
Apr 2026: arXiv preprint (immediate visibility)
    ↓
Jun 2026: Submit to EMNLP 2026 main conference
    ↓
Sep 2026: EMNLP notification
    ├─ Accepted → Present at EMNLP (Nov 2026), use for NIW
    └─ Rejected → Revise, submit to FAccT 2027 (Jan 2027)
        ↓
    Mar 2027: FAccT notification
        ├─ Accepted → Present at FAccT (Jun 2027)
        └─ Rejected → NAACL 2027 or AIES 2027
```

### Parallel Track: NIW Filing

```
Apr 2026: arXiv preprint published
    ↓
May 2026: Begin NIW petition preparation
    - arXiv preprint as evidence of scholarly contribution
    - System code as evidence of technical capability
    - Recommendation letters (start requesting)
    ↓
Jul-Aug 2026: File NIW petition
    - arXiv preprint (does NOT need to be peer-reviewed for NIW)
    - System documentation
    - Recommendation letters (3-5)
    - Petition letter emphasizing national importance
    ↓
Sep 2026: If EMNLP accepted, supplement NIW with acceptance letter
```

---

## 3. Detailed Timeline

### Phase 1: Paper Completion (Now → April 15, 2026)

| Week | Task | Deliverable |
|------|------|-------------|
| Mar 28 – Apr 3 | Run `paper_stats.py`, verify all statistical tests | `paper_statistical_tests.json` |
| Mar 28 – Apr 3 | Run `paper_figures.py`, iterate on figure quality | 7 publication figures (PNG + PDF) |
| Apr 4 – Apr 8 | Finalize paper draft, incorporate stats + figures | Complete `paper_draft.md` |
| Apr 9 – Apr 11 | Internal review, polish writing, check references | Revised draft |
| Apr 12 – Apr 14 | Format for arXiv (LaTeX conversion) | `paper.tex` + figures |
| Apr 15 | **Submit to arXiv** | arXiv ID |

### Phase 2: Optional Human Study (Apr 15 → May 5, 2026)

| Week | Task | Deliverable |
|------|------|-------------|
| Apr 15 – Apr 21 | Recruit 3-5 human raters | Confirmed participants |
| Apr 22 – Apr 28 | Collect human ratings | `human_ratings.jsonl` |
| Apr 29 – May 2 | Analyze human-LLM agreement | Updated stats + new section |
| May 3 – May 5 | Update arXiv with human data | arXiv v2 |

### Phase 3: Conference Submission (May → Jun 2026)

| Date | Task |
|------|------|
| May 2026 | Format paper for EMNLP (ACL format, 8 pages) |
| Jun 2026 | **Submit to EMNLP 2026** |
| Jun – Sep 2026 | Address reviewer comments if shepherded |

### Phase 4: NIW Preparation (May → Aug 2026)

| Date | Task |
|------|------|
| May 2026 | Draft NIW petition letter |
| May – Jun 2026 | Request recommendation letters (3-5 experts) |
| Jun – Jul 2026 | Compile evidence package |
| Aug 2026 | **File NIW petition** |

---

## 4. Venue-Specific Formatting Notes

### arXiv
- No page limit
- Use current draft format (markdown → LaTeX conversion)
- Cross-list: cs.CL (primary), cs.AI, cs.CY (computers & society)
- Keywords in metadata: "LLM evaluation", "AI hiring", "algorithmic auditing"

### EMNLP 2026
- 8 pages + unlimited references (ACL format)
- Requires: Abstract, anonymized submission
- Appendices allowed (unlimited) — put full tables here
- Reproducibility checklist required

### FAccT 2027
- 10 pages + references (ACM format)
- Requires: Positionality statement, broader impact
- Emphasis on policy implications — expand Section 6.2
- Non-anonymous submission (authors visible)

### CHI 2027
- 10 pages (ACM CHI format)
- Would need to add "human factors" framing
- Expand implications for job seekers and HR practitioners

---

## 5. NIW-Specific Considerations

### What Counts as "Published" for NIW

NIW does not strictly require peer review. The following all count as evidence:

| Evidence Type | Weight | Status |
|--------------|--------|--------|
| arXiv preprint | Medium | Available after Phase 1 |
| Conference acceptance letter | High | Available after Phase 3 |
| Published proceedings paper | Highest | Available after conference |
| Open-source code (GitHub) | Medium | Available now |
| Media coverage / blog posts | Medium | Pursue in parallel |

### Recommendation Letters

Request letters from:

1. **AI/NLP professor** — someone who researches LLM evaluation or AI fairness (academic credibility)
2. **Senior engineer at FAANG** — someone who conducts behavioral interviews (domain expertise)
3. **HR tech industry expert** — someone familiar with AI hiring tools (industry relevance)
4. **Policy/legal expert** — someone working on AI regulation (national importance framing)
5. **(Optional) Co-author** — if any co-author is a known researcher, their endorsement adds weight

### Key Talking Points for NIW Petition Letter

1. **National importance**: AI hiring affects 100M+ US job applications annually. Unreliable AI evaluators create systematic unfairness in the labor market.
2. **First-of-its-kind**: No prior multi-model reliability audit of LLM interview evaluators exists.
3. **Policy relevance**: Findings directly inform compliance with NYC Local Law 144, EEOC AI guidance, and EU AI Act.
4. **Quantified impact**: Scale collapse (5→2 effective bins), 10x test-retest variability, same-brand disagreement (rho=0.25).
5. **Practical contribution**: Open-source auditing framework enables other researchers and regulators to replicate and extend.

---

## 6. EB1A Long-Term Roadmap (12–24 months)

| Timeline | Action | EB1A Criterion |
|----------|--------|---------------|
| Apr 2026 | arXiv preprint | Scholarly articles (partial) |
| Nov 2026 | EMNLP publication | Scholarly articles (full) |
| Dec 2026 – Jun 2027 | Accumulate 10+ citations | Original contribution |
| 2026–2027 | Accept 2-3 review invitations | Judging work of others |
| 2027 | Publish follow-up paper (human ground truth) | Scholarly articles (2nd) |
| 2027 | Media coverage (TechCrunch, MIT Tech Review) | Published material about the alien |
| Mid-2027 | Evaluate EB1A readiness (need 3 of 10 criteria) | File if ready |

### Citation Acceleration Strategies

1. **Twitter/X thread**: Summarize 5 findings with visuals. AI hiring is a high-engagement topic.
2. **LinkedIn post**: Target HR tech and recruiting communities.
3. **Blog post**: "We tested 9 AI models as job interviewers. Here's what we found." Medium / personal blog.
4. **Pitch to journalists**: MIT Tech Review, The Verge, TechCrunch regularly cover AI hiring bias stories.
5. **Reply to related papers**: When new LLM-as-Judge papers cite MT-Bench or Chatbot Arena, share your benchmark as a domain-specific alternative.
