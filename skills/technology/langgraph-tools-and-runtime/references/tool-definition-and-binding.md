# Tool Definition & Model Binding

This reference provides guidance on declaring, typing, describing, and binding tools in LangGraph and LangChain Python applications.

---

## 1. Tool Declaration Approaches

LangChain and LangGraph support multiple ways to define tools:

| Approach | Best Suited For | Advantages | Considerations |
|---|---|---|---|
| **`@tool` Decorator** | Standard functions with explicit type hints and docstrings. | Concise, readable, automatic Pydantic schema generation from type hints. | Requires clean type annotations; docstring becomes the tool description. |
| **`StructuredTool.from_function`** | Functions requiring custom Pydantic input schemas (`args_schema`). | Strict schema validation, explicit field descriptions, custom error handlers. | Slightly more verbose than bare `@tool`. |
| **Subclassing `BaseTool`** | Complex tools with internal lifecycle state or async/sync dual execution. | Full control over `_run` and `_arun`, custom configuration, and private attributes. | Requires boilerplate class definition. |

---

## 2. Input Schemas, Typing, & Descriptions

### A. `@tool` with Pydantic Input Schema
```python
from typing import Optional
from langchain_core.tools import tool
from pydantic import BaseModel, Field

class FetchInvoiceSchema(BaseModel):
    invoice_id: str = Field(description="The unique alphanumeric identifier of the invoice (e.g. 'INV-1024').")
    include_line_items: bool = Field(default=False, description="Whether to include detailed line-item breakdown.")
    currency: Optional[str] = Field(default=None, description="Optional ISO currency code for conversion.")

@tool(args_schema=FetchInvoiceSchema)
def fetch_invoice(invoice_id: str, include_line_items: bool = False, currency: Optional[str] = None) -> dict:
    """Fetch invoice details and status from the billing system."""
    # Tool implementation delegates to application service
    return {"id": invoice_id, "status": "paid", "total": 1250.00}
```

### B. Accurate Tool Descriptions & Constraints
The tool's docstring and field descriptions form the schema passed to the LLM. 
- **Be Explicit**: Document accepted formats (e.g. `YYYY-MM-DD`, `ISO-4217`), valid ranges, and limitations.
- **Avoid Ambiguity**: Clearly state what the tool *does* and *does not* do so the model selects the correct tool and parameters.

---

## 3. Model-Tool Binding vs. Execution

### A. Binding Tools to Models
Binding tools provides their JSON schema to the model during invocation:

```python
from langchain_openai import ChatOpenAI
from my_agent.tools import fetch_invoice, search_customers

# Instantiate model
llm = ChatOpenAI(model="gpt-4o", temperature=0)

# Bind tool schemas
tools = [fetch_invoice, search_customers]
llm_with_tools = llm.bind_tools(tools)
```

> **Critical Distinction:** 
> Calling `response = llm_with_tools.invoke(messages)` produces an `AIMessage` containing `tool_calls` metadata (`name`, `args`, `id`). It does **NOT** execute the tool. Tool execution occurs in the runtime (`ToolNode` or graph node).

---

## 4. Handling Unknown Tool Names & Malformed Arguments

When an LLM generates a tool call:
1. **Unknown Tool Name**: The model may hallucinate a tool name not present in `tools`. The runtime must return an informative `ToolMessage(content="Error: Tool 'xyz' does not exist.", tool_call_id=call_id)` rather than crashing the graph.
2. **Schema Validation Failure**: If model arguments fail Pydantic validation (e.g. missing required field or bad type), the tool runtime should capture the validation error and return it to the model for correction.

```python
from langchain_core.tools import ToolException

def safe_tool_executor(tool_func, tool_args: dict, call_id: str):
    try:
        result = tool_func.invoke(tool_args)
        return ToolMessage(content=str(result), tool_call_id=call_id)
    except ToolException as e:
        return ToolMessage(content=f"Tool error: {str(e)}", tool_call_id=call_id)
    except Exception as e:
        return ToolMessage(content=f"Internal tool execution error: {str(e)}", tool_call_id=call_id)
```

