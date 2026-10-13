# Gate 1 Code Review: Validation Workflow

This guide defines the 6-stage operational workflow for Gate 1 local code validation, supporting both Local Developer Validation (**Mode A**) and Entry Guard Agent Orchestration (**Mode B**).

---

## 1. Execution Modes

| Mode | Invocation | Target | Output |
|---|---|---|---|
| **Mode A: Local Developer** | CLI (`python -m src.gate1.runner`) or IDE hook | Local working tree (staged, unstaged, untracked) | Terminal / Markdown report |
| **Mode B: Entry Guard Agent** | Automated agent platform trigger | Repository workspace / branch diff | Platform scorecard / review gate |

*Both modes share the exact same 6-stage workflow, validation standards, and blocking rules.*

---

## 2. Six-Stage Validation Process

### Stage 1: Repository & Change Inspection
1. **Root Discovery**: Locate repository root via Git (`git rev-parse --show-toplevel`) or project root manifests (`package.json`, `pyproject.toml`, `*.sln`).
2. **Stack Detection**: Identify active languages/frameworks:
   - *Python*: `pyproject.toml`, `requirements.txt`, `setup.py`
   - *TypeScript / JS*: `package.json`, `tsconfig.json`
   - *.NET / C#*: `*.csproj`, `*.sln`
   - *Java / Kotlin*: `pom.xml`, `build.gradle`
   - *Go / Rust / SQL*: `go.mod`, `Cargo.toml`, `*.sql`
3. **Change Detection**: Inspect modified, added, deleted, and untracked files via `git status --porcelain` and diffs. Extract surrounding code context for reviewers.

### Stage 2: Build & Static Validation
- Discover and execute native build/typecheck commands (`npm run build`, `tsc --noEmit`, `python -m py_compile`, `dotnet build`, `mvn compile`, `cargo check`).
- **Blocking Rule**: Any compilation error or syntax failure immediately blocks the review (`status: "BLOCKED"`). Missing toolchains are marked `unavailable` (`status: "INCOMPLETE"`).

### Stage 3: Automated Testing
- Discover and run configured test suites (`pytest`, `npm test`, `jest`, `dotnet test`, `mvn test`, `go test ./...`, `cargo test`).
- Record test metrics (`total`, `passed`, `failed`, `skipped`).
- **Blocking Rule**: Any test failure blocks the review (`status: "BLOCKED"`). Missing test runners without configuration record `status: "INCOMPLETE"`.

### Stage 4: Engineering Review Dispatch
Dispatch modified files and surrounding context to the 5 specialized engineering review skills:
1. [`skill-eng-security`](../skill-eng-security/SKILL.md): Injection, secrets, auth, OWASP (SEC01–SEC12).
2. [`skill-eng-performance`](../skill-eng-performance/SKILL.md): N+1 queries, async I/O, resource leaks (PERF01–PERF14).
3. [`skill-eng-maintainability`](../skill-eng-maintainability/SKILL.md): Complexity, duplication, readability (MAINT01–MAINT14).
4. [`skill-eng-modularity`](../skill-eng-modularity/SKILL.md): Layer boundaries, circular deps, god classes (MOD01–MOD12).
5. [`skill-eng-business-logic`](../skill-eng-business-logic/SKILL.md): Spec alignment, calculations, states (BIZ01–BIZ10).

### Stage 5: Result Aggregation & Scoring
- **0.0–10.0 Scale**: Initial score `10.0`. Base deductions: `critical` = 6.0, `high` = 4.0, `medium` = 2.0, `low` = 1.0 (with confidence multipliers). Formula: $\text{Score} = \max(0.0, 10.0 - \sum \text{deductions})$.
- **Deduplication**: Consolidate multi-rule findings caused by the same underlying defect into one root cause finding.
- **Dimension Blocking**: Score $< 9.0$ or any confirmed critical finding blocks the dimension.

### Stage 6: Report Generation & Readiness Verdict
Evaluate overall Gate 1 status:
- **`PASS`**: All builds/tests pass, all dimensions $\ge 9.0$, zero critical findings, $\le 1$ minor issue $\implies$ **Ready for PR**.
- **`BLOCKED`**: Any build failure, test failure, dimension $< 9.0$, or critical violation $\implies$ **Blocked (Fix required)**.
- **`INCOMPLETE`**: Required build tools, test runners, or sub-agents failed to run, with no blocking failures $\implies$ **Incomplete (Re-run/configure)**.
- *Conflict Precedence*: Blocking failures always take precedence over incomplete checks.

---

## 3. Safety & Non-Destructive Principles

- **Zero Code Mutation**: Strictly read-only analysis; never mutates or formats source files.
- **No Remote Git Actions**: Never runs `git push`, commits, or opens PRs automatically.
- **Actionable Remediation**: Provides clear manual fix recommendations for developers.
