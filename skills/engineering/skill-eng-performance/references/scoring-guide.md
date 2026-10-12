# Performance Scoring Guide

This guide defines how findings from `SKILL.md` rules PERF01–PERF14 are classified and how the performance dimension score and merge-blocking decisions are calculated directly on a native **0.0–10.0 scale** for the Code Review Portal's Scorecard Aggregator.

---

## 1. Severity Classification & Base Deductions

Severity reflects the **demonstrated or supported impact** on latency, throughput, memory, database load, and Core Web Vitals across rules PERF01–PERF14 (e.g. execution blocking PERF01, N+1 queries PERF02, memory leaks PERF03, caching strategy PERF04, timeouts PERF05, LLM context efficiency PERF06, unbounded concurrency PERF07, redundant computations PERF08, missing indexes PERF09, pagination bounds PERF10, render cascades PERF11, bundle delivery PERF12, asset efficiency PERF13, and state subscriptions PERF14).

| Severity | Base Deduction (0–10 Scale) | Definition & Performance Impact |
|---|---|---|
| **critical** | 6.0 | Causes service degradation, outages, severe user-facing latency, or OOM crashes at realistic load with clear direct evidence. Triggers unconditional merge block. |
| **high** | 4.0 | Materially degrades performance under normal or peak load; known anti-pattern with clear latency or cost impact (e.g. unbounded N+1 query loop, blocking sync I/O in async request loop). |
| **medium** | 2.0 | Degrades performance under identifiable conditions (high volume, large payloads) but manageable at current scale (e.g. missing HTTP client timeout, unindexed query on moderate table). |
| **low** | 1.0 | Minor or localized latency concern; pattern acceptable at current scale (e.g. missing minor asset dimensions, sub-optimal static re-computation). |

---

## 2. Confidence and Uncertainty Handling

Confidence measures how strongly code evidence and profiler/execution context support a finding:

| Confidence | Multiplier | Definition |
|---|---|---|
| **high** | 1.00 | Finding is directly visible in the diff with clear, unambiguous evidence and straightforward impact path. |
| **medium** | 0.70 | Finding is plausible from code patterns, but full runtime context (data volume, traffic) is partially visible. |
| **low** | 0.30 | Concern is speculative; available evidence is insufficient to confirm a production bottleneck. |

**Low-confidence concerns must not be reported as findings.** Instead, record an `uncertainty_note` at the dimension level (0.0 score deduction).

---

## 3. Native 0–10 Score Calculation

Performance scores are calculated directly on a **0.0 to 10.0 scale** from start to finish without any intermediate 0–100 calculation or division:

```
deduction = round(base_deduction × confidence_multiplier)
final_score = max(0.0, min(10.0, 10.0 - sum(deductions)))
```

- **Starting Score:** Initialized at `10.0`.
- **Deductions:** Applied directly on the 0–10 scale.
- **Precision:** Rounded to one decimal place (`X.X`) and clamped within `[0.0, 10.0]`.

### Deduplication and Documented Exceptions
- **Duplicate Findings:** A single underlying performance defect (e.g. unindexed query inside an N+1 loop) produces **one primary finding** under the root-cause rule ID (PERF01–PERF14).
- **Approved Exceptions:** Documented trade-offs (ADRs or PR notes) reduce deductions by **50%** with `status: "accepted"`.

---

## 4. Standard Scoring and Blocking Rubric

The performance review enforces the standard merge-blocking policy:

| Score | Status | Description & Blocking Rule |
|---|---|---|
| **10.0 (10/10)** | ✅ **Pass** | **Zero confirmed violations.** Highly efficient resource utilization and execution. |
| **9.0 (9/10)** | ✅ **Pass with minor issues** | **At most one minor (low) non-blocking violation.** No medium, high, or critical performance regressions. |
| **Below 9.0 (< 9/10)** | 🔴 **Block** | **Merge Blocked (`blocked: true`).** Two or more minor issues, or any medium/high violation. |
| **Critical Override** | 🔴 **Block** | **Merge Blocked (`blocked: true`).** Any confirmed critical violation blocks merge unconditionally regardless of numeric score. |

---

## 5. Scorecard Aggregator Integration & Global Review Decision

The performance review skill produces an evaluation object conforming to the global Scorecard Aggregator contract using native 0–10 scoring:

```json
{
  "dimension": "performance",
  "score": 9.0,
  "findings": [
    {
      "ruleId": "PERF13",
      "title": "Static Image Missing Explicit Width and Height Attributes",
      "severity": "low",
      "confidence": "high",
      "file": "src/components/FooterLogo.tsx",
      "lineStart": 15,
      "lineEnd": 22,
      "evidence": "Image tag lacks explicit width and height dimensions",
      "impact": "Minor risk of localized layout shift on slow connections",
      "recommendation": "Add width={120} height={40} attributes to image tag",
      "technology": "React/TypeScript",
      "status": "open"
    }
  ],
  "uncertainty_notes": [],
  "blocked": false
}
```

### Global Review Decision
1. **Dimension Evaluation:** Returns `score` (0.0–10.0) and `blocked` (`blocked: true` if score $< 9.0$ or critical violation present).
2. **Global Aggregate:** The global review passes **only if every evaluated dimension passes** ($\text{score} \ge 9.0$ and $\text{blocked} = \text{false}$). If any dimension is blocked, the global review is marked blocked.
