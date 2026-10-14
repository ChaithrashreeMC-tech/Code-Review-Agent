# LangGraph Tools & Runtime: Architecture & Patterns

This reference document details tool schema definition, model-tool binding, ToolNode execution, runtime context injection, error handling, and security controls in LangGraph applications.

---

## 1. Tool Definition and Model Binding

Define tools using typed schemas and explicit docstrings:

```python
from langchain_core.tools import tool
from pydantic import BaseModel, Field

class CalculateTaxInput(BaseModel):
    country_code: str = Field(description="ISO two-letter country code (e.g. US, DE)")
    amount: float = Field(description="Net transaction amount in USD", gt=0.0)

@tool(args_schema=CalculateTaxInput)
def calculate_tax(country_code: str, amount: float) -> dict:
    """Calculate the estimated sales or value-added tax for a transaction."""
    rate = 0.19 if country_code == "DE" else 0.08
    return {"country": country_code, "tax": round(amount * rate, 2)}
```

### Model Binding and ToolNode Wiring
```python
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph import StateGraph, START, END

tools = [calculate_tax]
llm_with_tools = chat_model.bind_tools(tools)

builder = StateGraph(AgentState)
builder.add_node("agent", agent_node)
builder.add_node("tools", ToolNode(tools))

builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", tools_condition)
builder.add_edge("tools", "agent")
```

---

## 2. Injected Runtime Context & Dependencies

Extract runtime context securely from `RunnableConfig`:

```python
from langchain_core.runnables import RunnableConfig

@tool
def fetch_user_orders(config: RunnableConfig) -> dict:
    """Fetch orders for the currently authenticated tenant session."""
    configurable = config.get("configurable", {})
    tenant_id = configurable.get("tenant_id")
    if not tenant_id:
        return {"error": "Unauthorized: Missing tenant context"}
        
    order_service = configurable.get("order_service")
    orders = order_service.get_orders_for_tenant(tenant_id)
    return {"orders": orders}
```

---

## 3. Tool Error Handling & Bounded Retries

Classify exceptions and handle errors gracefully:

```python
import httpx

@tool
def call_external_gateway(endpoint: str, payload: dict) -> dict:
    """Call external third-party API gateway with bounded retry policy."""
    retries = 3
    for attempt in range(retries):
        try:
            response = httpx.post(endpoint, json=payload, timeout=5.0)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if 400 <= e.response.status_code < 500:
                # Permanent client error; do not retry
                return {"error": f"Client error: {e.response.text}", "retryable": False}
        except httpx.RequestError as e:
            if attempt == retries - 1:
                return {"error": f"Network failure: {str(e)}", "retryable": True}
```

---

## 4. Output Sanitization & Security

Always sanitize tool outputs and mask sensitive credentials:

```python
import re

def sanitize_tool_output(raw_text: str) -> str:
    """Mask credentials and strip malicious script tags."""
    # Mask API keys
    masked = re.sub(r'sk-[a-zA-Z0-9]{20,}', '[REDACTED_API_KEY]', raw_text)
    # Strip HTML script injection
    sanitized = re.sub(r'<script.*?>.*?</script>', '', masked, flags=re.DOTALL)
    return sanitized
```

