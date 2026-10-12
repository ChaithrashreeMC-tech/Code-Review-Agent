# TC-007: Error Handling Clarity (MAINT07)
# Demonstrates swallowed exceptions, naked returns, and proper contextual error propagation

import logging
from typing import Optional

logger = logging.getLogger(__name__)

class AccountNotFoundError(Exception): pass
class PaymentProcessingError(Exception): pass


# --- VIOLATION ---
def execute_transfer_violation(source_id: str, dest_id: str, amount: float) -> Optional[str]:
    """
    VIOLATION:
    1. Catches generic Exception with bare except/pass concealing failure
    2. Swallows database connection errors, returning None silently
    3. Hides transaction aborts so the caller cannot tell success from catastrophic failure
    """
    try:
        if amount <= 0:
            raise ValueError("Amount must be positive")
        # Simulate payment backend network failure
        raise ConnectionResetError("Remote bank connection lost during debit")
    except Exception:
        # VIOLATION: completely swallowed error, zero logging or diagnostic context
        pass
    return None


# --- SAFE IMPLEMENTATION ---
def execute_transfer_safe(source_id: str, dest_id: str, amount: float) -> str:
    """
    SAFE:
    - Validates inputs explicitly
    - Catches specific network exceptions
    - Chains the original exception using 'from err' to preserve stack trace
    - Logs diagnostic context
    """
    if amount <= 0:
        raise ValueError(f"Invalid transfer amount: {amount}")

    try:
        # Simulate payment backend call
        raise ConnectionResetError("Remote bank connection lost during debit")
    except ConnectionResetError as err:
        logger.error("Payment gateway unreachable during transfer between %s and %s: %s", source_id, dest_id, err)
        raise PaymentProcessingError(f"Transfer from {source_id} failed due to gateway outage") from err

