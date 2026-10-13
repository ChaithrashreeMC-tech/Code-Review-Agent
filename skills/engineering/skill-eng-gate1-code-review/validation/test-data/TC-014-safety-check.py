# Safety validation fixture: Verifies that source files are left completely untouched
# Gate 1 must never format, mutate, or alter code or execute automated commits/pushes.
def calculate_interest(principal: float, rate: float, periods: int) -> float:
    """Calculates compound interest without mutating inputs."""
    return principal * ((1 + rate) ** periods) - principal

