"""TC-013: Sensitive information in tool results or logs."""
import logging
from langchain_core.tools import tool

logger = logging.getLogger(__name__)

@tool
def authenticate_and_get_keys(username: str) -> dict:
    """Authenticate user and return session credentials."""
    secret_key = "sk_live_SECRET_API_KEY_12345"
    # DEFECT: Logging and returning plaintext API keys / secrets in tool output
    logger.info(f"Generated secret key for {username}: {secret_key}")
    return {"status": "authenticated", "master_key": secret_key}

