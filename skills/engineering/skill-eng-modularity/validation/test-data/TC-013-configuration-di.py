# TC-013: Configuration and Dependency Injection

import os

# VIOLATION: Reading environment variables directly inside deep domain business logic
def calculate_shipping_cost_violation(weight: float):
    # Direct env read inside deep domain function
    api_key = os.environ.get("SHIPPING_API_KEY", "default_secret")
    max_weight = float(os.environ.get("MAX_SHIP_WEIGHT", "100.0"))
    
    if weight > max_weight:
        raise ValueError("Exceeds max allowed weight")
    return weight * 2.5


# SAFE: Environment settings passed via strongly-typed configuration object
class ShippingConfig:
    def __init__(self, api_key: str, max_weight: float):
        self.api_key = api_key
        self.max_weight = max_weight

def calculate_shipping_cost_safe(weight: float, config: ShippingConfig):
    if weight > config.max_weight:
        raise ValueError("Exceeds max allowed weight")
    return weight * 2.5

