from sqlalchemy import text

async def find_user_by_name_unformatted(session, user_name: str):
    # Violation: Unsafe string formatting in raw SQL query allowing SQL injection
    query = text(f"SELECT * FROM users WHERE name = '{user_name}'")
    return await session.execute(query)

async def find_user_by_name_parameterized(session, user_name: str):
    # Safe: Parameterized query binding
    query = text("SELECT * FROM users WHERE name = :name")
    return await session.execute(query, {"name": user_name})

