---
name: skill-eng-modularity
description: >-
  Activate when reviewing code changes involving modularity, architecture,
  coupling, cohesion, encapsulation, separation of concerns, dependency
  management, circular dependencies, domain boundaries, interface contracts,
  reusability, or component structure. Applies universal modularity rules
  (MOD01–MOD12) across all programming languages, frameworks, paradigms,
  platforms, architectural styles (agent orchestration, backend APIs, frontend
  components), and repository types.
---

# Engineering Modularity Review Skill

## 1. Purpose & Activation

This skill evaluates pull requests for architectural regressions, tight coupling, poor cohesion, leaky abstractions, circular dependencies, and structural technical debt across any software codebase.

**Activate when** code changes touch architectural boundaries, module/package structures, class/interface declarations, dependency wiring, cross-domain imports, state management layers, component hierarchies, or public API contracts; or when review context cites refactoring, coupling, cohesion, circular imports, spaghetti code, or architectural debt across any language or platform.

## 2. Technology Context

Infer the relevant technology stack, programming paradigm, and architectural style from changed files, imports, configurations, and surrounding context. Apply universal modularity principles consistently regardless of technology  or architecture .

Refer to `references/checklist.md` for technology- and paradigm-specific evidence patterns and remediation guidance.

Technology detection serves to contextualize evidence interpretation and suggest idiomatic remediation—it does not restrict review applicability or diminish universal modularity expectations.

## 3. Modularity Rules

| ID | Rule | Objective |
|---|---|---|
| MOD01 | Single Responsibility & Cohesion | Ensure modules, classes, and functions have a single, well-defined reason to change. |
| MOD02 | Layer Separation & Dependency Inversion | Prevent high-level modules from directly importing low-level I/O details across layer boundaries. |
| MOD03 | Cross-Domain Boundaries | Prevent modules in Domain A from importing private internal details of Domain B. |
| MOD04 | Hardcoded Global Clients | Prevent global SDK, DB, or HTTP client instantiation at module import scope. |
| MOD05 | Module Granularity & God Classes | Prevent God classes/steps with > 5 direct dependencies or multiple business lifecycles. |
| MOD06 | Declarative Graph Wiring | Isolate execution logic or LLM calls from declarative graph assembly files. |
| MOD07 | Agent Step Abstractions | Route external SDK/tool calls through shared client abstractions, not raw inline calls. |
| MOD08 | Handler Layer Isolation | Keep route/RPC handlers thin; move all business decisions into domain services. |
| MOD09 | Data Access Isolation | Encapsulate database queries in repositories/DAL; keep raw SQL out of services. |
| MOD10 | UI Component Modularity | Prevent direct data-fetching (`fetch`, `axios`) inside UI JSX component bodies. |
| MOD11 | Feature Collocation | Collocate feature-specific code in feature folders instead of scattering in global dirs. |
| MOD12 | Cyclic Dependencies | Eliminate circular dependencies/imports between modules, packages, or layers. |

*Detailed criteria, evidence, and remediation per rule are defined in [`references/checklist.md`](references/checklist.md).*

## 4. Review Workflow

1. **Inspect Context**: Review changed diffs, module declarations, import trees, and surrounding architectural boundaries.
2. **Detect Stack & Paradigm**: Identify runtime, languages, paradigms (OO, FP, procedural, component-based), and architectural style (see Section 2).
3. **Select Rules**: Match diff changes against applicable universal rules (MOD01–MOD12).
4. **Evaluate Evidence**: Consult [`references/checklist.md`](references/checklist.md) to substantiate each finding with visible code patterns and structural impact.
5. **Score & Deduplicate**: Apply [`references/scoring-guide.md`](references/scoring-guide.md). Consolidate multiple symptoms sharing a single root cause into one finding.
6. **Generate Output**: Format findings using the Scorecard Aggregator schema below.

## 5. Review Principles

- **Universal Principles, Stack-Idiomatic Remediation**: Apply the same core modularity rules everywhere while tailoring recommendations to stack conventions.
- **Evidence-Based**: Report issues only when diff code and architectural context substantiate them; describe uncertainties in `uncertainty_notes` rather than low-confidence findings.
- **Context & Scale Proportionality**: Weigh findings against actual project scale, architectural style, and team conventions (e.g. CLI scripts do not need enterprise clean architecture layers).
- **No Speculative Abstractions**: Do not mandate interfaces or indirection layers unless multiple implementations or concrete extension needs exist.
- **No Blanket Boilerplate Penalties**: Minor duplication across unrelated domain boundaries is preferable to premature coupling via an ill-fitting shared utility.
- **Root-Cause Deduplication**: One underlying defect (e.g. leaking persistence logic into presentation) must produce exactly one finding, not separate findings for secondary symptoms.
- **Review Only**: Identify structural defects and provide actionable guidance; do not generate refactored code or execute automated fixes.

## 6. Output Contract & References

Return structured output compatible with the Code Review Portal Scorecard Aggregator:

```json
{
  "dimension": "modularity",
  "score": 85,
  "findings": [
    {
      "ruleId": "MOD08",
      "title": "Business Logic inside Route Handler",
      "severity": "high",
      "confidence": "high",
      "file": "src/controllers/order_controller.py",
      "lineStart": 24,
      "lineEnd": 38,
      "evidence": "HTTP route handler directly executes domain calculations and DB transactions",
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

| Field | Type | Required | Description |
|---|---|---|---|
| `ruleId` | string | Yes | MOD01–MOD12 stable identifier |
| `title` | string | Yes | Concise issue summary |
| `severity` | string | Yes | `critical`, `high`, `medium`, or `low` |
| `confidence` | string | Yes | `high`, `medium`, or `low` |
| `file` | string | Yes | Repository-relative path |
| `lineStart` | integer | Yes | First line number of the relevant code |
| `lineEnd` | integer | No | End line number of the relevant code block |
| `evidence` | string | Yes | Concrete code observation supporting the issue |
| `impact` | string | Yes | Structural or maintainability consequence under ongoing development |
| `recommendation` | string | Yes | Stack-specific actionable remediation guidance |
| `technology` | string | No | Inferred technology stack |
| `status` | string | No | Finding lifecycle status (default: `open`) |

Integration rules for the aggregator:
- `score` starts at 100, reduced by deductions according to [`references/scoring-guide.md`](references/scoring-guide.md).
- `blocked` is set to `true` when score is below 60 and includes at least one `critical` or `high` finding.
- Low-confidence observations must be recorded in `uncertainty_notes` and incur 0 deductions.

## 7. Supporting References

- **Inspection Checklist**: [`references/checklist.md`](references/checklist.md) — Detailed criteria, evidence, and remediation per rule across languages and paradigms.
- **Scoring Guide**: [`references/scoring-guide.md`](references/scoring-guide.md) — Severity tiers, deduction formulas, exceptions, and merge blocking.
- **Validation Suite**: [`validation/test-suite.json`](validation/test-suite.json) — Automated test cases for detection and false-positive verification.
