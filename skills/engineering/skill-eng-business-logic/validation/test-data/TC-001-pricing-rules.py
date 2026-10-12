# TC-001: Correct implementation of documented business rule & TC-002: Incorrect calculation
# Spec: specs/pricing/business-spec.md Section 2.1
# Rule: Order discount is 10% if subtotal >= 1000 and customer tier is GOLD. Otherwise discount is 0.

def calculate_discount_correct(subtotal: float, tier: str) -> float:
    """Correct implementation matching spec requirements."""
    if subtotal >= 1000.0 and tier == "GOLD":
        return round(subtotal * 0.10, 2)
    return 0.0


def calculate_discount_incorrect_threshold(subtotal: float, tier: str) -> float:
    """VIOLATION (BIZ02): Applies discount when subtotal >= 500 instead of spec requirement >= 1000."""
    if subtotal >= 500.0 and tier == "GOLD":
        return round(subtotal * 0.10, 2)
    return 0.0

