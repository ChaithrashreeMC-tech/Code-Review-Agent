# Maintainability Scoring Guide

This guide defines how findings from `SKILL.md` rules MAINT01–MAINT14 are
classified and how the maintainability dimension score is calculated for the Code
Review Portal's Scorecard Aggregator.

---

## 1. Severity Classification

Severity reflects the **demonstrated impact** of the maintainability defect on code
comprehension, defect risk, testability, and the cost of future modifications. It must
not be inflated solely because code differs from a personal stylistic preference.

| Severity | Definition |
|---|---|
| **critical** | Severe architectural defect that directly causes high defect risk, prevents unit testing entirely, or creates catastrophic coupling/side-effects. |
| **high** | Major maintainability impediment: deeply tangled logic, unhandled swallowed errors hiding corrupt state, severe duplication in core rules, or captive DI dependencies. |
| **medium** | Moderate maintainability risk: functions with multiple responsibilities, scattered magic numbers, missing docstrings on tricky algorithms, or un-memoized complex selectors. |
| **low** | Minor code smell, minor naming ambiguity, or cosmetic maintenance opportunity with low risk of causing bugs or blocking future work. |

### Severity Anchors by Rule

| Rule | Critical Example | High Example | Medium Example | Low Example |
|---|---|---|---|---|
| MAINT01 | Critical billing rules copy-pasted across 4 modules with divergent edits | Duplicate authorization logic in 2 endpoints | Duplicate date formatting helper in 3 files | Incidental 2-line mapping logic in 2 places |
| MAINT02 | 7-level nested loop/conditional with 10+ boolean operators in financial math | 5-level nested conditionals with side-effects | 40-line complex if/else chain | Minor nested ternary expression |
| MAINT03 | Method named `checkAccess()` that secretly deletes records | Variable named `isValid` holding a user ID | Ambiguous variable name `data2` | Slightly verbose variable name |
| MAINT04 | 300-line method handling parsing, auth, DB queries, and email delivery | 100-line method with flag parameter splitting all logic | 60-line method doing formatting and logging | 25-line method with slightly mixed concerns |
| MAINT05 | Business logic directly instantiates raw socket connection preventing mock | Core service directly invokes concrete DB provider | Law of Demeter violation crossing 4 objects | Minor direct dependency on concrete utility class |
| MAINT06 | Omnibus 2,000-line `SystemManager` class doing auth, orders, and cache | God class handling both PDF generation and database migrations | Bloated utility file with 30 unrelated functions | Class with 2 slightly tangential helper methods |
| MAINT07 | Empty `except Exception: pass` concealing data loss during transactions | Catching exception, logging generic text, returning `null` | Catching exception and re-throwing without root cause | Missing error context on an already safe fallback |
| MAINT08 | Hardcoded production database credentials or secret keys | Hardcoded production API URLs in deep business logic | Scattered magic numbers in business calculation | Standard HTTP status code used inline |
| MAINT09 | Financial calculation directly calling `datetime.now()` making testing impossible | Static global mutable state mutated across test suites | Heavy private method that cannot be verified in isolation | Test fixture with slightly rigid assertions |
| MAINT10 | 6 layers of abstract wrapper classes that each forward a single method | Premature generic framework for a simple 10-line feature | Mixing Active Record and Repository in same file | Interface with only one implementation |
| MAINT11 | 200 lines of dead, commented-out historical code left in core service | Unreachable code block after unconditional raise/return | Unused private helper method | Unused imported package |
| MAINT12 | Misleading docstring stating function returns sanitized data when it does not | Undocumented complex custom compression algorithm | Missing docstring on public API endpoint | Missing comment on non-obvious line of code |
| MAINT13 | Adding 1 enum status forces edits in 15 distant files due to raw type checks | Modifying user record forces updating 10 manual serializers | Redundant field-by-field copy across 3 tiers | Small localized type update |
| MAINT14 | Scoped service injected into Singleton (.NET captive dependency) | 600-line React component with prop drilling across 7 layers | Python wildcard imports shadowing builtins | Slightly non-idiomatic framework usage |

---

## 2. Confidence Levels

Confidence reflects how strongly the available evidence supports the finding.

| Confidence | Definition |
|---|---|
| **high** | The finding is directly visible in the diff with clear, unambiguous evidence of maintainability harm. |
| **medium** | The pattern is visibly risky, but full repo context (call sites, callers, test suites) is only partially visible. |
| **low** | The concern is speculative or depends on future changes that may not occur. |

**Low-confidence concerns must not be reported as findings.** Instead, include
an `uncertainty_note` at the dimension level explaining:
- What pattern was observed
- Why it cannot be confirmed as a defect
- What additional repository context would resolve the uncertainty

---

## 3. Score Calculation

The maintainability dimension score starts at **100** and is reduced by deductions
for each finding. Deductions are computed using **base deduction × confidence modifier**.

### Base Deductions by Severity

| Severity | Base Deduction |
|---|---|
| critical | 25 |
| high | 15 |
| medium | 7 |
| low | 2 |

### Confidence Modifier

| Confidence | Multiplier |
|---|---|
| high | 1.00 |
| medium | 0.70 |
| low | 0.30 |

### Deduction Formula

```
deduction = round(base_deduction × confidence_multiplier)
```

Cap total deductions at 100 (minimum score is 0).

### Example Calculation

| Finding | Severity | Confidence | Base | Multiplier | Deduction |
|---|---|---|---|---|---|
| Swallowed exception in billing | high | high | 15 | 1.00 | 15 |
| Complex 5-level nested loop | medium | high | 7 | 1.00 | 7 |
| Scattered magic literals | medium | medium | 7 | 0.70 | 5 |
| **Total deduction** | | | | | **27** |
| **Final score** | | | | | **73** |

---

## 4. Handling Duplicate Findings

When multiple symptoms share a single root cause, they must produce **one primary finding**
using the most specific applicable rule ID.

**Rule:** The root-cause finding counts once for scoring. Symptoms that are merely
manifestations of the same architectural issue are not separately deducted.

**Example:** A bloated God class (MAINT06) that also has a 200-line method (MAINT04) and
scattered magic values (MAINT08). Report one primary MAINT06 finding documenting the
full scope in `evidence`. Do not apply three separate deductions.

---

## 5. Documented Exceptions and Accepted Trade-offs

When the team has documented an accepted trade-off (in code comments, ADRs, or PR
descriptions), reduce the deduction by **50%** and set `status` to `accepted`.

**Examples of documented exceptions:**
- "Intentionally duplicate this calculation to keep billing and warehouse services independently deployable" — MAINT01 reduced by 50%
- "Temporary workaround for upstream vendor bug #4512" — MAINT02 reduced by 50%

---

## 6. Blocking vs. Advisory Findings

### Blocking Findings

A review is considered **blocked** when:
- Final dimension score is **below 60**, AND
- At least one finding has severity `critical` or `high`

```json
{
  "dimension": "maintainability",
  "score": 52,
  "blocked": true,
  "block_reason": "One or more high/critical maintainability risks require resolution or explicit acceptance before merge."
}
```

### Advisory Findings

All `medium` and `low` severity findings are advisory and do not block merge.

- **75–100**: Passing ✅
- **60–74**: Flagged (Advisory warning, review recommended) ⚠️
- **0–59**: Blocked (Requires review-owner approval) 🔴

---

## 7. Scorecard Aggregator Integration

The maintainability skill returns a result object compatible with the Code Review
Portal's Scorecard Aggregator:

```json
{
  "dimension": "maintainability",
  "score": 82,
  "findings": [
    {
      "ruleId": "MAINT01",
      "title": "Duplicated Pricing Calculation Logic",
      "severity": "medium",
      "confidence": "high",
      "file": "src/services/billing_service.py",
      "lineStart": 45,
      "lineEnd": 68,
      "evidence": "Identical tax and discount calculation logic copied in checkout_service.py:112",
      "impact": "Changes to discount rules must be updated in multiple files, risking divergence",
      "recommendation": "Extract shared calculation into PricingPolicy.calculate_total()",
      "technology": "Python",
      "status": "open"
    }
  ],
  "uncertainty_notes": [],
  "blocked": false
}
```

