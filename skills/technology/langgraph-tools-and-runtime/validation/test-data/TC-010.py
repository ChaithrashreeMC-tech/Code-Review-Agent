"""TC-010: Bounded retries and timeout behavior."""
import time
from langchain_core.tools import tool

@tool
def fetch_inventory_status(sku: str) -> dict:
    """Fetch real-time warehouse inventory."""
    # DEFECT: Unbounded infinite while-True retry loop without timeout or maximum attempt count
    while True:
        try:
            return inventory_client.get_sku(sku)
        except Exception:
            time.sleep(1)

