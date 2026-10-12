# TC-009: Testability and Test Structure (MAINT09)
# Demonstrates unmockable direct system clock calls vs. injected time providers

from datetime import datetime, timezone, timedelta
from typing import Protocol, Callable

# --- VIOLATION ---
class TrialSubscriptionViolation:
    """
    VIOLATION: Calls datetime.now(timezone.utc) directly inside business logic.
    Unit tests cannot verify expiration without mocking the C-level datetime module
    or waiting real time, causing flaky and non-deterministic tests.
    """
    def __init__(self, start_date: datetime):
        self.start_date = start_date

    def is_expired(self) -> bool:
        # VIOLATION: direct call to system clock prevents deterministic unit testing
        current_time = datetime.now(timezone.utc)
        return current_time > (self.start_date + timedelta(days=14))


# --- SAFE IMPLEMENTATION ---
class TimeProvider(Protocol):
    def now_utc(self) -> datetime: ...

class SystemTimeProvider:
    def now_utc(self) -> datetime:
        return datetime.now(timezone.utc)

class TrialSubscriptionSafe:
    """
    SAFE: Injects time provider or accepts clock callable.
    Can be deterministically tested across any historical or future date.
    """
    def __init__(self, start_date: datetime, clock: Callable[[], datetime] = lambda: datetime.now(timezone.utc)):
        self.start_date = start_date
        self._clock = clock

    def is_expired(self) -> bool:
        return self._clock() > (self.start_date + timedelta(days=14))

