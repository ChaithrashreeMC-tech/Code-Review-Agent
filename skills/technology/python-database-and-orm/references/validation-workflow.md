# Python Database & ORM Validation Workflow Reference

## 1. Database Test Isolation

- Use in-memory SQLite (`sqlite+aiosqlite:///:memory:`) or ephemeral PostgreSQL containers (`testcontainers`) for automated tests.
- Re-create schema or run table rollbacks between tests to ensure test isolation.

```python
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

@pytest.fixture
async def test_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSession(engine) as session:
        yield session
```

## 2. Code Review Checklist for Database Code

1. **SQL Injection**: Are all raw SQL statements using parameterized query bindings (`text("... :param")`)?
2. **N+1 Query Hazards**: Are foreign key relationship accesses in loops using `selectinload` or `joinedload`?
3. **Session Lifecycle**: Are database sessions managed using `async with` context managers or `yield` generators?
4. **Transaction Rollbacks**: Do exception handlers execute explicit transaction rollbacks before re-raising?
5. **Alembic Drift**: Are database model changes matched by an up-to-date Alembic migration script?

