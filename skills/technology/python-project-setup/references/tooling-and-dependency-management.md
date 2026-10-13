# Tooling & Dependency Management Reference

## 1. Package Manager Detection & Workflow

Always detect the repository's active package manager before running commands or modifying manifests. Respect the project's existing lockfile and tool choice.

| Package Manager | Indicator Files | Preferred Execution Commands |
|---|---|---|
| **uv** (Primary ConnectRPC/Fast Template) | `uv.lock`, `pyproject.toml` | `uv sync`, `uv lock`, `uv add <pkg>`, `uv run <cmd>` |
| **Poetry** | `poetry.lock`, `pyproject.toml` | `poetry install`, `poetry lock`, `poetry add <pkg>`, `poetry run <cmd>` |
| **Pipenv** | `Pipfile.lock`, `Pipfile` | `pipenv install`, `pipenv run <cmd>` |
| **pip / venv** | `requirements.txt`, `setup.py` | `pip install -r requirements.txt` |

---

## 2. Python Version Declaration

1. **`.python-version` File**: Specifies the target Python runtime version for local virtual environments and version managers (`pyenv`, `uv`).
   ```text
   3.11.8
   ```
2. **`pyproject.toml` Requirement**: Enforce version boundaries in the `[project]` table to prevent installation on incompatible runtimes:
   ```toml
   [project]
   name = "my-service"
   version = "0.1.0"
   requires-python = ">=3.11,<3.13"
   ```

---

## 3. Lockfile Consistency & Reproducibility

- **Lockfile Enforcement**: Production deployments and CI pipelines must use deterministic lockfiles (`uv.lock`, `poetry.lock`) to guarantee byte-for-byte reproducible installations across environments.
- **Out-of-Sync Detection**: If `pyproject.toml` dependency declarations are updated without regenerating or syncing the lockfile, the build pipeline is in an inconsistent state.
  - For `uv`: Run `uv lock --check` to verify `uv.lock` is up-to-date with `pyproject.toml`.
  - For `poetry`: Run `poetry check` or `poetry lock --check`.
- **Dependency Pinning Rules**:
  - Production dependencies must specify version constraints (e.g. `pydantic >=2.6.0,<3.0.0` or `connectrpc ~=0.4.0`).
  - Wildcard dependency specifiers (`"*"`) in production dependencies are prohibited.

---

## 4. `pyproject.toml` Configuration Standards

Use `pyproject.toml` (PEP 518, PEP 621) as the single source of truth for project metadata, dependencies, and tool settings:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "my-connectrpc-service"
version = "0.1.0"
description = "Enterprise ConnectRPC Python Backend Service"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "connectrpc>=0.4.0",
    "protobuf>=4.25.0",
    "pydantic>=2.6.0",
    "httpx>=0.27.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "ruff>=0.3.0",
    "mypy>=1.8.0",
]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "B", "I", "UP"]
ignore = ["E501"]

[tool.mypy]
python_version = "3.11"
strict = true
ignore_missing_imports = true

[tool.pytest.ini_options]
minversion = "8.0"
testpaths = ["tests"]
python_files = ["test_*.py"]
asyncio_mode = "auto"
```

---

## 5. Environment Variables & Configuration Handling

1. **`.env.example` Template**: Every repository requiring environment configuration must track a sanitized `.env.example` template file in git containing non-sensitive default variables and comments.
2. **`.gitignore` Safeguard**: Ensure `.env`, `.env.local`, and secrets files are strictly listed in `.gitignore`.
3. **Structured Settings Parsing**: Prefer `pydantic-settings` or `python-dotenv` to parse and validate environment variables with strong types at application startup:
   ```python
   # src/my_service/config.py
   from pydantic_settings import BaseSettings

   class Settings(BaseSettings):
       DATABASE_URL: str
       PORT: int = 8080
       DEBUG: bool = False

       class Config:
           env_file = ".env"

   settings = Settings()
   ```

---

## 6. Safe Dependency Updates & Modifications

When tasked with adding or updating dependencies:
1. Check existing locked versions in `uv.lock` or `poetry.lock`.
2. Execute official manager update commands (`uv add <package>` or `poetry add <package>`).
3. Verify that new package additions do not introduce conflicting constraints or security vulnerabilities.
4. Verify that lockfile changes are committed alongside `pyproject.toml`.

