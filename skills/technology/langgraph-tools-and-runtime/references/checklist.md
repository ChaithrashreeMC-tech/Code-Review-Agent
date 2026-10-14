# LangGraph Tools & Runtime Review Checklist

This checklist defines concrete review rules (`TOOL01`–`TOOL10`), detection patterns, good/bad code examples, and remediation guidance for tool definition, model binding, ToolNode execution, runtime context, error handling, and security.

---

## Rule Index

| ID | Rule Name | Objective |
|---|---|---|
| `TOOL01` | Explicit Tool Schema Definition | Define tools with explicit Pydantic `args_schema` or type annotations; forbid untyped parameters. |
| `TOOL02` | Model Binding & Registration | Ensure all tools bound to the model (`bind_tools`) are registered in the corresponding `ToolNode`. |
| `TOOL03` | Tool Message Association | Ensure every `ToolMessage` matches a valid `tool_call_id` from the preceding `AIMessage.tool_calls`. |
| `TOOL04` | Runtime Context Validation | Safely access `RunnableConfig` (`config.get("configurable", {})`) without raw key access. |
| `TOOL05` | Injected Tool Dependencies | Inject external services and repositories into tools via runtime config or closures; avoid global singletons. |
| `TOOL06` | Authorization Boundaries | Verify caller permissions before executing destructive or sensitive operations in tool bodies. |
| `TOOL07` | Tenant Context Protection | Retrieve `tenant_id` from authenticated runtime context (`config`), never from model-generated arguments. |
| `TOOL08` | Error Classification & Retries | Differentiate transient network errors from permanent client errors; enforce bounded retry policies. |
| `TOOL09` | Output Sanitization & Security | Redact secrets and mask raw external payloads to prevent prompt injection and data leaks. |
| `TOOL10` | Isolated Tool Unit Testing | Test tool logic, schema validation, and error branches directly using mock clients and unit tests. |

---

## Detailed Rule Checklist

### TOOL01: Explicit Tool Schema Definition
- [ ] Tool functions use `@tool(args_schema=...)` or type-annotated arguments with docstrings.
- ❌ **Anti-pattern:** `@tool def query_data(*args, **kwargs): ...` without argument documentation.
- ✅ **Remediation:** Define `class QueryInput(BaseModel): query: str = Field(description="Search term")` and use `@tool(args_schema=QueryInput)`.

### TOOL02: Model Binding & Registration
- [ ] Tools bound via `llm.bind_tools(tools)` match the exact tool list supplied to `ToolNode(tools)`.
- ❌ **Anti-pattern:** LLM is bound to `[search_tool, delete_tool]`, but `ToolNode` only has `[search_tool]`, causing runtime unhandled tool call errors.
- ✅ **Remediation:** Define a single canonical tool list: `TOOLS = [search_tool, delete_tool]`.

### TOOL03: Tool Message Association
- [ ] Tool execution produces a `ToolMessage(content=..., tool_call_id=call["id"])`.
- ❌ **Anti-pattern:** Emitting `ToolMessage` with empty or missing `tool_call_id`.
- ✅ **Remediation:** Use LangGraph's standard `ToolNode` which handles ID correlation automatically.

### TOOL04: Runtime Context Validation
- [ ] Access `config.get("configurable", {})` with default fallbacks; do not index `config["configurable"]["key"]` directly.
- ❌ **Anti-pattern:** `api_key = config["configurable"]["api_key"]` throwing `KeyError`.
- ✅ **Remediation:** `api_key = config.get("configurable", {}).get("api_key")` with explicit validation.

### TOOL05: Injected Tool Dependencies
- [ ] Tools receive dependencies via `InjectedToolArg` or runtime config context.
- ❌ **Anti-pattern:** Using an uninitialized global variable `global_order_service.submit()`.
- ✅ **Remediation:** Inject dependency via `config["configurable"]["order_service"]`.

### TOOL06: Authorization Boundaries
- [ ] Destructive tools verify authorization tokens or user roles prior to state modification.
- ❌ **Anti-pattern:** A tool allowing arbitrary SQL deletion without checking permissions.
- ✅ **Remediation:** Validate user role in tool handler before executing destructive queries.

### TOOL07: Tenant Context Protection
- [ ] Query scoping uses `tenant_id` extracted from authenticated runtime config.
- ❌ **Anti-pattern:** Accepting `tenant_id: str` as an LLM argument, allowing LLM hallucinations to cross tenant boundaries.
- ✅ **Remediation:** Extract tenant ID from `RunnableConfig` context inside the tool.

### TOOL08: Error Classification & Retries
- [ ] Classify retryable vs non-retryable exceptions; do not retry HTTP 400 Bad Request.
- [ ] Loops must be bounded with max attempts and exponential backoff.
- ❌ **Anti-pattern:** `while True:` retrying forever on invalid client arguments.
- ✅ **Remediation:** Catch `httpx.RequestError`, retry up to 3 times, return error message on permanent failure.

### TOOL09: Output Sanitization & Security
- [ ] Sanitize external HTML/JSON outputs; strip API keys and confidential credentials before returning.
- ❌ **Anti-pattern:** Returning raw third-party webpage containing prompt injection attacks into the conversation messages.
- ✅ **Remediation:** Parse and sanitize content into markdown and mask credentials.

### TOOL10: Isolated Tool Unit Testing
- [ ] Unit test each tool function directly with valid and invalid inputs.
- ❌ **Anti-pattern:** Relying only on end-to-end graph tests to test low-level tool behavior.
- ✅ **Remediation:** Write `test_tool_validation()` and `test_tool_error_handling()` using pytest.

