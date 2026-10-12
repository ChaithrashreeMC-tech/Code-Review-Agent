# TC-009: State Management and Mutability Boundaries

# VIOLATION: Function mutating caller's input dictionary parameter unexpectedly
def apply_discount_violation(cart_data, discount_rate):
    # Unexpectedly mutates caller's dict in-place
    for item in cart_data["items"]:
        item["price"] = item["price"] * (1 - discount_rate)
    cart_data["discount_applied"] = True
    return cart_data


# SAFE: Pure transformation returning new data structure without mutating input
def apply_discount_safe(cart_data: dict, discount_rate: float) -> dict:
    new_items = [
        {**item, "price": item["price"] * (1 - discount_rate)}
        for item in cart_data["items"]
    ]
    return {
        **cart_data,
        "items": new_items,
        "discount_applied": True
    }

