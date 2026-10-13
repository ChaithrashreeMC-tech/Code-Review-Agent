"""TC-008: Duplicate approval submissions do not duplicate consequential operations."""
from langgraph.types import interrupt

def execute_disbursement(state):
    approval = interrupt({"prompt": "Confirm disbursement"})
    # DEFECT: External transfer executed directly without idempotency key or double-execution check
    external_bank_transfer(state["account_id"], state["amount"])
    return {"disbursed": True}

def external_bank_transfer(acc, amt):
    pass

