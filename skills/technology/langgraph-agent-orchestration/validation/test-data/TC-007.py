# agents/tools/account_tools.py
from langchain_core.tools import tool
from infrastructure.database import get_db_session  # Tool Handler Delegation violation

@tool
def query_account_balance(user_id: str) -> dict:
    with get_db_session() as session:
        result = session.query("SELECT * FROM accounts WHERE user_id = :uid", {"uid": user_id})
        return {"balance": result}
