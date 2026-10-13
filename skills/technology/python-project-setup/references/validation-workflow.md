# Validation Workflow Reference

## 1. Inspection & Check Selection Workflow

To validate a Python project setup or verify implementation changes, dynamically discover configured tools and run only applicable, safe verification checks.

```text
+-----------------------------------------------------------------------+
| 1. Inspect Manifests & Tool Configurations                             |
|    - Read pyproject.toml, uv.lock, ruff.toml, mypy.ini, buf.yaml, Docker  |
+-----------------------------------+-----------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------+
| 2. Detect Available Tools in Runtime Environment                     |
|    - Check availability of uv/poetry, pytest, ruff, mypy, buf, docker |
+-----------------------------------+-----------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------+
| 3. Execute Verification Commands & Capture Standard Output           |
|    - Run available commands; mark uninstalled tools as "unavailable"  |
+-----------------------------------+-----------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------+
| 4. Synthesize Verification Findings & Report Evidence                 |
|    - Distinguish confirmed failures from missing optional tools      |
+-----------------------------------------------------------------------+
```

---

## 2. Standard Validation Matrix

| Check Type | Detection Trigger | Primary Command | Alternative Command |
|---|---|---|---|
| **Lockfile Consistency** | `uv.lock` present | `uv lock --check` | `poetry check` |
| **Linting & Code Style** | `[tool.ruff]` in `pyproject.toml` | `uv run ruff check .` | `ruff check .` / `flake8` |
| **Formatting** | `[tool.ruff]` or `[tool.black]` | `uv run ruff format --check .` | `black --check .` |
| **Static Type Checking** | `[tool.mypy]` or `pyrightconfig.json` | `uv run mypy .` | `mypy src/` |
| **Unit & Integration Tests** | `tests/` directory present | `uv run pytest` | `pytest` |
| **Protobuf / ConnectRPC Linting** | `buf.yaml` present | `buf lint` | `buf generate` |
| **Container Build Smoke Test** | `Dockerfile` present | `docker compose config` | `docker build --no-cache -t test-img .` |

---

## 3. Step-by-Step Validation Procedures

### 1. Project Configuration Validation
- Verify `pyproject.toml` exists and parses cleanly as valid TOML.
- Verify `.python-version` matches `requires-python` in `pyproject.toml`.
- Verify `.env.example` is present if environment configuration is referenced in code.

### 2. Dependency & Lockfile Consistency
- Check if `pyproject.toml` dependencies match lockfile state.
- Command for `uv`:
  ```bash
  uv lock --check
  ```
- If lockfile is out of sync, report lockfile drift as a build configuration issue.

### 3. Code Quality & Static Analysis
- **Linting**:
  ```bash
  uv run ruff check .
  ```
- **Type Checking**:
  ```bash
  uv run mypy src/
  ```
- If static analysis or type checking fails, extract specific file paths, line numbers, and error codes for evidence reporting.

### 4. Test Execution
- Run unit and integration test suite:
  ```bash
  uv run pytest --maxfail=5 --disable-warnings
  ```
- Confirm test execution count, passes, and failures.

### 5. Protobuf & ConnectRPC Validation (When Applicable)
- If `buf.yaml` exists in repository or `backend/`:
  ```bash
  buf lint
  ```
- Check for breaking changes against main branch:
  ```bash
  buf breaking --against '.git#branch=main'
  ```

---

## 4. Handling Missing Tools & Execution Guardrails

1. **Missing Optional Tools**: If a tool (e.g. `buf`, `mypy`, `docker`) is configured in the repository but not installed in the local execution environment:
   - Mark the check status as `UNAVAILABLE` or `NOT_EXECUTED`.
   - Do **NOT** report missing optional tools as code syntax errors or security violations.
2. **Never Claim False Verification**: Never state or log that a check passed unless the command was executed in the shell and returned exit code `0`.
3. **Destructive Command Protection**: Never run commands that overwrite repository source files (e.g. `ruff format .` or `buf generate`) during code review tasks. Only run auto-formatters or generators when explicitly instructed during implementation tasks.

