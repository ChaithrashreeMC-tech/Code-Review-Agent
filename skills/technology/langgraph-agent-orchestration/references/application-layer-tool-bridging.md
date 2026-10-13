# Application-Layer Tool Bridging & Handler Delegation

This reference documents how LangGraph tools act as thin adapters to the Application layer, ensuring proper handler delegation, preventing business logic duplication, and identifying requirements gaps.

---

## 1. The Core Principle: Tools as Thin Adapters

A tool in `agents/tools/` is strictly a **driving adapter** that bridges the agent reasoning runtime to the backend's existing Application layer.

```text
+-----------------------+
|  LangGraph Agent Node |
+-----------------------+
           |
           v (calls @tool)
+-----------------------+
|  agents/tools/        |  <-- Thin Adapter: validates input, calls handler, returns dict
+-----------------------+
           |
           v (Tool Handler Delegation: imports Application Layer ONLY)
+---------------------------------------+
|  application/features/[feature]/      |  <-- CQRS Command / Query Handlers
+---------------------------------------+
           |
           v
+---------------------------------------+
|  domain/ & infrastructure/            |  <-- Business Entities, Repositories, Database
+---------------------------------------+
```

### Tool Handler Delegation Mandate
> `agents/tools/` may import from `application/` ONLY — to execute existing commands and queries. Tools never import `infrastructure/` or `domain/` directly, and never open raw database sessions or execute direct SQL queries.

---

## 2. Valid vs. Invalid Tool Implementation Patterns

### ✅ Correct Pattern: Delegating to Application Handler
```python
# agents/tools/portfolio_tools.py
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from application.features.portfolio.queries.get_user_balance import (
    GetUserBalanceQuery,
    GetUserBalanceHandler
)

class GetBalanceInput(BaseModel):
    user_id: str = Field(description="Unique ID of the account holder")

@tool("get_user_balance", args_schema=GetBalanceInput)
async def get_user_balance(user_id: str) -> dict:
    """Retrieve the verified account balance for a given user."""
    # Resolve handler via DI or factory matching the API layer
    handler: GetUserBalanceHandler = resolve_handler(GetUserBalanceHandler)
    result = await handler.handle(GetUserBalanceQuery(user_id=user_id))
    return result.model_dump()
```

### ❌ Violation Pattern 1: Direct Database Access (Infrastructure Leak)
```python
# VIOLATION: Tool opening DB session directly and querying infrastructure
from langchain_core.tools import tool
from infrastructure.database import get_db_session  # <-- VIOLATION: imports infrastructure
from domain.models.account import UserAccount      # <-- VIOLATION: imports domain directly

@tool
def get_user_balance_bad(user_id: str) -> dict:
    with get_db_session() as session:              # <-- VIOLATION: raw DB session
        account = session.query(UserAccount).filter_by(id=user_id).first()
        return {"balance": account.balance}
```

### ❌ Violation Pattern 2: Duplicating Business Logic in Tools
```python
# VIOLATION: Tool reimplementing business calculation instead of using Application Handler
@tool
def calculate_discount_bad(price: float, user_tier: str) -> float:
    # Business logic belongs in application/ or domain/, not inside agent tools!
    if user_tier == "GOLD":
        return price * 0.80
    return price * 0.95
```

---

## 3. Handling Requirements & Capability Gaps

When an agent feature requires a capability that has **no existing Application-layer handler**:

1. **Do NOT Create Shortcuts**: Never write raw SQL, bypass authentication, or query internal tables directly from `agents/tools/` to "make it work".
2. **Flag Requirements Gap**: Report a clear **Application Capability Gap** to the feature owner or specifier:
   - Identify the missing query or command contract.
   - Specify the required input parameters and return model.
   - Request the creation of the corresponding `application/features/[feature]/` handler.
3. **Use Mock Handler in Development**: While the application handler is being implemented, inject a stub handler contract adhering to the expected Application-layer interface.

---

## 4. Testing Tool Adapters

Tools are tested using unit tests with mocked Application handlers:

```python
# tests/agent_tests/tools/test_portfolio_tools.py
import pytest
from unittest.mock import AsyncMock
from application.features.portfolio.queries.get_user_balance import GetUserBalanceResult
from agents.tools.portfolio_tools import get_user_balance

@pytest.mark.asyncio
async def test_get_user_balance_tool_calls_handler(monkeypatch):
    mock_handler = AsyncMock()
    mock_handler.handle.return_value = GetUserBalanceResult(user_id="U123", balance=450.00)
    monkeypatch.setattr("agents.tools.portfolio_tools.resolve_handler", lambda _: mock_handler)

    result = await get_user_balance.ainvoke({"user_id": "U123"})

    assert result["user_id"] == "U123"
    assert result["balance"] == 450.00
    mock_handler.handle.assert_called_once()
```
