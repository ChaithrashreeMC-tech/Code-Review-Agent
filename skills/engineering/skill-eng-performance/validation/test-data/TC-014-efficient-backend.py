# TC-014: Efficient Backend — Multi-Rule Safe Implementation (PERF04 + PERF05 + PERF07)
# Expected: NO findings — this is a deliberately well-implemented example
# This case verifies the reviewer does not produce false positives on correct code.
# Technology: Python / FastAPI + Redis + asyncio

"""
Demonstrates a correctly implemented backend endpoint covering:
  - PERF04: Proper caching with TTL and invalidation
  - PERF05: Timeout and retry with backoff and cap
  - PERF07: Bounded concurrent fan-out with semaphore

The reviewer must NOT flag any of these patterns.
"""

import asyncio
import json
from typing import Optional

import httpx
import redis.asyncio as aioredis
from fastapi import FastAPI, HTTPException
from tenacity import retry, stop_after_attempt, wait_exponential

app = FastAPI()
redis_client: aioredis.Redis = None  # initialized at startup

INVENTORY_SERVICES = [
    "https://warehouse-a.example.com",
    "https://warehouse-b.example.com",
    "https://warehouse-c.example.com",
]


@app.on_event("startup")
async def startup():
    global redis_client
    redis_client = aioredis.from_url("redis://localhost:6379", decode_responses=True)


# ============================================================
# PERF04 SAFE: Cache with TTL and invalidation on write
# ============================================================

PRODUCT_CACHE_TTL = 300  # 5 minutes


async def get_product_from_cache(product_id: int) -> Optional[dict]:
    """Returns cached product or None on cache miss."""
    cached = await redis_client.get(f"product:{product_id}")
    return json.loads(cached) if cached else None


async def set_product_in_cache(product_id: int, product: dict) -> None:
    """Cache product with TTL."""
    await redis_client.set(
        f"product:{product_id}",
        json.dumps(product),
        ex=PRODUCT_CACHE_TTL,
    )


async def invalidate_product_cache(product_id: int) -> None:
    """Remove stale cache entry on write."""
    await redis_client.delete(f"product:{product_id}")


# ============================================================
# PERF05 SAFE: Timeout + retry with backoff and max attempts
# ============================================================

@retry(
    wait=wait_exponential(multiplier=1, min=1, max=10),
    stop=stop_after_attempt(3),  # cap: no infinite retries
    reraise=True,
)
async def fetch_from_service(client: httpx.AsyncClient, url: str) -> dict:
    """Fetch from a service with timeout and bounded retry."""
    response = await client.get(url, timeout=5.0)  # explicit timeout
    response.raise_for_status()
    return response.json()


# ============================================================
# PERF07 SAFE: Bounded concurrent fan-out with semaphore
# ============================================================

MAX_CONCURRENCY = 5  # no more than 5 simultaneous warehouse requests


async def fetch_inventory_across_warehouses(product_id: int) -> list[dict]:
    """
    Fan-out to multiple warehouses with a semaphore cap.
    Operations are independent — safe to parallelize.
    Semaphore prevents connection pool exhaustion.
    """
    semaphore = asyncio.Semaphore(MAX_CONCURRENCY)

    async def fetch_one(base_url: str) -> dict:
        async with semaphore:
            async with httpx.AsyncClient() as client:
                return await fetch_from_service(
                    client, f"{base_url}/inventory/{product_id}"
                )

    results = await asyncio.gather(
        *[fetch_one(url) for url in INVENTORY_SERVICES],
        return_exceptions=True,
    )
    # Filter out exceptions from individual warehouse failures
    return [r for r in results if isinstance(r, dict)]


# ============================================================
# Endpoint wiring all three patterns together
# ============================================================

@app.get("/products/{product_id}/stock")
async def get_product_stock(product_id: int):
    """
    1. Check cache (PERF04)
    2. Fan-out to warehouses with semaphore (PERF07) and timeout/retry (PERF05)
    3. Cache result
    """
    # Cache check
    cached = await get_product_from_cache(product_id)
    if cached:
        return cached

    # Parallel fetch with bounds
    inventory_data = await fetch_inventory_across_warehouses(product_id)
    if not inventory_data:
        raise HTTPException(status_code=503, detail="All warehouses unavailable")

    result = {
        "product_id": product_id,
        "warehouses": inventory_data,
        "total_stock": sum(w.get("stock", 0) for w in inventory_data),
    }

    # Cache with TTL
    await set_product_in_cache(product_id, result)
    return result


@app.put("/products/{product_id}")
async def update_product(product_id: int, data: dict):
    """Invalidates cache on write to prevent stale data."""
    # ... update DB ...
    await invalidate_product_cache(product_id)  # PERF04: proper invalidation
    return {"status": "updated"}

