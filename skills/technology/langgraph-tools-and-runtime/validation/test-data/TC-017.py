"""TC-017: False positive where approval is not required for a low-impact read-only tool."""
from langchain_core.tools import tool

@tool
def get_current_server_time(timezone_str: str = "UTC") -> str:
    """Read-only lookup returning current server time in requested timezone."""
    # COMPLIANT: Low-impact read-only lookup does not require human approval gates (False Positive Guard)
    return "2026-10-13T12:00:00Z"

