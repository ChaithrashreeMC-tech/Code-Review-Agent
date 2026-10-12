# Performance Scoring Guide

This guide defines how findings from `SKILL.md` rules PERF01–PERF14 are
classified and how the performance dimension score is calculated for the Code
Review Portal's Scorecard Aggregator.

---

## 1. Severity Classification

Severity reflects the **demonstrated or reasonably supported** impact of the
finding on production performance. It must not be inflated solely because a
pattern exists in code.

| Severity | Definition |
|---|---|
| **critical** | Causes or will likely cause service degradation, outages, or severe user-facing latency at any realistic load. Evidence is clear and direct. |
| **high** | Materially degrades performance under normal or high load with high confidence. The pattern is a known anti-pattern with a plausible impact path. |
| **medium** | Degrades performance in identifiable conditions (high data volume, concurrent requests, large payloads) but may be acceptable at current scale. |
| **low** | Minor or speculative impact. The pattern could become a concern at significantly higher scale but is acceptable now. |

### Severity Anchors by Rule

| Rule | Critical Example | High Example | Medium Example | Low Example |
|---|---|---|---|---|
| PERF01 | Sync HTTP call blocking event loop in hot path | Unnecessary sequential I/O in user-facing API | Avoidable repeated computation in a batch job | Minor blocking in a rarely-invoked admin endpoint |
| PERF02 | N+1 query per user on every page load with large user base | N+1 on unbounded order list | Eager load missing but table is small | N+1 on a bounded 3-item constant collection |
| PERF03 | Unbounded user-controlled file buffered in RAM | Full DB result set buffered without LIMIT | Inconsistent resource disposal | Minor allocation in a cold path |
| PERF04 | Cacheable config reloaded from DB on every request at 1k RPS | Hot DB query uncached, high read frequency | Cache TTL missing on mutable data | Caching opportunity speculative on cold path |
| PERF05 | No timeout on external API call in synchronous handler | Retry without backoff cap on external dependency | Timeout too long for UX requirements | Missing timeout on infrequent, supervised call |
| PERF06 | Unbounded history growth causing context-window overflow | Full history injected per prompt on long conversations | Repeated static doc in system message (bounded) | Speculative LLM efficiency concern |
| PERF07 | Shared mutable state corrupted by concurrent writes | Unbounded fan-out exhausting connection pool | Sequential I/O for independent operations in hot path | Parallelism opportunity on cold or rare path |
| PERF08 | AI tool called N times per request with identical args | External API called multiple times per request | Regex compiled inline in a hot loop | Cheap computation repeated but negligible cost |
| PERF09 | Full scan on multi-million-row table in hot query | Unindexed FK in high-frequency JOIN | Leading wildcard LIKE on moderately large table | Missing index on a rarely queried small table |
| PERF10 | Public endpoint returning all rows with no LIMIT | Unbounded internal list API with no pagination | Very large default page size without cap | OFFSET pagination concern on currently small table |
| PERF11 | Rendering 10k+ DOM nodes freezing the UI | Re-render cascade through large component subtree | Missing memoization on moderately expensive computation | Pre-emptive `useMemo` suggestion without evidence |
| PERF12 | 500 KB library added to critical bundle | Heavy route without code splitting | Moderate library without named imports | Small utility without lazy loading |
| PERF13 | Large unoptimized image causing LCP regression | Missing image dimensions causing CLS | Render-blocking font on non-critical path | Speculative WebP suggestion on small icon |
| PERF14 | Full store subscription causing cascade re-render on every keystroke | Selector returning new object defeating memoization | Missing debounce on moderate-frequency input | Pre-emptive `useMemo` suggestion on cheap derivation |

---

## 2. Confidence Levels

Confidence reflects how strongly the available evidence supports the finding.

| Confidence | Definition |
|---|---|
| **high** | The finding is directly visible in the diff with clear, unambiguous evidence. Impact path is straightforward. |
| **medium** | The finding is plausible based on code patterns, but full context (data volume, call frequency, infrastructure) is not visible. |
| **low** | The concern is speculative — the pattern could be an issue but available evidence is insufficient to confirm. |

**Low-confidence concerns must not be reported as findings.** Instead, include
an `uncertainty_note` at the dimension level explaining:
- What pattern was observed
- Why it cannot be confirmed as a finding
- What additional information (profiler output, data volume, infrastructure
  config) would resolve the uncertainty

---

## 3. Score Calculation

The performance dimension score starts at **100** and is reduced by deductions
for each finding. Deductions are computed using **severity × confidence
modifier**.

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

> Low-confidence findings should not reach this stage (see Section 2), but
> if included they receive the 0.30 multiplier.

### Deduction Formula

```
deduction = base_deduction × confidence_multiplier
```

Round each deduction to the nearest integer. Apply all deductions and sum.
Cap total deductions at 100 (minimum score is 0).

### Example Calculation

| Finding | Severity | Confidence | Base | Multiplier | Deduction |
|---|---|---|---|---|---|
| N+1 query in order service | high | high | 15 | 1.00 | 15 |
| Missing cache TTL | medium | high | 7 | 1.00 | 7 |
| Potential large bundle import | medium | medium | 7 | 0.70 | 5 |
| Speculative PERF01 concern (uncertainty_note) | — | — | — | — | 0 |
| **Total deduction** | | | | | **27** |
| **Final score** | | | | | **73** |

---

## 4. Rule Influence on Scoring

Each rule contributes findings independently. Rules are not weighted
differently — severity and confidence determine the deduction. However, some
rules more commonly produce high-severity findings due to their nature:

| Rule | Typical Severity Range | Notes |
|---|---|---|
| PERF01 | medium – critical | Blocking I/O in hot paths is critical |
| PERF02 | medium – high | N+1 on large datasets is typically high |
| PERF03 | medium – critical | Unbounded buffering can be critical |
| PERF04 | low – high | Depends on call frequency and data mutability |
| PERF05 | medium – high | Missing timeouts on external calls are high |
| PERF06 | low – high | Context overflow is high; minor redundancy is low |
| PERF07 | medium – high | Safety findings (shared state) can be high |
| PERF08 | low – medium | Rarely critical; most are medium |
| PERF09 | medium – high | Unindexed large-table queries are high |
| PERF10 | medium – high | Unbounded public endpoints are high |
| PERF11 | low – high | DOM-freeze cases are high; speculative useMemo is low |
| PERF12 | low – high | Large critical-bundle additions are high |
| PERF13 | low – high | LCP-impacting images can be high |
| PERF14 | low – medium | Rarely exceeds medium without profiler data |

---

## 5. Handling Duplicate Findings

When multiple symptoms share a single root cause, they must produce **one
finding** using the most specific applicable rule ID.

**Rule:** The root-cause finding counts once for scoring. Symptoms that are
merely additional manifestations of the same issue are not separately
deducted.

**Example:** An N+1 query (PERF02) in a loop also reads all columns (PERF09)
and materializes an unbounded result (PERF10). Report as one PERF02 finding
with the full scope described in `evidence`. Do not apply three separate
deductions.

If two truly independent performance issues share a code location, report both
as separate findings with distinct rule IDs and deduce both.

---

## 6. Documented Exceptions and Accepted Trade-offs

When the team has documented an accepted trade-off (in code comments, ADRs, or
PR descriptions), reduce the deduction by **50%** and set `status` to
`accepted`.

**Examples of documented exceptions:**
- "Full table scan on config table (< 500 rows, read once at startup)" — PERF09
  reduced by 50%
- "Full history injected for compliance audit trail" — PERF06 reduced by 50%
- "OFFSET pagination retained for simplicity at current scale" — PERF10 low
  severity reduced by 50%

Exceptions must be explicit (not inferred). Absence of a comment is not a
documented exception.

---

## 7. Insufficient Evidence

When evidence is insufficient to confirm a finding:

1. Do **not** record a finding.
2. Record an `uncertainty_note` at the dimension level:
   ```json
   {
     "uncertainty_note": "PERF04: Caching may benefit the /users endpoint
       if call frequency is high, but query cost and access patterns are not
       visible in the diff. Profiler data or call frequency metrics would
       confirm or rule out this concern."
   }
   ```
3. The `uncertainty_note` does **not** incur a score deduction.
4. Uncertainty notes are advisory and should prompt the author or reviewer
   to supply additional context.

---

## 8. Blocking vs. Advisory Findings

### Blocking Findings

A review is considered **blocked** (requires review-owner approval before
merge) when:

- Final dimension score is **below 60**, AND
- At least one finding has severity `critical` or `high`

A blocked review is indicated by:
```json
{
  "dimension": "performance",
  "score": 52,
  "blocked": true,
  "block_reason": "One or more high/critical findings require resolution or
    explicit acceptance before merge."
}
```

### Advisory Findings

All `medium` and `low` severity findings are advisory. They appear in the
review output but do not block merge. Teams are encouraged to address advisory
findings in a follow-up or to document accepted trade-offs.

A score of 60–74 is **flagged** (advisory warning, merge permitted):
```json
{ "dimension": "performance", "score": 68, "flagged": true }
```

A score of 75–100 is **passing**:
```json
{ "dimension": "performance", "score": 85 }
```

---

## 9. Scorecard Aggregator Integration

The performance skill returns a result object compatible with the Code Review
Portal's Scorecard Aggregator:

```json
{
  "dimension": "performance",
  "score": 78,
  "findings": [
    {
      "ruleId": "PERF02",
      "title": "N+1 Query in Order Processing Loop",
      "severity": "high",
      "confidence": "high",
      "file": "src/services/order_service.py",
      "lineStart": 42,
      "lineEnd": 55,
      "evidence": "Loop on line 42 issues one SELECT per order item; no eager load",
      "impact": "Query count scales linearly with order volume",
      "recommendation": "Use selectinload() or batch with WHERE id IN (...)",
      "technology": "Python/SQLAlchemy",
      "status": "open"
    }
  ],
  "uncertainty_notes": [
    "PERF04: Caching benefit for /products endpoint could not be confirmed
     without call frequency data."
  ],
  "blocked": false
}
```

**Aggregator contract rules:**
- `dimension` must be `"performance"`
- `score` must be an integer in [0, 100]
- `findings` must be an array (empty array if no findings)
- `blocked` must be present and boolean
- `uncertainty_notes` is optional; omit if empty
- All finding fields defined in `SKILL.md` Section 6 apply here

---

## 10. Score Interpretation Quick Reference

| Score Range | Status | Meaning |
|---|---|---|
| 90–100 | ✅ Passing | No significant performance concerns |
| 75–89 | ✅ Passing | Minor advisory findings only |
| 60–74 | ⚠️ Flagged | Medium findings present; review recommended |
| 40–59 | 🔴 Blocked | High findings present; approval required |
| 0–39 | 🔴 Blocked | Critical findings; must be resolved before merge |

