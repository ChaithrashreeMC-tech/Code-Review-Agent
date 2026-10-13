"""TC-008: Cross-tenant access attempts in a multi-tenant application."""
from langchain_core.tools import tool

@tool
def get_tenant_billing_records(tenant_id: str) -> list[dict]:
    """Retrieve billing ledger for given tenant."""
    # DEFECT: Trusting model-provided tenant_id parameter rather than extracting from validated runtime context
    return billing_db.query_by_tenant(tenant_id)

