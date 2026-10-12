# Maintainability Review Checklist

This reference defines detection criteria, evidence requirements, false positives, and remediation guidance for engineering maintainability rules (MAINT01–MAINT14). Use during Step 4 of the Review Workflow in `SKILL.md`.

---

## 1. Shared Review Principles

- **Evidence-Based:** Report only observable maintainability risks substantiated by code in the diff and immediate context.
- **Context-Aware:** Consider repository scale, module purpose, and lifecycle; avoid prescribing patterns unsuited to the domain.
- **No Style Bashing:** Do not flag subjective aesthetics, line counts, or formatting preferences without demonstrated harm.
- **Root-Cause Deduplication:** Consolidate multiple symptoms sharing a single design flaw into one primary finding.
- **Abstraction Parsimony:** Do not recommend indirection, interfaces, or refactorings without a clear maintenance benefit.
- **Impact-Driven Severity:** Evaluate severity by defect risk, test impediment, and blast radius rather than raw code volume.

### Rule Disambiguation Boundaries

| Overlap Pair | Boundary Guidance |
|---|---|
| **MAINT01 vs. MAINT10** | **MAINT01** for copy-pasted logic blocks; **MAINT10** for missing, leaky, or over-engineered abstractions. |
| **MAINT04 vs. MAINT06** | **MAINT04** for multi-responsibility functions; **MAINT06** for bloated, multi-domain classes or modules. |
| **MAINT05 vs. MAINT13** | **MAINT05** for direct structural coupling and instantiation; **MAINT13** for shotgun-surgery ripple edits. |
| **MAINT07 vs. MAINT12** | **MAINT07** for swallowed or masked runtime errors; **MAINT12** for missing or misleading contract documentation. |

---

## 2. Maintainability Rules (MAINT01–MAINT14)

### MAINT01 — Code Duplication
- **Purpose:** Prevent repeated business rules or algorithms that increase modification costs and cause divergence bugs.
- **Detect:** Verbatim or near-identical business calculations, parallel polymorphic `if`/`switch` chains, or duplicate validation sequences across multiple locations.
- **Evidence:** Concrete code references showing duplicate logic performing the same domain task in multiple places.
- **Avoid:** Incidental 1–2 line boilerplate, intentionally isolated test setup logic, or coincidental structural similarity across unrelated domains.
- **Remediation:** Consolidate genuinely duplicated logic into a focused shared function or module where this reduces maintenance cost without introducing unnecessary coupling.
- **Severity:** High for core financial/auth calculations; Medium for repeated validation or transformation logic; Low for minor utility helpers.

### MAINT02 — Complexity and Readability
- **Purpose:** Eliminate deeply tangled control flow, excessive nesting, and compound conditions that hinder comprehension.
- **Detect:** Nesting depth exceeding 4 levels, tangled compound boolean expressions without explanatory variables, or convoluted conditional branch matrices.
- **Evidence:** Visible multi-level nested blocks or complex boolean logic obscuring execution paths.
- **Avoid:** Flat parser token switches, naturally branching state machines with lookup tables, or documented performance-critical algorithms.
- **Remediation:** Flatten control flow using guard clauses (early returns), lookup maps, or decomposition into cohesive helper functions.
- **Severity:** High if complex unverified branches guard core business paths; Medium for nested loops and conditionals; Low for localized parsing logic.

### MAINT03 — Naming and Intent Clarity
- **Purpose:** Prevent ambiguous, cryptic, or misleading names that obscure symbol intent, types, or side-effects.
- **Detect:** Single-letter or cryptic names outside short loop counters, misleading names contradicting behavior (e.g., `get*` mutating state), double-negative booleans (`isNotDisabled`), or confusing casing anomalies.
- **Evidence:** Identifiers in the diff where the name obscures meaning or misrepresents the underlying operation.
- **Avoid:** Standard domain conventions (`x, y` coordinates, loop index `i`), framework idioms (`req, res`), or concise lambda variables.
- **Remediation:** Rename identifiers to clearly express their domain purpose, type, and behavioral contract using language naming standards.
- **Severity:** High if a misleading name masks destructive or side-effecting operations; Medium if ambiguous names make bug fixes error-prone.

### MAINT04 — Function and Method Responsibility
- **Purpose:** Ensure functions have a single well-defined responsibility and manageable scope.
- **Detect:** Functions mixing distinct concerns (e.g., parsing, DB querying, external HTTP calls, and notification), boolean flag arguments splitting execution into unrelated codepaths, or heavy business logic embedded directly in UI templates.
- **Evidence:** A single function executing multiple orthogonal side-effects or spanning distinct architectural tiers.
- **Avoid:** Linear orchestration pipelines delegating cleanly to sub-methods, or cohesive multi-step transform sequences.
- **Remediation:** Decompose into smaller focused functions; replace boolean flag parameters with separate targeted methods or strategy objects.
- **Severity:** High when mixed concerns prevent isolated testing or error recovery; Medium for oversized multi-phase functions.

### MAINT05 — Coupling and Dependency Management
- **Purpose:** Prevent tight structural coupling and hardcoded concrete dependencies that impede testing and modularity.
- **Detect:** Direct instantiation of infrastructure clients (DB, HTTP, I/O) inside domain logic, deep Law-of-Demeter object navigation, circular package imports, or deep relative imports bypassing public module boundaries.
- **Evidence:** Direct `new ConcreteService()` calls in business code or chained property navigations accessing collaborator internals.
- **Avoid:** Instantiation of simple value objects/DTOs, or cohesive private helpers within the same package boundary.
- **Remediation:** Inject dependencies via constructors or parameters, and depend on abstractions or protocols where substitution is needed.
- **Severity:** High if hardcoded dependencies block hermetic unit testing; Medium for multi-hop object traversal.

### MAINT06 — Cohesion and Module Boundaries
- **Purpose:** Prevent omnibus God classes and unstructured dumping-ground modules that group unrelated concerns.
- **Detect:** Classes spanning multiple disjoint business domains, classes with methods operating on disjoint subsets of fields, or generic `utils`/`helpers` files containing unrelated utilities.
- **Evidence:** Class or module combining unrelated domain imports and responsibilities with low method cohesion.
- **Avoid:** Intentional facade patterns aggregating sub-services, or cohesive modules fully managing one domain entity.
- **Remediation:** Split bloated classes into focused domain services, and organize modules by business capability rather than technical catch-alls.
- **Severity:** High for bloated classes causing merge conflicts and cross-domain contamination; Medium for generic helper dumping grounds.

### MAINT07 — Error Handling Clarity
- **Purpose:** Eliminate swallowed exceptions, opaque error responses, and suppressed stack traces that obscure runtime diagnostics.
- **Detect:** Empty `catch`/`except` blocks, catching exceptions and returning generic `null`/`None` without context, re-raising without preserving root cause chains, or throwing bare generic `Exception`/`Error` on business paths instead of domain error types.
- **Evidence:** Exception handlers containing `pass`, empty blocks, unchained custom rethrows, or masks that conceal underlying failure causes.
- **Avoid:** Top-level global error handlers converting exceptions to standard HTTP error responses, or documented fallbacks with diagnostic logging.
- **Remediation:** Catch specific exception types, preserve root cause chaining, and throw domain-specific exceptions with contextual logging.
- **Severity:** Critical/High if swallowed errors conceal data corruption or transaction failure; Medium if root cause context is discarded.

### MAINT08 — Configuration and Magic Values
- **Purpose:** Ensure environment settings, thresholds, and operational values are centralized rather than hardcoded.
- **Detect:** Magic numbers/strings embedded in calculations, hardcoded URLs or credentials, scattered direct reads of environment variables across deep domain logic, or raw inline system prompts assembled with ad-hoc string formatting across files.
- **Evidence:** Unnamed numeric or string literals in business logic, or raw `os.environ`/`process.env` calls outside configuration roots.
- **Avoid:** Idiomatic constants (`0`, `1`, `""`), known fixed test fixtures, or standard self-explanatory HTTP status codes.
- **Remediation:** Extract named constants for business literals, and centralize environment configuration and prompt templates into structured settings.
- **Severity:** Critical for hardcoded credentials; High for hardcoded endpoints/tax rates; Medium for uncentralized environment access.

### MAINT09 — Testability and Test Structure
- **Purpose:** Eliminate architectural obstacles that prevent hermetic, deterministic unit testing and dependency stubbing.
- **Detect:** Non-deterministic API calls (`datetime.now()`, `random()`, `UUID()`) embedded directly in domain logic, global mutable state, or functions/agent nodes mutating shared input state in-place rather than returning state updates.
- **Evidence:** Hardcoded external clock/random calls or global mutable singletons inside business calculations.
- **Avoid:** Outer adapter layers interfacing directly with OS/runtime APIs, or standard integration tests hitting test databases.
- **Remediation:** Inject time/random providers as parameters or dependencies, and eliminate global mutable state and in-place state mutation.
- **Severity:** High if non-deterministic calls prevent reliable testing of core business logic; Medium for hardcoded system time sources.

### MAINT10 — Abstraction and Design Consistency
- **Purpose:** Prevent over-engineering, premature abstractions, leaky abstractions, or conflicting design patterns within a module.
- **Detect:** Speculative indirection (single-implementation interfaces wrapped in pass-through delegations), overly complex generic hierarchies for simple tasks, or leaky implementation details.
- **Evidence:** Multi-layered wrapper classes forwarding calls without added logic, or conflicting architectural paradigms in adjacent files.
- **Avoid:** Standard project-wide architectural contracts, or public library interfaces explicitly designed for external extensibility.
- **Remediation:** Flatten redundant indirection layers, prefer composition over inheritance, and apply consistent architectural patterns.
- **Severity:** High if inheritance hierarchies obscure domain logic; Medium for redundant pass-through wrappers.

### MAINT11 — Dead and Obsolete Code
- **Purpose:** Remove demonstrably unreachable, unused, or obsolete code that adds cognitive load and maintenance overhead.
- **Detect:** Unreachable code following unconditional `return`/`throw`, unreferenced private functions or variables, unused dangling imports, or blocks of commented-out historical code.
- **Evidence:** Code immediately following unconditional jumps, unreferenced private symbols, or dead commented-out code in the diff.
- **Avoid:** Public API methods intended for external consumers, required interface contracts, or active feature-flagged branches.
- **Remediation:** Remove dead and commented-out code; rely on version control history for code retrieval.
- **Severity:** Medium for large commented-out blocks or unreachable complex logic; Low for unused local variables or imports.

### MAINT12 — Documentation and Contract Clarity
- **Purpose:** Ensure non-obvious algorithms, business rules, and public interface contracts are accurately documented.
- **Detect:** Complex algorithms or regex patterns lacking explanatory documentation, public APIs missing parameter/error contracts, stale docstrings contradicting code behavior, or comments explaining *what* trivial code does instead of *why* (business rationale, constraints).
- **Evidence:** High-complexity code blocks or public interfaces lacking documentation, or docstrings directly contradicting parameter/return types.
- **Avoid:** Self-explanatory, cleanly named functions, or trivial getters/setters.
- **Remediation:** Add concise docstrings explaining non-obvious business rules, assumptions, and error contracts; update misleading comments.
- **Severity:** High if misleading documentation masks security, side-effects, or data validation contracts; Medium for undocumented complex algorithms.

### MAINT13 — Change Safety and Locality
- **Purpose:** Prevent shotgun surgery where minor routine updates require widespread, error-prone edits across disparate files.
- **Detect:** Scattered manual type checks/switches when adding domain variants, repetitive field-by-field manual mappings across tiers, or shared mutable global state breaking distant components.
- **Evidence:** Repetitive manual mapping or type checking duplicated across multiple files in the diff.
- **Avoid:** True cross-cutting framework upgrades, or initial feature introductions touching standard vertical slices.
- **Remediation:** Encapsulate variant behavior using polymorphism or exhaustive pattern matching, and centralize domain mapping contracts.
- **Severity:** High when domain changes risk silent breakages across distant modules; Medium for repetitive manual mappings.

### MAINT14 — Technology-Specific Maintainability
- **Purpose:** Address stack-specific design anti-patterns that materially hinder clarity, testability, or maintainability.
- **Detect:**
  - **Python:** Heavy import-time side-effects, wildcard imports (`from m import *`), or mutable default arguments.
  - **.NET/C#:** Mismatched DI service lifetimes (e.g., Scoped dependency injected into Singleton creating captive dependencies).
  - **React/TS:** Massive components mixing data fetching, state, effects, and JSX; prop drilling across 5+ component levels; rendering numeric values with `&&` short-circuiting causing visual glitches (`0`); or pervasive untyped `any` in component contracts.
  - **SQL:** Monolithic stored procedures with nested dynamic SQL strings, implicit conversions, and un-modular structure.
  - **AI-Agent / LLM Systems:** Hardcoded monolithic prompts embedded inside tool execution logic; untyped agent state dictionaries passed across workflow steps without schema contracts; or node functions mutating shared graph state in-place.
- **Evidence:** Visible violation of established stack-specific maintainability practices in the diff.
- **Avoid:** Pragmatic framework idioms (e.g., Next.js server components co-locating data and view; simple single-turn scripts).
- **Remediation:** Refactor into framework-idiomatic structures (custom hooks, proper DI lifetime registration, scoped SQL CTEs/views, decoupled prompt/state schemas).
- **Severity:** High for captive DI dependencies or memory leaks; Medium for prop-drilling or monolithic SQL procedures.
