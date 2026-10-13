"""TC-012: Parallel tool-call behavior where supported."""
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode
from langchain_core.messages import AIMessage, ToolMessage

@tool
def fetch_stock_price(symbol: str) -> float:
    """Fetch current stock quote."""
    return 150.0

@tool
def fetch_company_news(symbol: str) -> list[str]:
    """Fetch recent news articles."""
    return [f"News for {symbol}"]

# ToolNode properly executes parallel calls and returns matching ToolMessages
tool_node = ToolNode([fetch_stock_price, fetch_company_news])
ai_msg = AIMessage(
    content="",
    tool_calls=[
        {"name": "fetch_stock_price", "args": {"symbol": "AAPL"}, "id": "call_1"},
        {"name": "fetch_company_news", "args": {"symbol": "AAPL"}, "id": "call_2"}
    ]
)

