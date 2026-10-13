"""TC-005: Missing or invalid runtime configuration."""
from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig

@tool
def fetch_user_profile(user_id: str, config: RunnableConfig) -> dict:
    """Fetch sensitive profile details."""
    # DEFECT: Accessing nested config without validation raises KeyError if runtime config is omitted
    api_token = config["configurable"]["api_token"]
    return {"user_id": user_id, "token": api_token}

