---
name: skill-eng-maintainability
description: >-
  Activate when reviewing code changes for maintainability, readability, duplication,
  complexity, naming, single responsibility, coupling, cohesion, error handling,
  configuration, testability, dead code, documentation, change locality, or architectural
  consistency across Python, .NET/C#, Java, JavaScript/TypeScript, React, SQL, and
  AI-agent workflows. Evaluates code structure, cognitive load, and ease of understanding,
  testing, extending, and modifying code without enforcing subjective style preferences.
---

# Engineering Maintainability Review Skill

## 1. Purpose & Activation

This skill evaluates pull requests and code modifications for maintainability risks that
hinder comprehension, testability, extensibility, or safe modification across backend
services, databases, frontend applications, and AI-agent workflows.

**Activate when** code changes modify structural design, component boundaries, error
handling semantics, business logic abstractions, public contracts, configuration, or test
harnesses; or when review context cites technical debt, high complexity, duplication,
unclear naming, tight coupling, or refactoring needs.

Do not report findings merely because code deviates from personal stylistic preferences or
unmandated idioms when the code is clear, well-isolated, and straightforward to maintain.

## 2. Technology Context

Infer the relevant technology from the supplied code and repository context. Apply shared maintainability principles across supported languages, frameworks, databases, and AI-agent systems, adapting review criteria to the code being examined. Do not create separate top-level skills for individual technologies.

Refer to `references/checklist.md` for technology-specific detection patterns and examples.

Technology context guides how rules are applied; it is not a standalone review objective. Report only evidence-based maintainability issues, not findings based solely on the presence of a particular technology or framework.

## 3. Maintainability Rules

| ID | Rule | Objective |
|---|---|---|
| MAINT01 | Code Duplication | Identify repeated logic or business rules that cause inconsistencies and increase modification costs. |
| MAINT02 | Complexity and Readability | Identify unnecessarily complex control flow, deep nesting, and logic that hinders comprehension. |
| MAINT03 | Naming and Intent Clarity | Identify ambiguous, misleading, or non-descriptive names that obscure symbol purpose or behavior. |
| MAINT04 | Function and Method Responsibility | Identify functions with multiple unrelated responsibilities, excessive size, or unclear boundaries. |
| MAINT05 | Coupling and Dependency Management | Identify unnecessary dependencies and tight coupling that impede isolation, testing, and reuse. |
| MAINT06 | Cohesion and Module Boundaries | Identify classes or modules that combine unrelated concerns or lack a focused purpose. |
| MAINT07 | Error Handling Clarity | Identify swallowed exceptions, misleading propagation, and opaque failure semantics that obscure diagnoses. |
| MAINT08 | Configuration and Magic Values | Identify scattered magic literals, hardcoded environments, and uncentralized configuration values. |
| MAINT09 | Testability and Test Structure | Identify designs that hinder isolated unit testing, dependency substitution, or behavioral verification. |
| MAINT10 | Abstraction and Design Consistency | Identify inappropriate abstractions, premature indirection, and conflicting design patterns. |
| MAINT11 | Dead and Obsolete Code | Identify demonstrably unreachable, unused, or obsolete code that adds maintenance burden. |
| MAINT12 | Documentation and Contract Clarity | Identify missing or misleading documentation for non-obvious contracts, constraints, and business rules. |
| MAINT13 | Change Safety and Locality | Identify designs where small logical changes force widespread edits across unrelated components. |
| MAINT14 | Technology-Specific Maintainability | Identify stack-specific design anti-patterns that materially hinder clarity, testing, or evolution. |

*Detailed criteria, evidence, and remediation per rule are defined in [`references/checklist.md`](references/checklist.md).*

## 4. Review Workflow

1. **Inspect Context**: Review changed diffs, call graphs, module boundaries, and surrounding context.
2. **Detect Stack**: Identify language, framework idioms, and architecture patterns (see Section 2).
3. **Select Rules**: Match diff changes against applicable rules (MAINT01–MAINT14).
4. **Evaluate Evidence**: Consult [`references/checklist.md`](references/checklist.md) to substantiate findings with visible code structures and concrete maintenance risks.
5. **Score & Deduplicate**: Apply [`references/scoring-guide.md`](references/scoring-guide.md). Consolidate multiple symptoms sharing a single root cause into one finding.
6. **Generate Output**: Format findings using the Scorecard Aggregator schema below.

## 5. Review Principles

- **Evidence-Based**: Report maintainability defects supported by concrete code evidence; explain why the code is difficult to understand, test, or modify.
- **Context & Scale Proportionality**: Account for codebase scale, module purpose, and component lifecycle; avoid prescribing unnecessary abstractions or interfaces for simple code.
- **No Subjective Style Bashing**: Do not enforce arbitrary aesthetic choices (e.g. line count limits or formatting preferences) without demonstrable maintainability impact.
- **Tolerate Incidental Duplication**: Do not treat small, coincidental, or intentionally decoupled repetitions as harmful duplication.
- **Abstraction Parsimony**: Do not introduce indirection, wrapper classes, or generic interfaces unless there is a concrete need for polymorphism or testing isolation.
- **Safe Review Scope**: Inspect the diff and relevant surrounding code; verify whether a symbol or dependency is truly dead before reporting.
- **Root-Cause Deduplication**: Multiple symptoms stemming from one design flaw (e.g. god class) must produce one primary finding.
- **Review Only**: State the defect and provide actionable remediation advice; do not generate automated rewrites or unsolicited refactorings.

## 6. Output Contract & References

Return structured output compatible with the Code Review Portal Scorecard Aggregator:

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

| Field | Type | Required | Description |
|---|---|---|---|
| `ruleId` | string | Yes | MAINT01–MAINT14 stable identifier |
| `title` | string | Yes | Concise issue summary |
| `severity` | string | Yes | `critical`, `high`, `medium`, or `low` |
| `confidence` | string | Yes | `high`, `medium`, or `low` |
| `file` | string | Yes | Repository-relative path |
| `lineStart` | integer | Yes | First line number of the relevant code |
| `lineEnd` | integer | No | End line number of the relevant code block |
| `evidence` | string | Yes | Concrete code observation supporting the issue |
| `impact` | string | Yes | Maintenance risk (readability, coupling, defect risk) |
| `recommendation` | string | Yes | Actionable guidance preserving existing behavior |
| `technology` | string | No | Inferred technology stack |
| `status` | string | No | Finding lifecycle status (default: `open`) |

Integration rules for the aggregator:
- `score` starts at 100, reduced by deductions according to [`references/scoring-guide.md`](references/scoring-guide.md).
- `blocked` is set to `true` when score is below 60 and includes at least one `critical` or `high` finding.
- Low-confidence observations must be recorded in `uncertainty_notes` and incur 0 deductions.

## 7. Supporting References

- **Inspection Checklist**: [`references/checklist.md`](references/checklist.md) — Detailed criteria, evidence, and remediation per rule.
- **Scoring Guide**: [`references/scoring-guide.md`](references/scoring-guide.md) — Severity tiers, deduction formulas, exceptions, and merge blocking.
- **Validation Suite**: [`validation/test-suite.json`](validation/test-suite.json) — Automated test cases for detection and false-positive verification.

