# TC-006: Incorrect backend business behavior
# Spec: specs/tax/business-spec.md Section 5.1
# Rule: Tax exemption status must be validated against customer.is_tax_exempt flag before applying 8.25% state tax.

def calculate_invoice_tax_violation(amount: float, is_tax_exempt: bool) -> float:
    """VIOLATION (BIZ01): Unconditionally applies state tax regardless of tax exemption status."""
    return round(amount * 0.0825, 2)


def calculate_invoice_tax_safe(amount: float, is_tax_exempt: bool) -> float:
    """SAFE: Correctly honors tax exemption flag per specification."""
    if is_tax_exempt:
        return 0.0
    return round(amount * 0.0825, 2)

