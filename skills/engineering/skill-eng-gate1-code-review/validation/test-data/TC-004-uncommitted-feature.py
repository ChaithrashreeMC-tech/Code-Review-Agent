# Uncommitted / Untracked feature module
def calculate_shipping(weight_kg: float, distance_km: float) -> float:
    """Calculates shipping fees based on weight and distance tiers."""
    base_fee = 5.0
    if weight_kg > 10.0:
        base_fee += (weight_kg - 10.0) * 1.5
    if distance_km > 50.0:
        base_fee += (distance_km - 50.0) * 0.1
    return round(base_fee, 2)

