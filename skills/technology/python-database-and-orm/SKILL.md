---
name: python-database-and-orm
description: >-
  Activate when writing, inspecting, or reviewing Python database persistence layers,
  ORMs (SQLAlchemy 2.0, SQLModel, Tortoise, Django ORM), Alembic migrations, connection pooling, transactions, or SQL query safety.
---

# Python Database & ORM Technology Skill

## 1. Purpose & Activation

Provides technology guidance for Python database integration, ORM model design, schema migrations, transaction safety, and query performance in Code Review Agent workflows.

**Activate when** inspecting or writing Python database code involving SQLAlchemy (async/sync), SQLModel, Tortoise ORM, Django ORM, Alembic migrations, connection pools, SQL injection risks, N+1 query patterns, or transaction boundaries.

## 2. Supported Use Cases

1. **Code Review**: Extract SQL query safety, connection leaks, missing transaction rollbacks, and N+1 query risks to supply evidence to core engineering skills (`skill-eng-security`, `skill-eng-performance`, `skill-eng-maintainability`).
2. **Persistence Layer Scaffolding**: Implement type-safe SQLAlchemy 2.0 `Mapped[...]` models, Alembic migrations, and `async_sessionmaker` factories.
3. **Query Optimization**: Convert eager/lazy loading issues into explicit `joinedload` / `selectinload` queries to prevent N+1 overhead.
4. **Transaction & Resource Safety**: Ensure context-managed DB sessions (`async with AsyncSession() as session:`) with deterministic rollback handling.

## 3. Reference Selection

| Topic | Focus | Reference Document |
|---|---|---|
| **ORM Frameworks & Models** | SQLAlchemy 2.0, SQLModel, Tortoise ORM, Django ORM, parameterized SQL | [`references/orm-frameworks-and-models.md`](references/orm-frameworks-and-models.md) |
| **Migrations & Pooling** | Alembic migrations, `async_engine`, session lifecycle, transaction boundaries | [`references/migrations-and-connection-pooling.md`](references/migrations-and-connection-pooling.md) |
| **Validation Workflow** | Database test fixtures, N+1 detection, connection leak checks, SQL safety | [`references/validation-workflow.md`](references/validation-workflow.md) |

## 4. Execution Workflow

1. **Inspect Persistence Setup**: Identify ORM (SQLAlchemy 2.0, SQLModel, Django), driver (`asyncpg`, `psycopg`, `aiosqlite`), migration tool (`alembic`), and session scoping.
2. **Select Reference**: Load relevant guide (`orm-frameworks-and-models.md` for models/queries; `migrations-and-connection-pooling.md` for sessions/migrations).
3. **Execute & Evaluate**:
   - *Review Mode*: Flag unparameterized raw SQL, missing session context managers, un-handled transaction exceptions, or N+1 queries.
   - *Implementation Mode*: Define `Mapped` columns, configure Alembic `env.py`, add `selectinload` relationships.
4. **Report Results**: State verified DB models, migration status, session management integrity, and query safety.

## 5. Technology Guidance vs. Engineering Scoring

- **Technology Skill Responsibility**: Provide accurate SQLAlchemy/Alembic mechanics, connection pool settings, and query optimization patterns.
- **Engineering Skill Responsibility**: Evaluate overall security, performance, or maintainability and assign numeric scores (0–10 scale).
- This technology skill does **not** generate a separate numeric score.

## 6. Supporting References

- **ORM Frameworks & Models**: [`references/orm-frameworks-and-models.md`](references/orm-frameworks-and-models.md)
- **Migrations & Pooling**: [`references/migrations-and-connection-pooling.md`](references/migrations-and-connection-pooling.md)
- **Validation Workflow**: [`references/validation-workflow.md`](references/validation-workflow.md)
- **Validation Suite**: [`validation/test-suite.json`](validation/test-suite.json)

