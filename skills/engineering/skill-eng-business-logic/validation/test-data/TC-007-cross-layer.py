# TC-007: Defect requiring tracing across multiple layers
# Spec: specs/discounts/business-spec.md Section 2.3
# Rule: Promo code VIP100 gives $100 off on minimum purchase of $500.

# API Layer sends promoCode and subtotal
# Domain Service Layer applies discount

def apply_promo_code_service_violation(subtotal: float, promo_code: str) -> float:
    """VIOLATION (BIZ09 / BIZ02): Service deducts $100 without validating subtotal >= 500 minimum purchase requirement."""
    if promo_code == "VIP100":
        return max(0.0, subtotal - 100.0)
    return subtotal


def apply_promo_code_service_safe(subtotal: float, promo_code: str) -> float:
    """SAFE: Verifies minimum subtotal qualification requirement across layers."""
    if promo_code == "VIP100" and subtotal >= 500.0:
        return max(0.0, subtotal - 100.0)
    return subtotal

