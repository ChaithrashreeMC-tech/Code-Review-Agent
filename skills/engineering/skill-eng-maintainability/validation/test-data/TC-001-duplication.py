# TC-001: Code Duplication (MAINT01)
# Demonstrates copy-pasted business logic and extraction into shared function

# --- VIOLATION ---
def calculate_invoice_total_domestic(subtotal: float, customer_tier: str) -> float:
    """Calculates domestic invoice total with discounts and taxes."""
    # VIOLATION: Duplicated pricing discount and tax logic
    discount = 0.0
    if customer_tier == "GOLD":
        discount = subtotal * 0.15
    elif customer_tier == "SILVER":
        discount = subtotal * 0.08
    elif customer_tier == "BRONZE":
        discount = subtotal * 0.03
    discounted = subtotal - discount
    tax = discounted * 0.0825
    return discounted + tax

def calculate_invoice_total_commercial(subtotal: float, customer_tier: str) -> float:
    """Calculates commercial invoice total with identical discount rates."""
    # VIOLATION: Exact copy-paste of discount logic from calculate_invoice_total_domestic
    discount = 0.0
    if customer_tier == "GOLD":
        discount = subtotal * 0.15
    elif customer_tier == "SILVER":
        discount = subtotal * 0.08
    elif customer_tier == "BRONZE":
        discount = subtotal * 0.03
    discounted = subtotal - discount
    tax = discounted * 0.0825
    return discounted + tax


# --- SAFE IMPLEMENTATION ---
DISCOUNT_RATES = {
    "GOLD": 0.15,
    "SILVER": 0.08,
    "BRONZE": 0.03,
}
DEFAULT_TAX_RATE = 0.0825

def apply_customer_discount(subtotal: float, customer_tier: str) -> float:
    """SAFE: Shared calculation for discount deduction."""
    rate = DISCOUNT_RATES.get(customer_tier, 0.0)
    return subtotal * (1.0 - rate)

def calculate_invoice_total_safe(subtotal: float, customer_tier: str, tax_rate: float = DEFAULT_TAX_RATE) -> float:
    """SAFE: Reusable calculation without duplication."""
    discounted = apply_customer_discount(subtotal, customer_tier)
    return discounted * (1.0 + tax_rate)

