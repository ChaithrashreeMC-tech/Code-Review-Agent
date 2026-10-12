# Modularity Scoring Guide

This guide defines how findings from `SKILL.md` rules MOD01–MOD12 are classified and how the modularity dimension score and merge-blocking decisions are calculated directly on a native **0.0–10.0 scale** for the Code Review Portal's Scorecard Aggregator.

---

## 1. Severity Classification & Base Deductions

Severity reflects the **demonstrated architectural impact** on system maintainability, boundary isolation, testability, and coupling across rules MOD01–MOD12 (e.g. single responsibility MOD01, layer separation MOD02, domain boundaries MOD03, global clients MOD04, god classes MOD05, graph wiring MOD06, agent abstractions MOD07, handler isolation MOD08, data access MOD09, UI modularity MOD10, feature collocation MOD11, and cyclic dependencies MOD12).

| Severity | Base Deduction (0–10 Scale) | Definition & Modularity Impact |
|---|---|---|
| **critical** | 6.0 | Severe architectural violation causing system instability, broken layer isolation, cyclic dependency deadlock, or God Class controlling multiple distinct domain lifecycles. Triggers unconditional merge block. |
| **high** | 4.0 | Material defect compromising modularity: business logic in route handlers, persistence leaking into domain services, presentation coupled to direct network side-effects, or cross-domain private access. |
| **medium** | 2.0 | Moderate modularity concern: missing dependency injection, unencapsulated client instantiation, or excessive dependencies approaching threshold. |
| **low** | 1.0 | Minor modularity issue: non-optimal feature collocation or minor helper organization concern. |

---

## 2. Confidence and Uncertainty Handling

Confidence measures how strongly code evidence and architectural context substantiate a finding:

| Confidence | Multiplier | Definition |
|---|---|---|
| **high** | 1.00 | Finding is directly visible in the diff with clear, unambiguous evidence and direct structural harm. |
| **medium** | 0.70 | Finding is plausible from code patterns, but broader system architecture is only partially visible. |
| **low** | 0.30 | Speculative concern; available evidence is insufficient to confirm an architectural defect. |

**Low-confidence concerns must not be reported as findings.** Instead, record an `uncertainty_note` at the dimension level (0.0 score deduction).

---

## 3. Native 0–10 Score Calculation

Modularity scores are calculated directly on a **0.0 to 10.0 scale** from start to finish without any intermediate 0–100 calculation or division:

```
deduction = round(base_deduction × confidence_multiplier)
final_score = max(0.0, min(10.0, 10.0 - sum(deductions)))
```

- **Starting Score:** Initialized at `10.0`.
- **Deductions:** Applied directly on the 0–10 scale.
- **Precision:** Rounded to one decimal place (`X.X`) and clamped within `[0.0, 10.0]`.

### Deduplication and Documented Exceptions
- **Duplicate Findings:** Multiple symptoms sharing a single root cause (e.g., embedded SQL query in a controller violating MOD08 and MOD09) produce **one primary finding** under the most specific applicable rule ID (MOD01–MOD12).
- **Approved Exceptions:** Documented architectural trade-offs (ADRs or PR notes) reduce deductions by **50%** with `status: "accepted"`.

---

## 4. Standard Scoring and Blocking Rubric

The modularity review enforces the standard merge-blocking policy:

| Score | Status | Description & Blocking Rule |
|---|---|---|
| **10.0 (10/10)** | ✅ **Pass** | **Zero confirmed violations.** Clean architecture and strict boundary isolation. |
| **9.0 (9/10)** | ✅ **Pass with minor issues** | **At most one minor (low) non-blocking violation.** No high or critical architectural violations. |
| **Below 9.0 (< 9/10)** | 🔴 **Block** | **Merge Blocked (`blocked: true`).** Two or more minor issues, or any medium/high violation. |
| **Critical Override** | 🔴 **Block** | **Merge Blocked (`blocked: true`).** Any confirmed critical violation blocks merge unconditionally regardless of numeric score. |

---

## 5. Scorecard Aggregator Integration & Global Review Decision

The modularity review skill produces an evaluation object conforming to the global Scorecard Aggregator contract using native 0–10 scoring:

```json
{
  "dimension": "modularity",
  "score": 9.0,
  "findings": [
    {
      "ruleId": "MOD11",
      "title": "Feature Helper Located in Global Shared Folder",
      "severity": "low",
      "confidence": "high",
      "file": "src/utils/checkout_helper.py",
      "lineStart": 12,
      "lineEnd": 28,
      "evidence": "Feature-specific helper located in global /utils rather than /features/checkout",
      "impact": "Minor collocation issue; does not violate architectural layer boundaries",
      "recommendation": "Move helper to src/features/checkout/utils.py",
      "technology": "Python",
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
