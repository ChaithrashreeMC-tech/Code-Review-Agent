def charge_card_node(state: dict) -> dict:
    # Defect: non_idempotent_side_effect with missing_idempotency_key re-executed on failure recovery
    payment_gateway.charge(amount=state["amount"])
    return {"status": "paid"}

