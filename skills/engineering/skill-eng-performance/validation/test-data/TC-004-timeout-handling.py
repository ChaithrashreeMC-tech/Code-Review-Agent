# TC-004: Timeout Handling (PERF05 violation)
# Expected: PERF05 finding, severity=high, confidence=high
# Technology: Python / httpx + tenacity

import httpx
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential


# --- VIOLATION: No timeout on external HTTP call ---
async def fetch_payment_status_no_timeout(payment_id: str) -> dict:
    """
    VIOLATION: HTTP call with no timeout. If the payment gateway stalls,
    this coroutine hangs indefinitely, eventually exhausting the thread pool
    or connection pool.
    """
    async with httpx.AsyncClient() as client:  # VIOLATION: no timeout
        response = await client.get(
            f"https://payments.example.com/status/{payment_id}"
        )
        return response.json()


# --- VIOLATION: Retry with no cap ---
@retry(wait=wait_exponential(multiplier=1, min=1))  # VIOLATION: no stop=
async def call_flaky_service(endpoint: str) -> dict:
    """
    VIOLATION: Retry with exponential backoff but no maximum attempt count.
    Will retry forever on a permanently failed service, amplifying load.
    """
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.get(endpoint)
        response.raise_for_status()
        return response.json()


# --- VIOLATION: asyncio.wait without timeout ---
async def gather_reports_no_timeout(report_ids: list[str]) -> list:
    """
    VIOLATION: Awaits tasks with no timeout. A stalled external call
    blocks all results indefinitely.
    """
    tasks = [fetch_payment_status_no_timeout(rid) for rid in report_ids]
    return await asyncio.gather(*tasks)  # VIOLATION: no timeout


# --- SAFE IMPLEMENTATIONS ---
async def fetch_payment_status_safe(payment_id: str) -> dict:
    """
    SAFE: Explicit 5-second timeout. Raises httpx.TimeoutException on stall.
    """
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.get(
            f"https://payments.example.com/status/{payment_id}"
        )
        return response.json()


@retry(
    wait=wait_exponential(multiplier=1, min=1, max=10),
    stop=stop_after_attempt(3),  # SAFE: maximum 3 attempts
)
async def call_flaky_service_safe(endpoint: str) -> dict:
    """
    SAFE: Retry with exponential backoff capped at 3 attempts and 10-second
    max wait. Will not retry indefinitely.
    """
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.get(endpoint)
        response.raise_for_status()
        return response.json()


async def gather_reports_safe(report_ids: list[str]) -> list:
    """
    SAFE: asyncio.wait_for wraps the gather with a 30-second ceiling.
    """
    tasks = [fetch_payment_status_safe(rid) for rid in report_ids]
    return await asyncio.wait_for(asyncio.gather(*tasks), timeout=30.0)

