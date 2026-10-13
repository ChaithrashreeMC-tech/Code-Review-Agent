from sqlalchemy.ext.asyncio import AsyncSession

async def fetch_records_unclosed_session(engine):
    # Violation: Instantiates raw AsyncSession without context manager, risking connection leak
    session = AsyncSession(engine)
    result = await session.execute("SELECT 1")
    return result

async def fetch_records_managed_session(engine):
    # Safe: Uses async with context manager to ensure session closure
    async with AsyncSession(engine) as session:
        result = await session.execute("SELECT 1")
        return result

