# Python Testing & Quality Validation Workflow Reference

## 1. Local Validation Step Execution

Run quality commands in logical order: format/lint -> type check -> unit tests -> coverage report.

```bash
# 1. Formatting & Linting
ruff check .
ruff format --check .

# 2. Security Analysis
bandit -r src/

# 3. Test Suite Execution & Coverage
pytest --cov=src --cov-report=term-missing --cov-fail-under=80
```

## 2. Reviewing Existing Codebases

When reviewing Python test suites and quality setups:
1. Check whether test files exist and run without errors.
2. Verify that network, database, and filesystem side-effects are properly mocked.
3. Check for assertion-free tests (tests that execute functions without `assert`).
4. Validate that coverage thresholds are configured in `pyproject.toml` or `.coveragerc`.
5. Check linter rules for missing security or bugbear checks.

## 3. Guardrails & Rules

- **Do Not Mask Test Failures**: Never suppress test assertions or add dummy `try/except` blocks to force tests to pass.
- **Do Not Disable Linters Blindly**: Avoid `# noqa` or `# type: ignore` unless accompanied by explicit reasoning.
- **Isolate Environments**: Use isolated virtual environments (`uv venv`, `poetry run`, `venv`) when running tests and quality tools.

