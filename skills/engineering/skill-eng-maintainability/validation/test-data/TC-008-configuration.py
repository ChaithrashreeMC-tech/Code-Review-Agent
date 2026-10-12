# TC-008: Configuration and Magic Values (MAINT08)
# Demonstrates hardcoded magic literals, scattered environment variables vs. centralized settings

import os
from dataclasses import dataclass

# --- VIOLATION ---
def calculate_user_session_expiry_violation(user_role: str) -> int:
    """
    VIOLATION:
    - Scattered magic numbers: 86400, 604800, 3600
    - Directly reading os.environ across business methods with fallback defaults
    - Hardcoded production URL in business calculation
    """
    # VIOLATION: magic values without named constants
    if user_role == "ADMIN":
        base_seconds = 3600
    elif user_role == "SUPPORT":
        base_seconds = 86400
    else:
        base_seconds = 604800

    # VIOLATION: direct environment read in deep business code
    multiplier = float(os.environ.get("SESSION_TIMEOUT_MULTIPLIER", "1.5"))
    return int(base_seconds * multiplier)


# --- SAFE IMPLEMENTATION ---
SECONDS_PER_HOUR = 3600
SECONDS_PER_DAY = 86400
SECONDS_PER_WEEK = 604800

ROLE_SESSION_DURATIONS = {
    "ADMIN": SECONDS_PER_HOUR,
    "SUPPORT": SECONDS_PER_DAY,
    "DEFAULT": SECONDS_PER_WEEK,
}

@dataclass(frozen=True)
class SecuritySettings:
    """SAFE: Centralized, typed configuration."""
    session_timeout_multiplier: float = 1.0

def calculate_user_session_expiry_safe(user_role: str, settings: SecuritySettings) -> int:
    """SAFE: Uses named constants and injected configuration."""
    base_seconds = ROLE_SESSION_DURATIONS.get(user_role, ROLE_SESSION_DURATIONS["DEFAULT"])
    return int(base_seconds * settings.session_timeout_multiplier)

