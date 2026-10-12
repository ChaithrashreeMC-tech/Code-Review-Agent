# Maintainability Scoring Guide

This guide defines how findings from `SKILL.md` rules MAINT01–MAINT14 are classified and how the maintainability dimension score and merge-blocking decisions are calculated directly on a native **0.0–10.0 scale** for the Code Review Portal's Scorecard Aggregator.

---

## 1. Severity Classification & Base Deductions

Severity reflects the **demonstrated impact** of the maintainability defect on code comprehension, defect risk, testability, and modification costs across rules MAINT01–MAINT14 (e.g. duplication MAINT01, complex control flow MAINT02, misleading naming MAINT03, multi-responsibility methods MAINT04, tight coupling MAINT05, god classes MAINT06, swallowed errors MAINT07, magic literals MAINT08, testability obstacles MAINT09, leaky abstractions MAINT10, dead code MAINT11, contract documentation MAINT12, shotgun surgery MAINT13, and framework anti-patterns MAINT14).

| Severity | Base Deduction (0–10 Scale) | Definition & Maintainability Impact |
|---|---|---|
| **critical** | 6.0 | Severe architectural defect that causes high defect risk, prevents unit testing entirely, conceals runtime data loss, or creates catastrophic coupling. Triggers unconditional merge block. |
| **high** | 4.0 | Major maintainability impediment: deeply tangled control flow, swallowed exceptions, core calculation duplication, hardcoded credentials, or captive DI dependencies. |
| **medium** | 2.0 | Moderate maintainability risk: multi-responsibility methods, scattered magic numbers, undocumented complex algorithms, or un-memoized complex selectors. |
| **low** | 1.0 | Minor code smell, naming ambiguity, or cosmetic maintenance opportunity with low defect risk. |

---

## 2. Confidence and Uncertainty Handling

Confidence measures how strongly code evidence supports a finding:

| Confidence | Multiplier | Definition |
|---|---|---|
| **high** | 1.00 | Finding is directly visible in the diff with clear, unambiguous evidence of maintainability harm. |
| **medium** | 0.70 | Pattern is visibly risky, but full repository context (callers, test suites) is only partially visible. |
| **low** | 0.30 | Concern is speculative or depends on unverified future modifications. |

**Low-confidence concerns must not be reported as findings.** Instead, record an `uncertainty_note` at the dimension level (0.0 score deduction).

---

## 3. Native 0–10 Score Calculation

Maintainability scores are calculated directly on a **0.0 to 10.0 scale** from start to finish without any intermediate 0–100 calculation or division:

```
deduction = round(base_deduction × confidence_multiplier)
final_score = max(0.0, min(10.0, 10.0 - sum(deductions)))
```

- **Starting Score:** Initialized at `10.0`.
- **Deductions:** Applied directly on the 0–10 scale.
- **Precision:** Rounded to one decimal place (`X.X`) and clamped within `[0.0, 10.0]`.

### Deduplication and Documented Exceptions
- **Duplicate Findings:** Multiple symptoms stemming from one underlying design flaw produce **one primary finding** under the most specific applicable rule ID (MAINT01–MAINT14).
- **Approved Exceptions:** Documented trade-offs (ADRs or PR notes) reduce deductions by **50%** with `status: "accepted"`.

---

## 4. Standard Scoring and Blocking Rubric

The maintainability review enforces the standard merge-blocking policy:

| Score | Status | Description & Blocking Rule |
|---|---|---|
| **10.0 (10/10)** | ✅ **Pass** | **Zero confirmed violations.** Clean, readable, and highly maintainable code. |
| **9.0 (9/10)** | ✅ **Pass with minor issues** | **At most one minor (low) non-blocking violation.** No medium, high, or critical maintainability risks. |
| **Below 9.0 (< 9/10)** | 🔴 **Block** | **Merge Blocked (`blocked: true`).** Two or more minor issues, or any medium/high violation. |
| **Critical Override** | 🔴 **Block** | **Merge Blocked (`blocked: true`).** Any confirmed critical violation blocks merge unconditionally regardless of numeric score. |

---

## 5. Scorecard Aggregator Integration & Global Review Decision

The maintainability review skill produces an evaluation object conforming to the global Scorecard Aggregator contract using native 0–10 scoring:

```json
{
  "dimension": "maintainability",
  "score": 9.0,
  "findings": [
    {
      "ruleId": "MAINT03",
      "title": "Ambiguous Variable Name in Helper Function",
      "severity": "low",
      "confidence": "high",
      "file": "src/utils/formatters.py",
      "lineStart": 14,
      "lineEnd": 20,
      "evidence": "Variable named 'tmp' used to store intermediate price string",
      "impact": "Minor readability issue; localized to private helper function",
      "recommendation": "Rename 'tmp' to 'formatted_price'",
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
