# Python Code Coverage & Quality Tooling Reference

## 1. Code Coverage (`coverage.py` / `pytest-cov`)

- **Configuration**: Standardize coverage settings in `pyproject.toml` under `[tool.coverage.run]` and `[tool.coverage.report]`.
- **Branch Coverage**: Always enable `branch = true` to verify execution paths in conditionals.
- **Exclusions**: Omit non-production code (tests, migrations, generated code like `*_pb2.py`). Use `# pragma: no cover` sparingly for unreachable code.

```toml
# pyproject.toml
[tool.coverage.run]
branch = true
source = ["src"]
omit = ["*/tests/*", "*/gen/*"]

[tool.coverage.report]
fail_under = 80
show_missing = true
exclude_lines = [
    "pragma: no cover",
    "if TYPE_CHECKING:",
    "raise NotImplementedError",
]
```

## 2. Modern Linting & Formatting (`ruff` / `black` / `flake8`)

- **Ruff**: High-performance linter & formatter replacing `flake8`, `isort`, `black`, and `bandit`.
- **Formatting Rules**: Standard 88-character line length, double quotes, clean import ordering.
- **Key Linter Rules**:
  - `F` (Pyflakes): Undefined variables, unused imports.
  - `E`/`W` (pycodestyle): Syntax errors, formatting anomalies.
  - `I` (isort): Clean import sorting.
  - `B` (flake8-bugbear): Common bugs and design pitfalls.
  - `S` (flake8-bandit): Automated security issue detection.

```toml
# pyproject.toml
[tool.ruff]
line-length = 88
target-version = "py310"

[tool.ruff.lint]
select = ["E", "F", "W", "I", "B", "S"]
ignore = ["S101"] # Ignore assert warning in test code
```

## 3. Security Linting (`bandit`)

- Static analyzer for common security vulnerabilities (hardcoded passwords, `eval()`, SQL injection hazards, insecure PRNGs, `shell=True` in subprocesses).
- Run `bandit -r src/` or configure via `ruff.lint.select = ["S"]`.

## 4. Quality Thresholds & Gates

| Quality Metric | Target Threshold | Action if Failed |
|---|---|---|
| **Unit Test Pass Rate** | 100% | Block build; fix failing tests |
| **Branch Coverage** | >= 80% | Add missing test branches |
| **Linter Diagnostic Errors** | 0 errors (`ruff check`) | Autofix or fix manually |
| **Security Alerts** | 0 High/Medium alerts | Remediate vulnerability immediately |

