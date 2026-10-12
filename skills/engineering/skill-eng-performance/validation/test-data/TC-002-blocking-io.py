# TC-002: Blocking I/O in Async Context (PERF01 violation)
# Expected: PERF01 finding, severity=high, confidence=high
# Technology: Python / asyncio + httpx

import asyncio
import time
import httpx
import requests  # sync library


# --- VIOLATION ---
async def fetch_user_profile_blocking(user_id: int) -> dict:
    """
    VIOLATION: Uses synchronous requests.get() inside an async function.
    Blocks the event loop for the duration of the HTTP call.
    All other coroutines are stalled while this executes.
    """
    # VIOLATION: blocking HTTP call — stalls the event loop
    response = requests.get(f"https://api.example.com/users/{user_id}")
    response.raise_for_status()
    return response.json()


async def process_report_blocking() -> dict:
    """
    VIOLATION: time.sleep() in async context blocks the event loop.
    Should use asyncio.sleep() instead.
    """
    time.sleep(2)  # VIOLATION: blocks event loop for 2 seconds
    return {"status": "done"}


# --- SAFE IMPLEMENTATIONS ---
async def fetch_user_profile_safe(user_id: int) -> dict:
    """
    SAFE: Uses async httpx client. Yields control to the event loop
    during the I/O wait, allowing other coroutines to run.
    """
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.get(f"https://api.example.com/users/{user_id}")
        response.raise_for_status()
        return response.json()


async def process_report_safe() -> dict:
    """
    SAFE: asyncio.sleep() yields control to the event loop.
    """
    await asyncio.sleep(2)
    return {"status": "done"}


# NOT APPLICABLE case: sync CLI script — blocking I/O is fine here
def cli_export_report(output_path: str) -> None:
    """
    NOT APPLICABLE: This is a CLI script, not a server request handler.
    Blocking I/O is acceptable in this context.
    PERF01 should not be flagged here.
    """
    import urllib.request
    data = urllib.request.urlopen("https://api.example.com/export").read()
    with open(output_path, "wb") as f:
        f.write(data)

