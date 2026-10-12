# Modularity Scoring Guide

This guide defines how findings from `SKILL.md` rules MOD01–MOD12 are classified and how the modularity dimension score is calculated for the Code Review Portal's Scorecard Aggregator.

---

## 1. Severity Classification

Severity reflects the **demonstrated or reasonably supported** impact of the finding on code maintainability, testability, and architectural integrity. It must not be inflated solely because a pattern exists in code.

| Severity | Definition |
|---|---|
| **critical** | Severe architectural violation causing system instability, broken layer isolation, or circular import deadlock. |
| **high** | Materially degrades codebase maintainability, testability, or domain boundaries. Direct anti-pattern with clear technical debt impact. |
| **medium** | Degrades modularity in specific components or modules but manageable at current scale. |
| **low** | Minor modularity concern or feature collocation issue. |

### Severity Anchors by Rule

| Rule | Critical Example | High Example | Medium Example | Low Example |
|---|---|---|---|---|
| MOD01 | Class mixing database mutations, network I/O, UI rendering, and business calculations | Domain service combining user profile management, payment processing, and email formatting | Service method handling parameter validation alongside domain processing | Helper module containing slightly broad string formatting routines |
| MOD02 | Domain layer directly calling raw OS / DB drivers across core layer boundary | High-level domain service directly importing concrete HTTP/DB client libraries | Domain logic calling concrete file I/O helper instead of interface | Application wiring importing low-level driver for setup |
| MOD03 | Deep private internal access breaking sibling domain encapsulation | Cross-domain import reaching into private package internals of another domain | Direct call to internal helper function in sibling feature module | Cross-domain import of public shared domain type |
| MOD04 | Global DB/SDK client instantiated at module load mutating global state | Hardcoded global Stripe/DB client instantiated at module import scope | Concrete client instantiation inside constructor without DI container | Missing interface wrapper for simple local utility client |
| MOD05 | God class (> 8 dependencies) managing multiple distinct application lifecycles | Service class with > 5 direct dependencies controlling multiple sub-domains | Class with 5 dependencies approaching complexity threshold | Slightly lengthy configuration manager class |
| MOD06 | Graph file containing full inline business logic, database queries, and LLM calls | `graph.py` or `edges.py` containing inline LLM calls or complex state transformations | Graph file containing non-trivial data mapping functions | Minor inline routing decision function in graph assembly |
| MOD07 | Agent node function directly executing raw cloud SDK / DB calls inline | Agent step invoking raw external SDK methods directly without client wrapper | Agent step bypassing tool abstraction for quick read call | Direct call to standard project wrapper utility |
| MOD08 | Route handler containing complete business workflow, pricing math, and DB queries | HTTP route handler executing domain logic and calculations inline | RPC handler containing input data normalization business rules | Handler with slight parameter mapping logic |
| MOD09 | Service class building raw SQL query strings and executing against DB connection | Domain service issuing raw SQL strings or directly operating raw DB handles | Service bypassing repository for simple raw count query | Repository helper executing raw SQL query |
| MOD10 | JSX component body calling `fetch()` / API client directly during render | React component executing inline network side-effects and complex state | Presentational component with embedded data fetching hook | Component with minor inline event handler |
| MOD11 | Feature-specific business logic and components scattered in root directories | Feature components, hooks, and clients placed in global `/utils` or `/components` | Feature helper file located in global shared folder | Minor utility file shared across features |
| MOD12 | Circular import loop between core packages causing runtime module import failure | Circular dependency between two domain modules (`A -> B -> A`) | Circular import between internal helper modules resolved at runtime | Circular type reference resolved via type-only imports |

---

## 2. Confidence Levels

Confidence reflects how strongly the available evidence supports the finding.

| Confidence | Definition |
|---|---|
| **high** | The finding is directly visible in the diff with clear, unambiguous evidence. Impact path is straightforward. |
| **medium** | The finding is plausible based on code patterns, but full architectural context is not visible. |
| **low** | The concern is speculative — the pattern could be an issue but available evidence is insufficient to confirm. |

**Low-confidence concerns must not be reported as findings.** Instead, include an `uncertainty_note` at the dimension level explaining:
- What pattern was observed
- Why it cannot be confirmed as a finding
- What additional information (project architecture, system boundaries) would resolve the uncertainty

---

## 3. Score Calculation

The modularity dimension score starts at **100** and is reduced by deductions for each finding.

### Per-Rule Deduction Guide

| Rule ID | Violation | Suggested Deduction |
| :--- | :--- | :--- |
| MOD01 | Module/class has more than one distinct reason to change | −8 per instance |
| MOD02 | High-level module directly imports low-level I/O detail across a layer boundary | −10 per occurrence |
| MOD03 | Cross-domain private import (Domain A reaches into Domain B internals) | −8 per import |
| MOD04 | Hardcoded global SDK/DB client at module import scope | −8 per instance |
| MOD05 | Class/service with > 5 direct dependencies | −10 per class |
| MOD06 | graph.py / edges.py contains execution logic or LLM calls inline | −10 per occurrence |
| MOD07 | Agent node calls raw external SDK endpoint directly | −10 per node |
| MOD08 | Business logic present inside a route handler or RPC handler | −12 per handler |
| MOD09 | Raw SQL or raw DB session handle used directly inside a Service | −12 per occurrence |
| MOD10 | fetch() / raw Connect client call inside a JSX component body | −10 per component |
| MOD11 | Feature-specific code scattered in global folders | −5 per misplaced module |
| MOD12 | Circular import detected between two modules | −15 per cycle |

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
deduction = base_deduction × confidence_multiplier
```

Round each deduction to the nearest integer. Sum all deductions and cap at 100 (minimum score is 0).

### Example Calculation

| Finding | Severity | Confidence | Base | Multiplier | Deduction |
|---|---|---|---|---|---|
| Business logic in route handler (MOD08) | high | high | 12 | 1.00 | 12 |
| Hardcoded global DB client (MOD04) | medium | high | 8 | 1.00 | 8 |
| Feature code in global folder (MOD11) | low | medium | 5 | 0.70 | 4 |
| Speculative MOD02 concern (uncertainty_note) | — | — | — | — | 0 |
| **Total deduction** | | | | | **24** |
| **Final score** | | | | | **76** |

---

## 4. Rule Influence on Scoring

Each rule contributes findings independently. Rules are not weighted differently — severity and confidence determine the deduction. However, some rules more commonly produce high-severity findings due to their nature:

| Rule | Typical Severity Range | Notes |
|---|---|---|
| MOD01 | medium – high | Violation of Single Responsibility Principle |
| MOD02 | medium – high | Violation of layer separation & dependency inversion |
| MOD03 | medium – high | Bypassing domain encapsulation boundaries |
| MOD04 | medium – high | Impairs dependency injection and unit test isolation |
| MOD05 | medium – critical | God objects controlling multi-domain lifecycles |
| MOD06 | medium – high | Mixing execution logic in graph assembly |
| MOD07 | medium – high | Raw external SDK calls in agent steps |
| MOD08 | medium – high | Transport layer coupled to business logic |
| MOD09 | medium – high | Persistence layer leaking into domain service |
| MOD10 | medium – high | Presentation layer coupled to network side-effects |
| MOD11 | low – medium | Organization and feature collocation defect |
| MOD12 | high – critical | Circular import loops causing initialization failures |

---

## 5. Handling Duplicate Findings

When multiple symptoms share a single root cause, they must produce **one finding** using the most specific applicable rule ID.

**Rule:** The root-cause finding counts once for scoring. Symptoms that are merely additional manifestations of the same issue are not separately deducted.

**Example:** An embedded SQL query in a controller (MOD08) also uses a raw DB session handle (MOD09). Report as one MOD08 finding with the full scope described in `evidence`. Do not apply two separate deductions.

---

## 6. Documented Exceptions and Accepted Trade-offs

When the team has documented an accepted trade-off (in code comments, ADRs, or PR descriptions), reduce the deduction by **50%** and set `status` to `accepted`.

**Examples of documented exceptions:**
- "Direct SQL used in migration script for performance" — MOD09 reduced by 50%
- "Inline import used to break circular type dependency in legacy module" — MOD12 reduced by 50%

---

## 7. Insufficient Evidence

When evidence is insufficient to confirm a finding:

1. Do **not** record a finding.
2. Record an `uncertainty_note` at the dimension level:
   ```json
   {
     "uncertainty_note": "MOD02: Interface abstraction may benefit PaymentService if multiple gateways are planned, but current diff shows single provider. Architectural context is needed to confirm."
   }
   ```
3. The `uncertainty_note` does **not** incur a score deduction.
4. Uncertainty notes are advisory and prompt the author or reviewer to supply additional context.

---

## 8. Blocking vs. Advisory Findings

### Blocking Findings

A review is considered **blocked** when:
- Final dimension score is **below 60**, AND
- At least one finding has severity `critical` or `high`

A blocked review is indicated by:
```json
{
  "dimension": "modularity",
  "score": 52,
  "blocked": true,
  "block_reason": "One or more high/critical modularity violations require resolution before merge."
}
```

### Advisory Findings

All `medium` and `low` severity findings are advisory. They appear in the review output but do not block merge.

A score of 60–74 is **flagged** (advisory warning, merge permitted):
```json
{ "dimension": "modularity", "score": 68, "flagged": true }
```

A score of 75–100 is **passing**:
```json
{ "dimension": "modularity", "score": 85 }
```

---

## 9. Scorecard Aggregator Integration

The modularity skill returns a result object compatible with the Code Review Portal's Scorecard Aggregator:

```json
{
  "dimension": "modularity",
  "score": 76,
  "findings": [
    {
      "ruleId": "MOD08",
      "title": "Business Logic inside Route Handler",
      "severity": "high",
      "confidence": "high",
      "file": "src/controllers/order_controller.py",
      "lineStart": 24,
      "lineEnd": 38,
      "evidence": "Route handler executes domain calculations directly",
      "impact": "Violates layer separation, preventing independent unit testing and service reuse",
      "recommendation": "Move business logic into a dedicated OrderService",
      "technology": "Python/Flask",
      "status": "open"
    }
  ],
  "uncertainty_notes": [],
  "blocked": false
}
```

**Aggregator contract rules:**
- `dimension` must be `"modularity"`
- `score` must be an integer in [0, 100]
- `findings` must be an array (empty array if no findings)
- `blocked` must be present and boolean
- `uncertainty_notes` is optional; omit if empty

---

## 10. Score Interpretation Quick Reference

| Score Range | Status | Meaning |
|---|---|---|
| **90–100** | ✅ **Passing** (Excellent) | Strict 3-tier boundary, SRP honoured everywhere, 100% dependency injection, fully decoupled agent nodes, zero circular imports. No rule violations. |
| **75–89** | ✅ **Passing** (Acceptable) | Clean architecture mostly followed. Minor advisory findings only. No circular imports. |
| **60–74** | ⚠️ **Flagged** (Needs Improvement) | Medium findings present; business logic in handlers or direct DB calls in services. Review recommended. |
| **40–59** | 🔴 **Blocked** | High findings present; approval required before merge. |
| **0–39** | 🔴 **Blocked** | Critical findings (God class > 8 deps, circular dependencies, raw DB queries in UI); must be resolved. |
