# TC-011: Domain and Feature Boundaries

# VIOLATION: Deep internal import reaching into private internals of sibling feature
def get_user_internal_discount_violation():
    # Bypassing billing feature's public index facade API
    from billing.internal.private_calc_helpers import _secret_discount_formula
    return _secret_discount_formula(100)


# SAFE: Importing strictly from billing domain's public API facade
def get_user_internal_discount_safe():
    from billing import get_public_discount
    return get_public_discount(100)

