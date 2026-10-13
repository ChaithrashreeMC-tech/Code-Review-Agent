# Tool Security & Testing

This reference provides guidance on security boundaries, untrusted output handling, prompt injection defense, least privilege, and deterministic testing for LangGraph tools.

---

## 1. Tool Boundary Security & Defense-in-Depth

### A. Treat Model Arguments as Untrusted Input
- Model-generated arguments must undergo strict validation before passing to application services.
- Never construct raw SQL queries, shell commands, or file system paths using model-generated strings without strict parameterized interfaces or allowlists.

### B. Defense Against Prompt Injection in Tool Outputs
Tool outputs (e.g. web search results, scraped HTML, customer emails, uploaded documents) may contain adversarial prompt injections attempting to hijack agent behavior.
- **Isolate Content**: Tag external tool output as raw data:
  ```python
  return f"<tool_output source='web_search'>\n{sanitized_content}\n</tool_output>"
  ```
- **Never Execute Instructions in Tool Results**: System prompts must instruct models to treat tool outputs as passive data, never as system instructions.

### C. Sensitive Data & Log Masking
- Mask credentials, PII (SSN, credit card numbers), and internal exception stack traces before returning them in `ToolMessage` content or writing to application logs.

```python
# Bad: Leaking sensitive internal stack trace to model and logs
return ToolMessage(content=traceback.format_exc(), tool_call_id=call_id)

# Good: Sanitized error response
return ToolMessage(content="Failed to retrieve record: Database query error.", tool_call_id=call_id)
```

---

## 2. Least Privilege & Consequential Action Boundaries

- **Least Privilege**: Only bind the minimum tools required for the specific agent role (e.g. a Read-Only Search Agent should not have `delete_record` bound).
- **Consequential Actions**: For irreversible actions (funds transfer, data deletion, external email sending), require human approval (via `interrupt` in LangGraph) or verified MFA tokens.
- **False-Positive Guard**: Read-only tools or idempotent lookups do NOT require human approval gates.

---

## 3. Deterministic Testing Patterns

### A. Testing Tool Execution in Isolation with Mocks
```python
# tests/test_tools.py
from unittest.mock import AsyncMock, patch
from my_agent.tools import make_billing_tools

async def test_cancel_subscription_tool():
    mock_service = AsyncMock()
    mock_service.cancel.return_value = AsyncMock(status="cancelled")
    
    tools = make_billing_tools(mock_service)
    cancel_tool = tools[0]
    
    config = {"configurable": {"user_id": "usr_123"}}
    result = await cancel_tool.ainvoke({"subscription_id": "sub_999", "reason": "too expensive"}, config=config)
    
    assert "cancelled" in result
    mock_service.cancel.assert_awaited_once_with(user_id="usr_123", sub_id="sub_999", reason="too expensive")
```

### B. Testing ToolNode & Tool Message Matching
```python
# tests/test_tool_node.py
from langgraph.prebuilt import ToolNode
from langchain_core.messages import AIMessage, ToolMessage

async def test_tool_node_matches_call_id():
    tool_node = ToolNode([fetch_invoice])
    input_message = AIMessage(
        content="",
        tool_calls=[{"name": "fetch_invoice", "args": {"invoice_id": "INV-1"}, "id": "call_abc"}]
    )
    
    output = await tool_node.ainvoke({"messages": [input_message]})
    messages = output["messages"]
    
    assert len(messages) == 1
    assert isinstance(messages[0], ToolMessage)
    assert messages[0].tool_call_id == "call_abc"
```

