"""TC-015: Sensitive checkpoint and audit data are protected."""
from langgraph.types import interrupt

def payment_review_node(state):
    # DEFECT: Raw unmasked credit card CVV and customer SSN sent into interrupt payload and saved into checkpoint state
    decision = interrupt({
        "prompt": "Approve transaction",
        "ssn": state.get("customer_ssn"),
        "cvv": state.get("card_cvv")
    })
    return {"decision": decision}

