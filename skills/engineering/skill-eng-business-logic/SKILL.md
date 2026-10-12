---
name: skill-eng-business-logic
description: >-
  Activate when reviewing code changes that implement, modify, or affect business
  requirements, domain rules, calculation formulas, workflows, eligibility criteria,
  state transitions, input validations, cross-field constraints, boundary conditions,
  data consistency invariants, or acceptance criteria across user interfaces, backend
  services, data persistence, and integration layers. Evaluates functional correctness
  and fidelity against documented feature specifications and use cases.
---

# Engineering Business Logic Review Skill

## 1. Purpose & Activation

This skill evaluates pull requests and code modifications to verify that implemented behavior correctly and completely satisfies documented business requirements, domain rules, calculations, workflows, and acceptance criteria across all application layers.

**Activate when** code changes alter business rules, calculations, eligibility checks, pricing/discount logic, approval workflows, state machines, domain validations, data persistence consistency, or user journey outcomes; or when review context references feature specifications, user stories, acceptance criteria, business bugs, or functional requirements.

## 2. Specification Discovery & Authority

Locate relevant feature specifications dynamically without hardcoding environment paths:
1. **Target Feature Identification**: Resolve the feature identifier from PR metadata, branch naming, linked work items, specification references, or orchestrator context.
2. **Dynamic Discovery**: Locate specification files under the repository's `specs/` directory (or orchestrator-provided path), discovering `business-spec.md`, `design-spec.md`, `tech-spec.md`, and acceptance criteria documents.
3. **Specification Authority Hierarchy**:
   - **Primary Authority**: Business requirements, use cases, domain rules, and acceptance criteria define expected behavior.
   - **Supporting Context**: Technical specs, architectural designs, and implementation plans provide structural context but do not override business requirements.
   - **Explicit Precedence**: Approved decisions, change records, and versioned amendments supersede older baseline specs.
   - **Ambiguity & Conflicts**: If specifications are missing, ambiguous, or contradictory, record an uncertainty note rather than inventing business requirements.

## 3. Business Logic Rules

| ID | Rule | Objective |
|---|---|---|
| BIZ01 | Specification Alignment | Verify changed behavior completely and accurately satisfies documented functional requirements. |
| BIZ02 | Business Rules & Domain Calculations | Verify formulas, rates, discounts, financial computations, and domain logic produce correct results. |
| BIZ03 | Workflow Ordering & State Transitions | Verify lifecycle states, approval sequences, prerequisites, and transitions follow documented rules. |
| BIZ04 | Validation & Domain Invariants | Verify required fields, cross-field dependencies, ranges, and domain entity constraints are enforced. |
| BIZ05 | Boundary Values & Edge Case Handling | Verify extreme values, zero/empty states, threshold equalities, and date/time boundaries behave correctly. |
| BIZ06 | Data Consistency & Side Effect Completion | Verify dependent entity updates, atomic invariants, ledger entries, and related records are preserved. |
| BIZ07 | Error Handling & Business Failure Paths | Verify rejected operations, invalid inputs, and failure conditions produce specified business outcomes. |
| BIZ08 | Idempotency & Duplicate Operation Guarding | Verify duplicate actions, retries, and replays do not trigger unintended business side-effects. |
| BIZ09 | Cross-Layer Business Consistency | Verify calculations, validation rules, and domain outcomes remain synchronized across UI and backend. |
| BIZ10 | Acceptance Criteria Coverage | Verify all explicit positive, negative, and edge acceptance criteria scenarios are fulfilled. |

*Detailed criteria, evidence requirements, and false-positive guidance are in [`references/checklist.md`](references/checklist.md).*

## 4. Review Workflow

1. **Inspect Context & Scope**: Identify changed files, affected entry points, and domain boundaries in the PR diff.
2. **Discover Specifications**: Locate feature documents in `specs/` or orchestrator context; extract business rules and acceptance criteria.
3. **Map Execution Paths**: Trace requirement execution across UI components, backend services, domain models, and persistence.
4. **Compare Expected vs. Implemented**: Evaluate whether implemented logic, formulas, and conditions match specified rules.
5. **Verify Boundary & Failure Paths**: Check threshold operators, boundary conditions, edge inputs, and error outcomes.
6. **Trace Multi-Layer Consistency**: Confirm client-side checks and backend domain logic enforce identical invariants.
7. **Verify Idempotency & State Safety**: Confirm repeated executions and state transitions follow lifecycle rules.
8. **Substantiate Code Evidence**: Verify findings with concrete line references and specification citations.
9. **Score & Deduplicate**: Apply [`references/scoring-guide.md`](references/scoring-guide.md); consolidate multi-layer symptoms into one root cause finding.
10. **Generate Structured Output**: Output findings adhering to the Scorecard Aggregator schema below.

## 5. Review Principles & False-Positive Controls

- **Evidence-Based**: Every finding must cite explicit specification criteria and concrete code evidence demonstrating the functional discrepancy.
- **Specification Authority**: Do not assume unstated requirements or invent domain rules; report missing/ambiguous specs in `uncertainty_notes`.
- **No Design Preference Enforcement**: Do not flag code solely because it uses an alternative design pattern or coding style if the business outcome is correct.
- **Root-Cause Deduplication**: When a single business logic defect manifests across multiple files or tiers, report one finding with supporting references.
- **Layer Agnostic**: Evaluate business correctness wherever logic resides; verify cross-layer consistency without penalizing architecture choices.
- **Review Only**: Identify functional defects and provide clear domain remediation; do not generate unsolicited automated code rewrites.

## 6. Output Contract & Aggregator Integration

Return structured output compatible with the Code Review Portal Scorecard Aggregator:

```json
{
  "dimension": "business_logic",
  "score": 8.0,
  "findings": [
    {
      "ruleId": "BIZ02",
      "title": "Incorrect Tiered Discount Threshold Calculation",
      "severity": "high",
      "confidence": "high",
      "file": "src/domain/pricing_service.py",
      "lineStart": 42,
      "lineEnd": 58,
      "evidence": "Applied 15% discount for orders >= $500 instead of specified > $500 threshold from business-spec.md Section 3.2",
      "impact": "Orders exactly at $500 receive unauthorized discount, leading to margin leakage",
      "recommendation": "Update condition from 'total >= 500' to 'total > 500' to match pricing specification",
      "technology": "Python",
      "status": "open"
    }
  ],
  "uncertainty_notes": [],
  "blocked": true
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `ruleId` | string | Yes | BIZ01–BIZ10 stable identifier |
| `title` | string | Yes | Concise business logic issue summary |
| `severity` | string | Yes | `critical`, `high`, `medium`, or `low` |
| `confidence` | string | Yes | `high`, `medium`, or `low` |
| `file` | string | Yes | Repository-relative path |
| `lineStart` | integer | Yes | First line number of the relevant code |
| `lineEnd` | integer | No | End line number of the relevant code block |
| `evidence` | string | Yes | Code observation and specification requirement citation |
| `impact` | string | Yes | Business, financial, workflow, or compliance risk |
| `recommendation` | string | Yes | Actionable guidance aligning code with specification |
| `technology` | string | No | Inferred technology stack |
| `status` | string | No | Finding lifecycle status (default: `open`) |

Integration rules for the aggregator:
- `score` is calculated directly on a native 0.0–10.0 scale, reduced by deductions according to [`references/scoring-guide.md`](references/scoring-guide.md).
- `blocked` is set to `true` when the dimension score is below 9.0 or when any confirmed critical violation is present.
- 10.0 (10/10) indicates pass with zero violations; 9.0 (9/10) indicates pass with at most one minor non-blocking finding and no critical violations.
- Ambiguities, missing specifications, or unverified requirements are recorded in `uncertainty_notes` (0.0 deduction).

## 7. Supporting References

- **Inspection Checklist**: [`references/checklist.md`](references/checklist.md) — Detailed criteria, evidence, and remediation per rule.
- **Scoring Guide**: [`references/scoring-guide.md`](references/scoring-guide.md) — Severity tiers, deduction formulas, exceptions, and merge blocking.
- **Validation Suite**: [`validation/test-suite.json`](validation/test-suite.json) — Automated test cases for detection and false-positive verification.

