"""TC-003: Malformed or missing tool arguments."""
from langchain_core.tools import tool

@tool
def calculate_tax(amount: float, country_code: str) -> float:
    """Calculate tax for transaction."""
    # DEFECT: Direct untyped invocation without validation causes unhandled TypeError on missing country_code
    return amount * 0.2 if country_code == "US" else amount * 0.1

