# TC-006: Concurrency and Parallelism (PERF07 violations)
# Expected: PERF07 finding for sequential I/O; separate finding for unbounded fan-out
# Technology: Python / asyncio

import asyncio
from typing import Any
import httpx

ENDPOINTS = [
    "https://api.example.com/inventory",
    "https://api.example.com/pricing",
    "https://api.example.com/reviews",
]


# --- VIOLATION 1: Sequential awaits on independent I/O ---
async def fetch_product_data_sequential(product_id: str) -> dict:
    """
    VIOLATION: Three independent HTTP calls executed sequentially.
    Total latency ≈ sum of all three latencies.
    These operations are independent and could run in parallel.
    """
    async with httpx.AsyncClient(timeout=5.0) as client:
        inventory = await client.get(f"{ENDPOINTS[0]}/{product_id}")  # ~200ms
        pricing = await client.get(f"{ENDPOINTS[1]}/{product_id}")    # ~150ms
        reviews = await client.get(f"{ENDPOINTS[2]}/{product_id}")    # ~300ms
        # VIOLATION: Total ≈ 650ms; parallel would be ~300ms
    return {
        "inventory": inventory.json(),
        "pricing": pricing.json(),
        "reviews": reviews.json(),
    }


# --- VIOLATION 2: Unbounded fan-out ---
async def fetch_all_users_parallel_unbounded(user_ids: list[int]) -> list[dict]:
    """
    VIOLATION: Launches one task per user_id with no concurrency cap.
    With 10,000 user_ids this will exhaust the HTTP connection pool,
    OS file descriptors, and potentially the event loop.
    """
    async def fetch_one(uid: int) -> dict:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(f"https://api.example.com/users/{uid}")
            return r.json()

    # VIOLATION: no semaphore bounding concurrency
    return await asyncio.gather(*[fetch_one(uid) for uid in user_ids])


# --- SAFE 1: Parallel with asyncio.gather ---
async def fetch_product_data_parallel(product_id: str) -> dict:
    """
    SAFE: All three independent HTTP calls run concurrently.
    Total latency ≈ max(200ms, 150ms, 300ms) = ~300ms.
    """
    async with httpx.AsyncClient(timeout=5.0) as client:
        inventory_t, pricing_t, reviews_t = await asyncio.gather(
            client.get(f"{ENDPOINTS[0]}/{product_id}"),
            client.get(f"{ENDPOINTS[1]}/{product_id}"),
            client.get(f"{ENDPOINTS[2]}/{product_id}"),
        )
    return {
        "inventory": inventory_t.json(),
        "pricing": pricing_t.json(),
        "reviews": reviews_t.json(),
    }


# --- SAFE 2: Bounded fan-out with semaphore ---
async def fetch_all_users_parallel_bounded(user_ids: list[int], max_concurrency: int = 20) -> list[dict]:
    """
    SAFE: Uses asyncio.Semaphore to cap concurrent connections at 20.
    Prevents connection pool exhaustion regardless of user_ids length.
    """
    semaphore = asyncio.Semaphore(max_concurrency)

    async def fetch_one(uid: int) -> dict:
        async with semaphore:
            async with httpx.AsyncClient(timeout=5.0) as client:
                r = await client.get(f"https://api.example.com/users/{uid}")
                return r.json()

    return await asyncio.gather(*[fetch_one(uid) for uid in user_ids])


# NOT APPLICABLE: Operations have data dependency — must be sequential
async def create_and_notify_user(email: str, name: str) -> dict:
    """
    NOT APPLICABLE: create_user must complete before notify_user can use
    the new user's ID. Sequential execution is required here.
    PERF07 must not be flagged for this pattern.
    """
    async with httpx.AsyncClient(timeout=5.0) as client:
        create_resp = await client.post(
            "https://api.example.com/users",
            json={"email": email, "name": name},
        )
        user_id = create_resp.json()["id"]  # needed by next call

        notify_resp = await client.post(
            f"https://api.example.com/users/{user_id}/welcome-email"
        )
    return {"user_id": user_id, "notified": notify_resp.status_code == 200}

