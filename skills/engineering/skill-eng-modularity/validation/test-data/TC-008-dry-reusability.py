# TC-008: Code Reusability and DRY

# VIOLATION: Duplicate complex tax calculation logic copy-pasted across multiple functions
def calculate_invoice_tax_violation(amount, state):
    if state == "CA":
        tax = amount * 0.0725 + (amount * 0.01 if amount > 1000 else 0)
    elif state == "NY":
        tax = amount * 0.08875
    else:
        tax = amount * 0.05
    return amount + tax

def calculate_order_tax_violation(amount, state):
    # Identical copy-pasted tax logic
    if state == "CA":
        tax = amount * 0.0725 + (amount * 0.01 if amount > 1000 else 0)
    elif state == "NY":
        tax = amount * 0.08875
    else:
        tax = amount * 0.05
    return amount + tax


# SAFE: Reusable tax calculator function
def compute_tax(amount: float, state: str) -> float:
    if state == "CA":
        return amount * 0.0725 + (amount * 0.01 if amount > 1000 else 0)
    elif state == "NY":
        return amount * 0.08875
    return amount * 0.05

def calculate_invoice_tax_safe(amount: float, state: str) -> float:
    return amount + compute_tax(amount, state)

def calculate_order_tax_safe(amount: float, state: str) -> float:
    return amount + compute_tax(amount, state)

