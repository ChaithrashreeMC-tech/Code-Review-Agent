# Business Logic Scoring Guide

This guide defines how findings from `SKILL.md` rules BIZ01–BIZ10 are classified and how the business logic dimension score and merge-blocking decisions are calculated directly on a native **0.0–10.0 scale** for the Code Review Portal's Scorecard Aggregator.

---

## 1. Severity Classification & Base Deductions

Severity reflects the **demonstrated business and financial impact** of the finding on domain calculations, workflow transitions, data integrity, and compliance across rules BIZ01–BIZ10 (e.g. specification alignment BIZ01, calculation errors BIZ02, invalid state transitions BIZ03, invariant bypasses BIZ04, boundary defects BIZ05, data inconsistency BIZ06, swallowed business errors BIZ07, duplicate operations BIZ08, cross-layer divergence BIZ09, and missing acceptance criteria BIZ10).

| Severity | Base Deduction (0–10 Scale) | Definition & Business Impact |
|---|---|---|
| **critical** | 6.0 | Severe defect causing financial loss, silent data corruption, unauthorized state transition, compliance breach, or failure of a core business workflow. Triggers unconditional merge block. |
| **high** | 4.0 | Material defect in business calculation, missing domain validation rule, broken workflow transition, or cross-layer contract divergence causing operational failure. |
| **medium** | 2.0 | Defective edge-case boundary condition, unhandled business failure path, or omitted non-critical acceptance criteria degrading domain behavior under specific inputs. |
| **low** | 1.0 | Minor validation message discrepancy, cosmetic business label mismatch, or non-blocking domain detail variation. |

---

## 2. Confidence and Uncertainty Handling

Confidence measures how strongly specifications and code evidence substantiate a finding:

| Confidence | Multiplier | Definition |
|---|---|---|
| **high** | 1.00 | Requirement is explicitly documented in the spec; code diff directly contradicts or omits it. |
| **medium** | 0.70 | Requirement is reasonably inferred from domain context; code indicates probable defect. |
| **low** | 0.30 | Requirement is ambiguous or speculative; evidence is insufficient to prove a violation. |

**Low-confidence concerns must not be reported as findings.** Instead, record an `uncertainty_note` at the dimension level (0.0 score deduction) prompting specification clarification.

---

## 3. Native 0–10 Score Calculation

Business logic scores are calculated directly on a **0.0 to 10.0 scale** from start to finish without any intermediate 0–100 calculation or division:

```
deduction = round(base_deduction × confidence_multiplier)
final_score = max(0.0, min(10.0, 10.0 - sum(deductions)))
```

- **Starting Score:** Initialized at `10.0`.
- **Deductions:** Applied directly on the 0–10 scale.
- **Precision:** Rounded to one decimal place (`X.X`) and clamped within `[0.0, 10.0]`.

### Deduplication and Documented Exceptions
- **Duplicate Findings:** A single underlying business defect affecting multiple files or layers produces **one primary finding** under the most specific applicable rule ID (BIZ01–BIZ10).
- **Approved Exceptions:** Documented business rule exceptions (ADRs or linked tickets) reduce deductions by **50%** with `status: "accepted"`.

---

## 4. Standard Scoring and Blocking Rubric

The business logic review enforces the standard merge-blocking policy:

| Score | Status | Description & Blocking Rule |
|---|---|---|
| **10.0 (10/10)** | ✅ **Pass** | **Zero confirmed violations.** Core business logic and rules correctly implemented. |
| **9.0 (9/10)** | ✅ **Pass with minor issues** | **At most one minor (low) non-blocking violation.** No medium, high, or critical business logic defects. |
| **Below 9.0 (< 9/10)** | 🔴 **Block** | **Merge Blocked (`blocked: true`).** Two or more minor issues, or any medium/high violation. |
| **Critical Override** | 🔴 **Block** | **Merge Blocked (`blocked: true`).** Any confirmed critical violation blocks merge unconditionally regardless of numeric score. |

---

## 5. Scorecard Aggregator Integration & Global Review Decision

The business logic review skill produces an evaluation object conforming to the global Scorecard Aggregator contract using native 0–10 scoring:

```json
{
  "dimension": "business_logic",
  "score": 9.0,
  "findings": [
    {
      "ruleId": "BIZ04",
      "title": "Minor Validation Error Message Mismatch",
      "severity": "low",
      "confidence": "high",
      "file": "src/validators/user_validator.py",
      "lineStart": 22,
      "lineEnd": 28,
      "evidence": "Validation message uses 'Invalid zip' instead of spec 'Zip code must be 5 digits'",
      "impact": "Minor discrepancy; input validation logic functions correctly",
      "recommendation": "Update message string to match specification requirements",
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
