# TC-011: Potential issue already handled elsewhere in implementation -> Safe
# TC-012: Security / Maintainability concern not misclassified as business logic -> Safe
# TC-013: Missing test without evidence of business defect -> Safe
# TC-014: Design preference difference vs correct business implementation -> Safe

# Context for TC-011: Controller does not check for None, but middleware/pydantic validator guarantees non-null
def process_order_request_safe(order_id: str, validated_payload: dict) -> dict:
    """SAFE: Null validation already enforced upstream by SchemaValidator middleware."""
    return {"order_id": order_id, "amount": validated_payload["amount"]}


# Context for TC-012: SQL parameterization (Security) or duplicate helper (Maintainability)
def query_customer_orders_safe(customer_id: str, db_connection) -> list:
    """SAFE (Business Logic): Correct domain query logic. (SQL parameterization is evaluated under Security)."""
    return db_connection.execute("SELECT * FROM orders WHERE customer_id = ?", (customer_id,)).fetchall()


# Context for TC-013: Feature implementation matches spec; unit test not included in PR
def calculate_loyalty_points_safe(spent_amount: float) -> int:
    """SAFE: Correct business logic (1 point per $10 spent). Lack of unit test is not a business logic violation."""
    return int(spent_amount // 10)


# Context for TC-014: Written as procedural loop rather than functional map/reduce per reviewer preference
def aggregate_tier_totals_safe(order_amounts: list[float]) -> float:
    """SAFE: Correctly sums qualifying amounts. Implementation style matches spec despite procedural preference."""
    total = 0.0
    for amt in order_amounts:
        if amt > 0:
            total += amt
    return total

