# TC-007: Async Function Return Typing Fixture

import asyncio

async def fetch_account_name(account_id: int) -> str | None:
    await asyncio.sleep(0.01)
    if account_id > 0:
        return f"Account_{account_id}"
    return None

