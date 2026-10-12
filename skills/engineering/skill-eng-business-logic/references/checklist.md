# Business Logic Review Checklist

This reference defines detection criteria, evidence requirements, false positives, and remediation guidance for engineering business logic review rules (BIZ01–BIZ10). Use during Step 4 of the Review Workflow in `SKILL.md`.

---

## 1. Shared Review Principles

- **Evidence-Based:** Report only observable discrepancies substantiated by explicit specification requirements and concrete code diff evidence.
- **Specification Authority:** Use `business-spec.md` and acceptance criteria as primary sources of truth; record specification ambiguities in `uncertainty_notes` instead of inventing rules.
- **No Style Bashing:** Do not report findings for design pattern or coding style choices when the business outcome strictly satisfies requirements.
- **Multi-Layer Analysis:** Evaluate business correctness across frontend, backend, database, and integration layers, verifying end-to-end consistency.
- **Root-Cause Deduplication:** Consolidate multi-layer or multi-file symptoms of a single business logic defect into one primary finding.
- **Impact-Driven Severity:** Evaluate severity based on financial risk, data integrity, regulatory compliance, and user journey disruption.

### Rule Disambiguation Boundaries

| Overlap Pair | Boundary Guidance |
|---|---|
| **BIZ01 vs. BIZ10** | **BIZ01** for broad functional requirement omissions or workflow mismatches; **BIZ10** for specific unmet positive/negative acceptance criteria scenarios. |
| **BIZ02 vs. BIZ05** | **BIZ02** for formula, rate, or mathematical calculation errors; **BIZ05** for boundary inequalities (`>` vs `>=`), zero/empty edge states, or date cutoffs. |
| **BIZ03 vs. BIZ08** | **BIZ03** for invalid state machine transitions or bypassed approval sequences; **BIZ08** for duplicate operation execution from network retries or replays. |
| **BIZ04 vs. BIZ06** | **BIZ04** for input constraints and entity invariants at entry/creation; **BIZ06** for cross-entity side-effects, audit trails, and multi-table consistency. |
| **BIZ07 vs. BIZ08** | **BIZ07** for business failure paths and error outcome handling; **BIZ08** for duplicate request guarding and idempotency keys. |

---

## 2. Business Logic Rules (BIZ01–BIZ10)

### BIZ01 — Specification Alignment
- **Purpose:** Ensure modified code completely and accurately fulfills documented functional requirements and primary use cases.
- **Detect:** Omission of mandatory business steps; features executing contrary to documented use cases; silent departure from stated business flow.
- **Evidence:** Code diff missing required specification steps or implementing an alternative flow contradicted by specification documentation.
- **Avoid:** Implementation details left unspecified; unmentioned cosmetic UI styling choices; refactorings preserving identical business behavior.
- **Remediation:** Align feature execution flow with the documented functional requirements in the primary business specification.
- **Severity:** Critical if core revenue or regulatory functionality is missing; High if primary user journey deviates from specification.

### BIZ02 — Business Rules & Domain Calculations
- **Purpose:** Ensure mathematical formulas, tiered rates, discounts, financial computations, and domain algorithms produce correct results.
- **Detect:** Inverted operators, incorrect operator precedence, wrong formula constants, inverted percentage calculations, or misapplied tiered pricing rules.
- **Evidence:** Concrete calculation logic in code producing outputs that deviate from specified formulas or domain rules.
- **Avoid:** Floating-point rounding within documented tolerance; alternative mathematical factoring producing equivalent outputs.
- **Remediation:** Correct the formula or algorithm to strictly match specified business calculation rules and rounding policies.
- **Severity:** Critical for financial loss, overbilling, or legal non-compliance; High for incorrect pricing, tier rating, or fee calculations.

### BIZ03 — Workflow Ordering & State Transitions
- **Purpose:** Enforce valid lifecycle states, approval sequences, transition guards, and business operation ordering.
- **Detect:** Skipping mandatory approval states; allowing forbidden transitions (e.g., `CANCELLED -> COMPLETED`); executing downstream actions before prerequisites are validated.
- **Evidence:** State machine or workflow handler permitting invalid state transitions or omitting prerequisite checks specified in workflow rules.
- **Avoid:** Internal technical sub-states not restricted by domain rules; idempotent re-transitions to current state where explicitly permitted.
- **Remediation:** Implement state transition guards verifying current state and prerequisite conditions before permitting lifecycle mutations.
- **Severity:** Critical if unauthorized operations or bypassed security approvals occur; High for invalid state corruption.

### BIZ04 — Validation & Domain Invariants
- **Purpose:** Ensure domain entity constraints, required attributes, range limits, and cross-field business dependencies are strictly enforced.
- **Detect:** Missing required field enforcement; unvalidated cross-field constraints (e.g., `end_date >= start_date`); unenforced minimum/maximum domain limits.
- **Evidence:** Code accepting inputs or creating entity states that violate documented domain invariant rules.
- **Avoid:** Purely structural type validations already enforced by runtime/schema; optional fields with safe defaults.
- **Remediation:** Enforce domain invariants and cross-field constraints before processing or persisting entity state.
- **Severity:** High for corrupted domain entity persistence; Medium for missing user-facing cross-field input validations.

### BIZ05 — Boundary Values & Edge Case Handling
- **Purpose:** Ensure extreme values, zero/empty states, threshold inequalities, and date/time boundaries behave according to specifications.
- **Detect:** Off-by-one threshold errors (`>` vs `>=` or `<` vs `<=`); unhandled zero or negative amounts; incorrect leap year or timezone cutoff calculations.
- **Evidence:** Code logic misinterpreting threshold boundaries or failing on documented edge values.
- **Avoid:** Unspecified extreme hypothetical inputs with no business relevance; defensive handling that safely rejects invalid inputs.
- **Remediation:** Correct comparison operators and boundary branches to match documented inclusion/exclusion rules.
- **Severity:** High if boundary errors misclassify tier eligibility or violate SLA limits; Medium for localized off-by-one threshold triggers.

### BIZ06 — Data Consistency & Side Effect Completion
- **Purpose:** Ensure operations preserve multi-entity consistency, atomic business invariants, ledger entries, and required side-effect record updates.
- **Detect:** Updating parent entity balance without creating corresponding ledger/audit transactions; orphaned child records; partial updates failing to maintain cross-table consistency.
- **Evidence:** Execution path completing primary mutation while omitting mandatory secondary business records or related updates.
- **Avoid:** Asynchronously queued side-effects verified to execute reliably via event bus; optional analytics telemetry.
- **Remediation:** Wrap related mutations in transactional units or ensure all mandatory side-effect records are created.
- **Severity:** Critical for unbalanced accounting/ledger discrepancies; High for missing mandatory audit or parent-child sync.

### BIZ07 — Error Handling & Business Failure Paths
- **Purpose:** Ensure rejected business operations, domain rule violations, and failure conditions produce specified outcomes and revert pending state.
- **Detect:** Swallowing business rejections and reporting success; returning generic technical errors instead of specified domain rejection codes; failing to roll back partial business changes.
- **Evidence:** Failure branch returning success or leaving entity in inconsistent partial state following domain validation failure.
- **Avoid:** Standard unhandled runtime exceptions handled by global crash handlers; generic network timeout retries.
- **Remediation:** Return specified domain error responses and ensure all partial state changes are rolled back upon rejection.
- **Severity:** High if failed operations claim success or leave locked state; Medium for incorrect business error response codes.

### BIZ08 — Idempotency & Duplicate Operation Guarding
- **Purpose:** Prevent duplicate user actions, network retries, or webhook replays from causing unintended duplicate business effects.
- **Detect:** Payment or checkout handlers lacking idempotency keys/locks; repeated webhook events re-crediting accounts; duplicate submission causing multiple order creations.
- **Evidence:** State-mutating operation executing without deduplication checks or transaction locks against duplicate requests.
- **Avoid:** Naturally idempotent read/query operations; endpoints explicitly designed to allow repeated identical inserts.
- **Remediation:** Guard state-mutating operations with idempotency keys, unique request tokens, or optimistic concurrency locks.
- **Severity:** Critical for duplicate financial transactions or duplicate order fulfillment; High for repeated state mutations.

### BIZ09 — Cross-Layer Business Consistency
- **Purpose:** Ensure business rules, calculations, and eligibility constraints remain synchronized across UI, API, and persistence layers.
- **Detect:** UI applying different discount/validation rules than backend services; client allowing submission of records that backend immediately rejects due to mismatched rules.
- **Evidence:** Conflicting domain rule implementations or mismatched constants across frontend and backend code in the PR.
- **Avoid:** Progressive enhancement where frontend performs lightweight preliminary format checks while backend enforces full domain logic.
- **Remediation:** Synchronize validation rules, calculation constants, and eligibility logic across client and server layers.
- **Severity:** High for calculation divergence between UI quote and backend charge; Medium for mismatched form validation rules.

### BIZ10 — Acceptance Criteria Coverage
- **Purpose:** Verify that all explicit positive, negative, and edge scenario acceptance criteria defined in feature documents are satisfied.
- **Detect:** PR implementing the happy path but completely omitting negative acceptance criteria (e.g. user with expired subscription rejected); missing explicit edge criteria.
- **Evidence:** Feature implementation failing to handle an explicitly numbered acceptance criterion scenario defined in the specification.
- **Avoid:** Unstated hypothetical scenarios not part of the agreed acceptance criteria; acceptance criteria designated for a future sprint/phase.
- **Remediation:** Implement handlers for all documented positive, negative, and edge acceptance criteria scenarios.
- **Severity:** High if critical negative/rejection acceptance criteria are missed; Medium for secondary edge criteria omissions.

---

## Disambiguation & Boundary Rules

1. **Security vs. Business Logic:**
   - Evaluated under **Security** (do not report under BIZ): SQL injection, authentication flaws, missing authorization checks, cryptographic issues, XSS/CORS.
   - Evaluated under **Business Logic** (BIZ): Business permission rules, domain workflow gates, user role eligibility per specification.

2. **Maintainability vs. Business Logic:**
   - Evaluated under **Maintainability** (do not report under BIZ): Code duplication, long functions, naming conventions, docstrings, type annotations.
   - Evaluated under **Business Logic** (BIZ): Semantic domain calculation errors, missing state transitions, boundary condition defects.

3. **Performance vs. Business Logic:**
   - Evaluated under **Performance** (do not report under BIZ): N+1 database queries, unindexed queries, memory bloat, missing caching.
   - Evaluated under **Business Logic** (BIZ): Unreleased inventory reservations, omitted ledger writes, broken side-effect consistency.

4. **Missing Tests vs. Business Logic:**
   - Omission of automated tests in a PR is not a business logic violation unless there is concrete evidence of an actual business logic defect in the code.

