from sqlalchemy import select
from sqlalchemy.orm import selectinload

async def get_user_orders_n_plus_1(session, user_id: int):
    # Violation: Lazy loading inside loop triggering N+1 queries
    users = (await session.execute(select(User))).scalars().all()
    orders = [u.orders for u in users] # N+1 query trigger
    return orders

async def get_user_orders_eager_loaded(session, user_id: int):
    # Safe: Explicitly eager loads relationship using selectinload
    stmt = select(User).options(selectinload(User.orders))
    users = (await session.execute(stmt)).scalars().all()
    return [u.orders for u in users]

