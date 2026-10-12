# TC-007: Redundant Calls and Computation (PERF08 violation)
# Expected: PERF08 finding, severity=medium, confidence=high
# Technology: Python

import re
import hashlib
from functools import lru_cache
import httpx


# --- VIOLATION 1: Regex compiled on every call ---
def extract_emails_from_text_slow(text: str) -> list[str]:
    """
    VIOLATION: re.compile() is called on every invocation of this function.
    In a request handler called at 500 RPS, this recompiles the regex
    500 times per second unnecessarily.
    """
    # VIOLATION: should be module-level constant
    EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
    return EMAIL_PATTERN.findall(text)


# --- VIOLATION 2: Same external API called twice per request ---
async def get_user_dashboard(user_id: int) -> dict:
    """
    VIOLATION: Calls the user profile API twice within a single request.
    The first call's result could be reused for the second use.
    """
    async with httpx.AsyncClient(timeout=5.0) as client:
        # Call 1: to get the user's name
        profile_1 = await client.get(f"https://api.example.com/users/{user_id}")
        user_name = profile_1.json()["name"]

        # ... some processing ...

        # VIOLATION: identical call to same endpoint
        profile_2 = await client.get(f"https://api.example.com/users/{user_id}")
        user_avatar = profile_2.json()["avatar_url"]  # could use profile_1

    return {"name": user_name, "avatar": user_avatar}


# --- VIOLATION 3: Config reloaded from disk on every request ---
def get_feature_flags() -> dict:
    """
    VIOLATION: Reads configuration from disk on every call.
    At 1,000 RPS this creates 1,000 disk reads per second unnecessarily.
    """
    import json
    with open("/etc/app/feature-flags.json") as f:  # VIOLATION: per-call disk I/O
        return json.load(f)


# --- SAFE IMPLEMENTATIONS ---

# SAFE 1: Module-level compiled regex
_EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")

def extract_emails_from_text_fast(text: str) -> list[str]:
    """SAFE: Regex compiled once at module load time."""
    return _EMAIL_PATTERN.findall(text)


async def get_user_dashboard_safe(user_id: int) -> dict:
    """SAFE: Profile fetched once; result reused."""
    async with httpx.AsyncClient(timeout=5.0) as client:
        profile = await client.get(f"https://api.example.com/users/{user_id}")
        profile_data = profile.json()
    return {
        "name": profile_data["name"],
        "avatar": profile_data["avatar_url"],  # reuses same response
    }


# SAFE 2: Cached at startup via lru_cache
@lru_cache(maxsize=1)
def get_feature_flags_cached() -> dict:
    """
    SAFE: Loaded once and cached indefinitely (or until process restart).
    For mutable config, combine with a TTL-based refresh mechanism.
    """
    import json
    with open("/etc/app/feature-flags.json") as f:
        return json.load(f)

