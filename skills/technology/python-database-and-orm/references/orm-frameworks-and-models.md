# Python ORM Frameworks & Models Reference

## 1. Modern SQLAlchemy 2.0 Models

- **Declarative Base**: Use `DeclarativeBase` with `Mapped[...]` and `mapped_column()` type annotations.
- **Async Engine**: Use `create_async_engine()` with `asyncpg` or `aiosqlite`.
- **Select Syntax**: Use `select(User).where(User.id == user_id)` instead of legacy `session.query(User)`.

```python
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs

class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255))
```

## 2. Preventing SQL Injection in Raw Queries

- **Never** interpolate variables into SQL strings (`f"SELECT * FROM users WHERE name='{name}'"`).
- **Always** use parameterized bindings with `text()` in SQLAlchemy or parameterized tuples in DB-API.

```python
from sqlalchemy import text

# Safe parameterized raw SQL query
stmt = text("SELECT id, username FROM users WHERE email = :email")
result = await session.execute(stmt, {"email": user_email})
```

## 3. Mitigating N+1 Query Overhead

- **N+1 Hazard**: Accessing lazy-loaded relationships in loops triggers a separate SQL query per iteration.
- **Eager Loading**: Use `selectinload()` or `joinedload()` explicitly in `select()` statements.

```python
from sqlalchemy.orm import selectinload

# Prevents N+1 by eager loading orders in a single JOIN or secondary SELECT
stmt = select(User).options(selectinload(User.orders)).where(User.is_active == True)
users = (await session.execute(stmt)).scalars().all()
```

## 4. SQLModel & Tortoise ORM

- **SQLModel**: Combines Pydantic v2 and SQLAlchemy `Mapped` definitions (`class User(SQLModel, table=True)`).
- **Tortoise ORM**: Async ORM for asyncio applications (`await User.filter(id=1).first()`).

