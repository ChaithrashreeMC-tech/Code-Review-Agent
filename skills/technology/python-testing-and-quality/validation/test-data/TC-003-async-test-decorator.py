import pytest
import asyncio

async def test_async_fetch_missing_mark() -> None:
    # Violation: Async test function without @pytest.mark.asyncio decorator will be skipped or fail silently
    await asyncio.sleep(0.01)
    result = "data"
    assert result == "data"

@pytest.mark.asyncio
async def test_async_fetch_with_mark() -> None:
    # Safe: Properly decorated with @pytest.mark.asyncio
    await asyncio.sleep(0.01)
    result = "data"
    assert result == "data"

