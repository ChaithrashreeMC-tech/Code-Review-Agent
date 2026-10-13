---
name: python-testing-and-quality
description: >-
  Activate when writing, inspecting, or reviewing Python test suites (pytest, unittest),
  fixtures, mocking, async test cases, code coverage (coverage.py, pytest-cov), linting (ruff, flake8, black),
  security linting (bandit), or test automation workflows.
---

# Python Testing & Quality Technology Skill

## 1. Purpose & Activation

Provides technology guidance for Python automated testing, mock isolation, coverage thresholds, linting, and static quality checks within Code Review Agent workflows.

**Activate when** creating, updating, or reviewing Python test files (`test_*.py`, `conftest.py`), `pytest` fixtures, `unittest.mock` usage, async tests (`pytest-asyncio`), code coverage configurations (`pyproject.toml`, `.coveragerc`), or code style/linter settings (`ruff`, `flake8`, `black`, `bandit`).

## 2. Supported Use Cases

1. **Code Review**: Extract test completeness, mock safety, lint violations, and coverage gaps to supply context to engineering skills (`skill-eng-maintainability`, `skill-eng-security`, `skill-eng-business-logic`).
2. **Test Implementation & Refactoring**: Write robust, isolated `pytest` test cases with proper fixtures, parametrization, and clean assertions.
3. **Mocking & Isolation**: Replace network/DB side effects with safe, explicit mocks (`unittest.mock.AsyncMock`, `pytest_mock.mocker`).
4. **Quality & Lint Enforcement**: Configure and execute `ruff`, `black`, `coverage`, and `bandit` checks across Python repositories.

## 3. Reference Selection

| Topic | Focus | Reference Document |
|---|---|---|
| **Testing & Mocking** | `pytest`, fixtures, parametrization, async testing, `unittest.mock` | [`references/testing-frameworks-and-mocking.md`](references/testing-frameworks-and-mocking.md) |
| **Coverage & Quality Tooling** | `pytest-cov`, `ruff`, `black`, `flake8`, `bandit`, quality gates | [`references/code-coverage-and-quality-tooling.md`](references/code-coverage-and-quality-tooling.md) |
| **Validation Workflow** | Execution commands, report parsing, failure analysis, safety guardrails | [`references/validation-workflow.md`](references/validation-workflow.md) |

## 4. Execution Workflow

1. **Inspect Test Setup**: Locate test runner (`pytest`), `conftest.py`, linter configs (`pyproject.toml`, `ruff.toml`), and existing test directory.
2. **Select Reference**: Load relevant guide (`testing-frameworks-and-mocking.md` for test design; `code-coverage-and-quality-tooling.md` for linters).
3. **Execute & Evaluate**:
   - *Review Mode*: Identify missing assertions, unmocked side effects, weak coverage, or linter errors. Pass evidence to engineering skills.
   - *Implementation Mode*: Add unit/integration tests with clean fixtures; run `pytest` and `ruff check`.
4. **Report Results**: State passing/failing test count, coverage percentage, and linter diagnostic summary.

## 5. Technology Guidance vs. Engineering Scoring

- **Technology Skill Responsibility**: Define Python test practices, fixture scopes, mock idioms, and linter tool commands.
- **Engineering Skill Responsibility**: Evaluate overall maintainability, security, or business logic correctness and assign numeric scores (0–10 scale).
- This technology skill does **not** generate a separate numeric score.

## 6. Supporting References

- **Testing & Mocking**: [`references/testing-frameworks-and-mocking.md`](references/testing-frameworks-and-mocking.md)
- **Coverage & Tooling**: [`references/code-coverage-and-quality-tooling.md`](references/code-coverage-and-quality-tooling.md)
- **Validation Workflow**: [`references/validation-workflow.md`](references/validation-workflow.md)
- **Validation Suite**: [`validation/test-suite.json`](validation/test-suite.json)

