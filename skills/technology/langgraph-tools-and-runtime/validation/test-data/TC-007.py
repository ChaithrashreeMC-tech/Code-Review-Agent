"""TC-007: Unauthorized tool access."""
from langchain_core.tools import tool

@tool
def delete_database_records(table_name: str, filter_criteria: str) -> str:
    """Permanently delete database records."""
    # DEFECT: High-impact destructive tool callable without any role or permission authorization check
    raw_db_executor.execute(f"DELETE FROM {table_name} WHERE {filter_criteria}")
    return "Records deleted successfully"

