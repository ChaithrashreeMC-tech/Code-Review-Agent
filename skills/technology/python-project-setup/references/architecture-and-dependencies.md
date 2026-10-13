# Architecture & Dependency Boundaries Reference

## 1. Clean Architecture Overview

When reviewing or building repositories that employ Clean Architecture (such as the ConnectRPC project template), enforce strict unidirectional dependency boundaries. Inner layers must never depend on outer layers.

```text
       +-------------------------------------------------+
       |                  API / Delivery                 |
       |  (ConnectRPC Services, Controllers, Interceptors)|
       +------------------------+------------------------+
                                |
                                v
       +-------------------------------------------------+
       |                  Infrastructure                 |
       |   (SQLAlchemy ORM, Redis, External HTTP Clients)|
       +------------------------+------------------------+
                                |
                                v
       +-------------------------------------------------+
       |                   Application                   |
       |  (Use Cases, DTOs, Repository Port Interfaces)   |
       +------------------------+------------------------+
                                |
                                v
       +-------------------------------------------------+
       |                     Domain                      |
       |   (Entities, Value Objects, Core Business Rules) |
       +-------------------------------------------------+
```

---

## 2. Layer Responsibilities & Permitted Imports

### 1. Domain Layer (`src/[project_name]/domain/`)
- **Responsibility**: Houses pure business entities, value objects, domain exceptions, and core business rules.
- **Allowed Imports**: Standard Python library (`dataclasses`, `enum`, `typing`, `uuid`, `datetime`).
- **Prohibited Imports**: SQLAlchemy, ConnectRPC, Pydantic, HTTP libraries (`requests`, `httpx`), database drivers, or any outer layer (`application`, `infrastructure`, `api`).

### 2. Application Layer (`src/[project_name]/application/`)
- **Responsibility**: Encapsulates use cases, application service workflows, input/output DTOs, and abstract repository/service interfaces (ports).
- **Allowed Imports**: `domain` layer modules, standard library, typing abstractions.
- **Prohibited Imports**: Database models, ORM engines (`infrastructure`), ConnectRPC generated stubs or HTTP frameworks (`api`).

### 3. Infrastructure Layer (`src/[project_name]/infrastructure/`)
- **Responsibility**: Implements abstract interfaces defined in `application` (e.g. database repositories, Redis caching, email gateways, external REST clients).
- **Allowed Imports**: `domain` and `application` layers, ORM packages (SQLAlchemy, Alembic), HTTP clients (`httpx`), cloud SDKs.
- **Prohibited Imports**: Delivery controllers or API stubs (`api`).

### 4. API / Delivery Layer (`src/[project_name]/api/`)
- **Responsibility**: Handles incoming RPC or HTTP requests, parses payloads, invokes `application` use cases, catches domain/application errors, and returns formatted responses.
- **Allowed Imports**: `domain`, `application`, generated stubs (`api/gen/`), ConnectRPC package (`connectrpc`), framework tools.
- **Prohibited Imports**: Direct SQL execution or ORM database session instantiations (delegate data access to `infrastructure` via `application`).

### 5. Agents Layer (`src/[project_name]/agents/`)
- **Responsibility**: Orchestrates AI agent workflows, prompt management, tool bindings, and state transitions (e.g., LangGraph).
- **Allowed Imports**: `domain`, `application`, agent frameworks (LangChain, LangGraph).
- **Prohibited Imports**: Direct presentation/API interceptors.

---

## 3. Dependency Inversion Principle (DIP)

Outer infrastructure layers must implement abstract interfaces defined by inner application layers:

```python
# GOOD: Application layer defines abstract interface (Port)
# src/my_project/application/interfaces/user_repository.py
from abc import ABC, abstractmethod
from my_project.domain.user import User

class UserRepositoryPort(ABC):
    @abstractmethod
    def get_by_id(self, user_id: str) -> User | None:
        pass

# GOOD: Infrastructure layer implements interface (Adapter)
# src/my_project/infrastructure/persistence/user_repository_impl.py
from my_project.application.interfaces.user_repository import UserRepositoryPort
from my_project.domain.user import User

class PostgresUserRepository(UserRepositoryPort):
    def get_by_id(self, user_id: str) -> User | None:
        # DB lookup logic using SQLAlchemy...
        return user
```

---

## 4. Circular Import Prevention

Circular imports occur when two modules depend on each other directly or indirectly. Prevent circular import crashes in Python by enforcing these guidelines:

1. **Type-Only Annotations**: Use `from __future__ import annotations` (PEP 563) and `if TYPE_CHECKING:` blocks for static type hints to prevent runtime import evaluation cycles.
   ```python
   from __future__ import annotations
   from typing import TYPE_CHECKING

   if TYPE_CHECKING:
       from my_project.application.service import UserService
   ```
2. **Decoupled Abstract Ports**: Move shared interface definitions or data transfer objects to dedicated interface modules rather than importing concrete implementations.
3. **Avoid Package `__init__.py` Over-Exporting**: Do not eagerly import every internal class inside root `__init__.py` files if it pulls concrete infrastructure dependencies into pure domain packages.

---

## 5. Architectural Scoping Rules

- **Do Not Force Clean Architecture on Simple Services**: Flat layouts, FastAPI apps, or library packages should follow their own established architecture. Only enforce multi-layer Clean Architecture boundaries when the codebase explicitly employs that pattern or when working within a ConnectRPC backend template.
- **Reporting Architecture Findings**: When inspecting illegal cross-layer imports (e.g. `domain` importing `infrastructure.db`), report the technical evidence to the `skill-eng-modularity` engineering skill for finding creation and scoring.

