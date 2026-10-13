"""TC-016: Retry or recovery cannot silently repeat an external side effect."""
import requests
from langgraph.types import interrupt

def charge_and_confirm_node(state):
    # DEFECT: Non-idempotent external HTTP POST executed before interrupt inside the same node without replay protection
    requests.post("https://payment.gateway/api/v1/charge", json={"amount": state["amount"]})
    user_confirm = interrupt({"prompt": "Acknowledge payment"})
    return {"confirmed": True}

