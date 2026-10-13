# Python Database Migrations & Connection Pooling Reference

## 1. Connection Lifecycle & Async Sessions

- **Context Manager**: Always manage sessions with context managers (`async with AsyncSession() as session:`) or FastAPI dependency generators.
- **Connection Leak**: Unclosed sessions or raw DB-API connections tie up database connection pool slots.

```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from typing import AsyncGenerator

engine = create_async_engine("postgresql+asyncpg://user:pass@localhost/dbname", pool_size=10, max_overflow=20)
AsyncSessionFactory = async_sessionmaker(engine, expire_on_commit=False)

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

## 2. Transaction Boundaries & Exception Safety

- **Atomic Blocks**: Wrap multi-step mutations in `async with session.begin():`.
- **Explicit Rollbacks**: Roll back open transactions inside `except` blocks to prevent corrupting connection state in the pool.

## 3. Alembic Migrations

- **Revision Control**: Auto-generate migrations using `alembic revision --autogenerate -m "add_users_table"`.
- **Review Auto-Generations**: Always inspect generated migration files (`alembic/versions/*.py`) for missing column types, constraints, or destructive `drop_table()` operations.
- **Migration Execution**: Run `alembic upgrade head` during deployment pipelines.

