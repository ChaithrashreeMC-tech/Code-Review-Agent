"""TC-011: Duplicate side effects after a retry."""
from langchain_core.tools import tool

@tool
def submit_wire_transfer(recipient_iban: str, amount_usd: float) -> str:
    """Execute non-idempotent international wire transfer."""
    # DEFECT: Retrying non-idempotent fund transfer without idempotency key causes duplicate debit
    tx = bank_wire_api.transfer(iban=recipient_iban, amount=amount_usd)
    return f"Transfer successful: {tx.id}"

