# Python Project Structure & Layout Reference

## 1. Overview & Project Type Detection

Every Python repository follows structural conventions suited to its domain, framework, and deployment target. Before modifying files or conducting reviews, identify the project type by inspecting key indicator files in the repository root.

### Repository Type Matrix

| Project Type | Indicator Files & Directories | Core Characteristics |
|---|---|---|
| **ConnectRPC Backend** | `backend/proto/`, `buf.yaml`, `api/gen/`, `src/[pkg]/domain/` | Schema-first Protobuf, ConnectRPC handlers, Clean Architecture layout. |
| **General Package / Library** | `pyproject.toml`, `src/[pkg_name]/__init__.py` | `src/` layout, typed package (`py.typed`), library exports. |
| **FastAPI / Flask App** | `app/main.py`, `routers/`, `views/`, `schemas/` | HTTP web service, API endpoints, dependency injection, async handlers. |
| **Django Application** | `manage.py`, `[pkg]/settings.py`, `apps/` | Monolithic or app-based framework, ORM models, settings modules. |
| **SQLAlchemy Service** | `alembic/`, `models/`, `db/session.py` | Data-tier service, database migrations, declarative models. |
| **LangGraph Agent App** | `graph.py`, `state.py`, `nodes/`, `tools/` | State-machine graph workflow, LLM agent orchestration, state schemas. |
| **Monorepo** | Root `pyproject.toml` workspace, `services/`, `apps/`, `packages/` | Multi-service or backend/frontend repository sharing common utilities. |

---

## 2. ConnectRPC Enterprise Project Template

When creating or reviewing a schema-first ConnectRPC Python backend, use the enterprise ConnectRPC project structure documented below as the primary reference template.

```text
tests/
├── conftest.py
├── application_tests/
├── api_tests/
├── agent_tests/
└── regression_suite/

backend/
├── proto/
│   └── [project_name]/v1/
├── src/
│   └── [project_name]/
│       ├── __init__.py
│       ├── py.typed
│       ├── domain/
│       ├── application/
│       ├── infrastructure/
│       ├── agents/
│       ├── api/
│       │   ├── gen/
│       │   ├── services/
│       │   └── interceptors/
│       └── main.py
├── buf.yaml
├── buf.gen.yaml
├── pyproject.toml
├── uv.lock
├── .python-version
├── .env.example
├── README.md
├── .gitignore
├── Dockerfile
├── .dockerignore
└── docker-compose.yml

TestResults/
Specs/
```

### Template Component Responsibilities

1. **Root `tests/` Directory**: Positioned at the repository root to support end-to-end integration and cross-layer test suites (`application_tests/`, `api_tests/`, `agent_tests/`, `regression_suite/`).
2. **`backend/proto/`**: Houses `.proto` schema files defining ConnectRPC services and message contracts (`[project_name]/v1/`).
3. **`backend/src/[project_name]/`**: The primary Python package directory containing business layers:
   - `domain/`: Pure domain entities and rules.
   - `application/`: Use cases and interface contracts.
   - `infrastructure/`: External database, messaging, and API implementations.
   - `agents/`: Reserved for LLM and agent orchestration logic when required.
   - `api/services/`: ConnectRPC service handler implementations.
   - `api/interceptors/`: Request authentication, logging, and error interceptors.
   - `api/gen/`: Generated Protobuf and ConnectRPC code (`_pb2.py`, `_connect.py`).
4. **`pyproject.toml` & `uv.lock`**: Managed inside `backend/` for service dependency locking and tool configuration.
5. **`buf.yaml` & `buf.gen.yaml`**: Protobuf linting, breaking change detection, and ConnectRPC code generation settings.
6. **`TestResults/` & `Specs/`**: Root directories for test execution reports and project specifications.

---

## 3. Alternative Python Project Layouts

Do **not** enforce the ConnectRPC template on repositories built for other frameworks. Respect existing working project layouts:

### Standard Python Package (`src/` Layout)
```text
pyproject.toml
uv.lock
README.md
src/
└── my_package/
    ├── __init__.py
    ├── py.typed
    ├── core.py
    └── utils.py
tests/
    ├── conftest.py
    └── test_core.py
```
- **Rule**: Use the `src/` layout for reusable libraries to prevent accidental imports of uninstalled local packages during test execution.

### FastAPI / Flask Web Service Layout
```text
pyproject.toml
app/
├── __init__.py
├── main.py
├── config.py
├── api/
│   ├── v1/
│   └── router.py
├── models/
├── services/
└── schemas/
tests/
```
- **Rule**: Group routes by API version or domain feature. Maintain separate Pydantic schemas for request/response payloads.

### LangGraph Agent Application Layout
```text
pyproject.toml
src/
└── agent_service/
    ├── __init__.py
    ├── main.py
    ├── graph.py
    ├── state.py
    ├── nodes/
    └── tools/
tests/
```
- **Rule**: Keep agent state definitions in `state.py` and graph node functions in `nodes/`. Isolate LLM tools inside `tools/`.

---

## 4. Package Rules, Boundaries & Generated Code

### Package Markers (`__init__.py` & `py.typed`)
- Every directory containing Python modules must include an `__init__.py` file to form explicit package namespaces.
- Reusable or typed Python packages must include a zero-byte `py.typed` marker file (PEP 561) in their root package folder so static type checkers (`mypy`, `pyright`) recognize inline type annotations.

### Generated Code Rules (`api/gen/`)
- All auto-generated code (e.g. Protobuf `*_pb2.py`, ConnectRPC `*_connect.py`, OpenAPI client stubs) must reside in dedicated generated directories such as `api/gen/`.
- **CRITICAL**: Hand editing files inside `api/gen/` or generated stub files is strictly prohibited. Any schema or stub updates must be performed by executing `buf generate` or the corresponding code generator tool.
- Exclude generated code directories from linting (`ruff`) and static analysis (`mypy`) via tool configuration if stubs contain third-party formatting incompatibilities.

### Test Placement Rules
- Maintain test files mirror-structured under `tests/` matching source module paths (e.g. `src/my_pkg/domain/user.py` -> `tests/unit/domain/test_user.py`).
- Shared test fixtures, mock factories, and database setup must reside in `tests/conftest.py`.

