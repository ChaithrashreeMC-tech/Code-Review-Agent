---
name: python-project-setup
description: >-
  Activate when scaffolding, configuring, inspecting, or refactoring Python project structures,
  package layouts, environment setup, pyproject.toml configuration, uv/poetry/pip dependency
  management, build tooling, Clean Architecture layer boundaries, ConnectRPC/Protobuf setups,
  or setup validation workflows.
---

# Python Project Setup Technology Skill

## 1. Purpose & Activation

This technology skill provides domain-specific Python environment, package layout, build configuration, dependency management, and architectural guidance for Code Review Agent workflows.

**Activate when** creating, inspecting, configuring, reviewing, or refactoring Python repositories—including general Python packages, FastAPI/Flask services, Django apps, SQLAlchemy projects, LangGraph agents, monorepo services, or schema-first ConnectRPC/Protobuf backends.

## 2. Supported Use Cases

1. **Code Review**: Provide Python setup evidence and context to core engineering skills (`skill-eng-maintainability`, `skill-eng-modularity`, `skill-eng-security`, `skill-eng-performance`, `skill-eng-business-logic`).
2. **New Project Setup**: Scaffold idiomatic, reproducible Python projects following established repository conventions or standard templates.
3. **Feature Implementation**: Add new modules, layers, or dependencies while maintaining existing package boundaries and lockfile consistency.
4. **Refactoring**: Reorganize legacy code into standard layouts (`src/` layout, Clean Architecture, or multi-service monorepo) without breaking imports.
5. **Project Maintenance**: Audit `.python-version`, `pyproject.toml`, lockfiles (`uv.lock`, `poetry.lock`), linter configurations, and build/test workflows.

## 3. Project Type Detection & Reference Selection

Before providing guidance or making changes, inspect the repository root to detect project type, package manager, Python version, and architectural style. Load only the necessary reference documents:

| Detected Aspect | Evidence Markers | Reference Document |
|---|---|---|
| **Project Structure & Layout** | `pyproject.toml`, `src/`, `backend/`, `tests/`, `buf.yaml` | [`references/project-structure.md`](references/project-structure.md) |
| **Architecture & Imports** | `domain/`, `application/`, `infrastructure/`, `api/`, `graph.py` | [`references/architecture-and-dependencies.md`](references/architecture-and-dependencies.md) |
| **Tooling & Dependencies** | `uv.lock`, `poetry.lock`, `Pipfile`, `.python-version`, `.env` | [`references/tooling-and-dependency-management.md`](references/tooling-and-dependency-management.md) |
| **Validation Workflow** | `pytest`, `ruff.toml`, `mypy.ini`, `buf.gen.yaml`, `Dockerfile` | [`references/validation-workflow.md`](references/validation-workflow.md) |

## 4. Execution Workflow

1. **Inspect Repository Evidence**: Read manifests (`pyproject.toml`, `setup.py`), lockfiles, directory tree, `.python-version`, and tool configs.
2. **Identify Repository Type**:
   - *ConnectRPC Backend*: `backend/proto/`, `buf.yaml`, `api/gen/`, `src/[pkg]/domain/`.
   - *FastAPI/Flask Web Service*: `app/main.py`, `routers/`, `views/`, `schemas/`.
   - *Django Web App*: `manage.py`, `[pkg]/settings.py`.
   - *LangGraph Agent*: `graph.py`, `state.py`, `nodes/`.
   - *Standard Python Package*: `src/[pkg_name]/__init__.py`, `pyproject.toml`.
   - *Monorepo*: Root workspace manifests, `services/`, `apps/`, or `backend/` + `frontend/`.
3. **Establish Baseline Conventions**: Treat existing working architecture as the baseline. Apply ConnectRPC or Clean Architecture templates **only** when explicitly required or detected.
4. **Load Relevant References**: Read specific reference files based on task mode (review vs implementation).
5. **Execute Task**:
   - *Review Mode*: Identify structural flaws, stale lockfiles, or illegal imports; report evidence to applicable engineering review skills.
   - *Implementation Mode*: Apply scoped changes following detected conventions without altering unrelated project files.
6. **Verify & Report**: Run available, safe verification commands (e.g. `uv lock --check`, `ruff check`, `mypy`, `pytest`). Report passed checks, failed checks, and unavailable tools separately.

## 5. Technology Guidance vs. Engineering Scoring

- **Technology Skill Responsibility**: Provide accurate Python structural knowledge, package layout rules, tool command invocation, and lockfile validation.
- **Engineering Skill Responsibility**: Evaluate overall quality, assign numerical scores (0–10 scale), determine merge blocking (`blocked: true/false`), and emit findings using standard engineering scorecard schemas.
- This technology skill does **not** create a separate numeric score or scoring guide.

## 6. Safety Guardrails & Policy

- **No Unnecessary Restructuring**: Do not reorganize or convert a working flat/package layout into ConnectRPC or Clean Architecture unless requested.
- **No Destructive Commands**: Do not run `rm -rf`, `git reset --hard`, or overwrite configuration files without authorization.
- **No Unauthorized Dependencies**: Do not add new external packages or change dependency lockfiles unless explicitly part of the task scope.
- **Never Edit Generated Code**: Files inside `api/gen/` or `*_pb2.py` must be updated via code generators (`buf generate`), never hand-edited.
- **Accurate Tool Reporting**: If optional tools (`mypy`, `buf`, `docker`) are not installed, report them as "tool unavailable", not as code security or architecture violations.

## 7. Supporting References

- **Project Structure**: [`references/project-structure.md`](references/project-structure.md) — Layout detection, ConnectRPC monorepo template, package boundaries, generated code locations.
- **Architecture & Dependencies**: [`references/architecture-and-dependencies.md`](references/architecture-and-dependencies.md) — Clean Architecture layers, import directions, circular dependency prevention.
- **Tooling & Dependency Management**: [`references/tooling-and-dependency-management.md`](references/tooling-and-dependency-management.md) — Python versioning, `uv`/`poetry`/`pip`, lockfile reproducibility, environment variables.
- **Validation Workflow**: [`references/validation-workflow.md`](references/validation-workflow.md) — Inspection checklist, linting, type-checking, test execution, Buf/Protobuf generation, container smoke checks.
- **Validation Suite**: [`validation/test-suite.json`](validation/test-suite.json) — Automated test suite verifying detection and setup rules.

