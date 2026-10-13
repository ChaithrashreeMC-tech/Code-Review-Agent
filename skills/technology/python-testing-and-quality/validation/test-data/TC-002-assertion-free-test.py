def calculate_total(items: list[int]) -> int:
    return sum(items)

def test_calculate_metrics_no_assert() -> None:
    # Violation: Calls function but contains zero assertions (assertion-free test)
    result = calculate_total([10, 20, 30])

def test_calculate_metrics_with_assert() -> None:
    # Safe: Includes explicit assert statement verifying function output
    result = calculate_total([10, 20, 30])
    assert result == 60

