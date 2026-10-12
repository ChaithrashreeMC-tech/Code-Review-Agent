# TC-011: Dead and Obsolete Code (MAINT11)
# Demonstrates unreachable code, unused private methods, and commented-out dead code

from typing import Optional

# --- VIOLATION ---
def calculate_tax_with_dead_code(amount: float, country: str) -> float:
    """
    VIOLATION:
    - Code following unconditional return is 100% unreachable
    - Dead commented-out block of old calculation logic
    - Unused private helper '_legacy_vat_calculator'
    """
    if country == "US":
        return amount * 0.07
    else:
        return amount * 0.20

    # VIOLATION: Unreachable code below
    adjustment = amount * 0.02
    print(f"Applied adjustment {adjustment}")
    return amount + adjustment

# VIOLATION: Large block of dead commented-out code
# def _deprecated_2021_tax_formula(amt):
#     if amt > 1000:
#         return amt * 0.25
#     return amt * 0.15

def _unused_private_helper(x: int) -> int:
    """VIOLATION: Private function that is never called anywhere."""
    return x * 42


# --- SAFE IMPLEMENTATION ---
def calculate_tax_clean(amount: float, country: str) -> float:
    """SAFE: Clean, reachable paths with zero commented-out or dead code."""
    if country == "US":
        return amount * 0.07
    return amount * 0.20

