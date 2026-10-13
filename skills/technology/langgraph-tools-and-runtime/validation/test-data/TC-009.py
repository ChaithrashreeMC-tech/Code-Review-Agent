"""TC-009: Retryable and non-retryable errors."""
import requests
from langchain_core.tools import tool

@tool
def call_external_payment_gateway(payload: dict) -> dict:
    """Send transaction to payment gateway."""
    # DEFECT: Blindly treating HTTP 400 (Bad Request / invalid card) as retryable transient failure
    response = requests.post("https://api.payment.example/v1/charge", json=payload)
    if response.status_code == 400:
        raise ConnectionResetError("Retryable client bad request error")
    return response.json()

