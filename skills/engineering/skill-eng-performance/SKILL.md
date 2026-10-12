---
name: skill-eng-performance
description: >-
  Activate when reviewing code changes involving performance, optimization,
  latency, slow queries, N+1 queries, memory usage, caching, timeouts,
  pagination, concurrency, rendering, bundle size, Core Web Vitals, LLM
  context efficiency, or AI-agent orchestration. Evaluates backend execution,
  database access, memory and resource management, caching strategy, timeout
  resilience, LLM context, concurrency, call efficiency, index efficiency,
  data retrieval, frontend rendering, code delivery, assets, and state updates
  across Python, .NET/C#, Java, JavaScript/TypeScript, React, SQL, and AI-agent
  systems. Adapts inspection methods to the detected stack.
---

# Engineering Performance Review Skill

## 1. Purpose & Activation

This skill evaluates pull requests for performance regressions, bottlenecks, and resource
inefficiencies across backend services, data access layers, frontend applications, and
AI-agent orchestration workflows.

**Activate when** code changes touch latency-critical paths, database queries, ORM usage,
caching layers, async or concurrent flows, React rendering or state management, asset
pipelines, or LLM prompt construction and token budgets; or when review context cites
latency, throughput, memory, bundle size, Core Web Vitals, slow queries, N+1, or timeouts.

## 2. Technology Context

Infer the relevant technology stack from the supplied code, file extensions, imports, dependency manifests, configuration, and surrounding context. Apply shared performance principles across supported technologies, adapting detection criteria to the technologies actually present.

Refer to `references/checklist.md` for technology-specific detection patterns and examples.

Technology detection is supporting guidance, not a standalone review objective. Do not report findings merely because a particular technology or framework is present.

## 3. Performance Rules

| ID | Rule | Objective |
|---|---|---|
| PERF01 | Execution Efficiency | Eliminate blocking calls, avoidable delays, and unneeded CPU work in request paths. |
| PERF02 | Data Access Efficiency | Prevent N+1 queries, repeated round trips, and missing batch retrieval. |
| PERF03 | Memory and Resource Management | Prevent unbounded buffering, memory leaks, and unclosed resource handles. |
| PERF04 | Caching Strategy | Ensure caching is applied where beneficial with proper TTL and invalidation. |
| PERF05 | Timeouts and Resilience | Protect external calls and async tasks with bounded timeouts, retries, and cancellation. |
| PERF06 | LLM and Context Efficiency | Minimize token consumption, runaway context growth, and redundant model prompts. |
| PERF07 | Concurrency and Parallelism | Parallelize independent I/O safely while bounding concurrency and protecting shared state. |
| PERF08 | Call and Computation Efficiency | Eliminate redundant service calls, duplicated computations, and per-request static loads. |
| PERF09 | Database Query and Index Efficiency | Ensure queries utilize appropriate indexes and avoid full-table scans. |
| PERF10 | Data Retrieval and Pagination | Bound result sizes and avoid large-offset pagination on growing datasets. |
| PERF11 | Frontend Rendering Efficiency | Prevent UI freezes, unvirtualized large lists, and unnecessary re-render cascades. |
| PERF12 | Code and Module Delivery | Minimize initial bundle size through code splitting, dynamic imports, and tree-shaking. |
| PERF13 | Asset and Network Efficiency | Optimize image formats, specify dimensions to prevent CLS, and reduce transfer payloads. |
| PERF14 | State and Update Efficiency | Prevent broad store subscriptions, unstable selectors, and unthrottled state updates. |

*Detailed criteria, evidence, and remediation per rule are defined in [`references/checklist.md`](references/checklist.md).*

## 4. Review Workflow

1. **Inspect Context**: Review changed diffs, execution paths, data volumes, and surrounding code.
2. **Detect Stack**: Identify runtime, frameworks, and data-access libraries (see Section 2).
3. **Select Rules**: Match diff changes against applicable rules (PERF01–PERF14).
4. **Evaluate Evidence**: Consult [`references/checklist.md`](references/checklist.md) to substantiate each finding with visible code patterns and plausible runtime impact.
5. **Score & Deduplicate**: Apply [`references/scoring-guide.md`](references/scoring-guide.md). Consolidate multiple symptoms sharing a single root cause into one finding.
6. **Generate Output**: Format findings using the Scorecard Aggregator schema below.

## 5. Review Principles

- **Evidence-Based**: Report issues only when diff code and execution context substantiate them; describe uncertainties in `uncertainty_notes` rather than low-confidence findings.
- **Context & Scale Proportionality**: Weigh findings against actual workload, data volume, and service SLAs (e.g. small lookup tables do not need indexes).
- **No Speculative Recommendations**: Do not prescribe caching, streaming, cursor pagination, or parallelism without demonstrated access-pattern justification.
- **No Blanket React Penalties**: Omitting `useMemo` or `useCallback` is not a defect unless profiling or component hierarchy demonstrates a measurable render cascade.
- **Root-Cause Deduplication**: One underlying defect (e.g. N+1 query loop) must produce exactly one finding, not separate findings for secondary symptoms.
- **Review Only**: Identify defects and provide actionable guidance; do not generate refactored code or execute automated fixes.
- **Web Vitals Evidence**: Do not claim Core Web Vitals regressions (LCP, CLS, INP) without clear layout or network transfer evidence.

## 6. Output Contract & References

Return structured output compatible with the Code Review Portal Scorecard Aggregator:

```json
{
  "dimension": "performance",
  "score": 8.0,
  "findings": [
    {
      "ruleId": "PERF02",
      "title": "N+1 Query in Order Processing Loop",
      "severity": "high",
      "confidence": "high",
      "file": "src/services/order_service.py",
      "lineStart": 42,
      "lineEnd": 55,
      "evidence": "Loop issues SELECT per item without eager loading",
      "impact": "Database query count scales linearly with order count",
      "recommendation": "Use selectinload(Order.items) to batch load in 2 queries",
      "technology": "Python/SQLAlchemy",
      "status": "open"
    }
  ],
  "uncertainty_notes": [],
  "blocked": true
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `ruleId` | string | Yes | PERF01–PERF14 stable identifier |
| `title` | string | Yes | Concise issue summary |
| `severity` | string | Yes | `critical`, `high`, `medium`, or `low` |
| `confidence` | string | Yes | `high`, `medium`, or `low` |
| `file` | string | Yes | Repository-relative path |
| `lineStart` | integer | Yes | First line number of the relevant code |
| `lineEnd` | integer | No | End line number of the relevant code block |
| `evidence` | string | Yes | Concrete code observation supporting the issue |
| `impact` | string | Yes | Plausible runtime consequence under load |
| `recommendation` | string | Yes | Stack-specific actionable remediation guidance |
| `technology` | string | No | Inferred technology stack |
| `status` | string | No | Finding lifecycle status (default: `open`) |

Integration rules for the aggregator:
- `score` is calculated directly on a native 0.0–10.0 scale from start to finish without any intermediate 0–100 calculation or division, according to [`references/scoring-guide.md`](references/scoring-guide.md).
- `blocked` is set to `true` when the dimension score is below 9.0 (9/10) or when any confirmed critical violation is present.
- A score of 10.0 (10/10) indicates pass with zero violations; 9.0 (9/10) indicates pass with at most one minor non-blocking finding and no critical violations.
- Low-confidence observations must be recorded in `uncertainty_notes` and incur 0 deductions.

## 7. Supporting References

- **Inspection Checklist**: [`references/checklist.md`](references/checklist.md) — Detailed criteria, evidence, and remediation per rule.
- **Scoring Guide**: [`references/scoring-guide.md`](references/scoring-guide.md) — Severity tiers, deduction formulas, exceptions, and merge blocking.
- **Validation Suite**: [`validation/test-suite.json`](validation/test-suite.json) — Automated test cases for detection and false-positive verification.
