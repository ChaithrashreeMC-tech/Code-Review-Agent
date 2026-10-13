"""TC-006: Missing required dependencies."""
from langchain_core.tools import tool

@tool
def process_order(order_id: str) -> dict:
    """Process customer order through application service."""
    # DEFECT: Missing required dependency injection; global order_service is undefined/None
    return global_uninitialized_order_service.submit(order_id)

