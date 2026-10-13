# Clean feature implementation: Pricing calculation service
from decimal import Decimal
from typing import Dict, Any

class PricingCalculator:
    """Calculates order totals with standard tax and validated discounts."""
    
    def __init__(self, base_tax_rate: Decimal = Decimal("0.08")) -> None:
        self.tax_rate = base_tax_rate

    def calculate_total(self, subtotal: Decimal, discount_percent: Decimal = Decimal("0.0")) -> Dict[str, Any]:
        """Returns itemized order summary adhering strictly to domain rules."""
        if subtotal < Decimal("0.0"):
            raise ValueError("Subtotal cannot be negative")
        if not (Decimal("0.0") <= discount_percent <= Decimal("1.0")):
            raise ValueError("Discount must be between 0.0 and 1.0")

        discount_amount = (subtotal * discount_percent).quantize(Decimal("0.01"))
        taxable_amount = subtotal - discount_amount
        tax_amount = (taxable_amount * self.tax_rate).quantize(Decimal("0.01"))
        final_total = taxable_amount + tax_amount

        return {
            "subtotal": subtotal,
            "discount": discount_amount,
            "tax": tax_amount,
            "total": final_total,
        }

