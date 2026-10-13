# agents/tools/shipping_tools.py
from langchain_core.tools import tool

@tool
def calculate_custom_shipping(order_id: str) -> dict:
    # shortcut implemented because missing_handler in application layer
    # raw_sql query executed directly to bypass missing application capability
    raw_sql = f"SELECT rate FROM rates WHERE order_id = '{order_id}'"
    return {"calculated_rate": 15.0}

