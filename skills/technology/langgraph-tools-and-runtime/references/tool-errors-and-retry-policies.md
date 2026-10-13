# Tool Errors & Retry Policies

This reference documents failure classification, bounded retries, exponential backoff, timeouts, error sanitization, and side-effect idempotency in LangGraph tools.

---

## 1. Failure Classification

When an error occurs during tool execution, classify it to choose the appropriate recovery strategy:

| Failure Type | Examples | Recovery Strategy | Action |
|---|---|---|---|
| **User / Validation Error** | Invalid date format, missing required ID, bad argument value. | Model Correction | Return clear error description in `ToolMessage(content=...)` so the model can fix the arguments. |
| **Transient Infrastructure Error** | Rate limit (HTTP 429), gateway timeout (504), network hiccup. | Automated Retry | Retry with exponential backoff and jitter up to a fixed retry limit (e.g. 3 attempts). |
| **Authorization / Permission Error** | Forbidden (403), invalid tenant access, insufficient scope. | Terminal Rejection | Return sanitized rejection in `ToolMessage` or raise exception; do NOT retry. |
| **Fatal System Crash** | Unhandled programming bug, DB constraint violation. | Circuit Break / Halt | Raise exception to graph execution or trigger fallback node. |

---

## 2. Returning Tool Result vs. Raising Graph Exceptions

- **Return as `ToolMessage` (Model Recoverable)**: Use when the model can self-correct (e.g. "Customer ID '123' not found. Did you mean 'CUST-123'?").
- **Raise Graph Exception (Runtime Halt)**: Use when security is violated, infrastructure is completely down, or the graph must transition to an explicit error recovery node.

```python
from langchain_core.tools import tool, ToolException

@tool
def process_refund(order_id: str, amount: float) -> str:
    """Issue a refund for an eligible customer order."""
    if amount <= 0:
        # Recoverable validation error: tell the LLM why it failed
        return "Error: Refund amount must be greater than zero."
        
    try:
        tx_id = payment_gateway.refund(order_id, amount)
        return f"Refund successful. Transaction ID: {tx_id}"
    except RateLimitExceeded:
        # Transient error handled by retry decorator
        raise
    except UnauthorizedError:
        # Non-retryable permission error
        return "Permission Denied: Caller does not have refund authority."
```

---

## 3. Bounded Retries, Backoff, & Timeouts

Never implement unbounded or open-ended retries. Always enforce:
1. **Max Retry Limit**: Restrict retries to 3–5 attempts.
2. **Exponential Backoff with Jitter**: Avoid thundering herds on upstream services.
3. **Hard Timeout**: Enforce strict execution timeouts (e.g. 10–30s) per tool call.

```python
import tenacity
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((TimeoutError, ConnectionError)),
    reraise=True
)
def call_external_api_with_retry(endpoint: str, payload: dict) -> dict:
    return http_client.post(endpoint, json=payload, timeout=10.0)
```

---

## 4. Idempotency & Duplicate Side Effects

> **Critical Rule:** Retrying a tool that creates, modifies, or deletes external resources without an idempotency key causes duplicate charges, duplicate records, or inconsistent state.

When implementing mutating tools:
1. Require or generate an **idempotency key** combining `thread_id` and the operation details:
   - `idempotency_key = f"tool_{thread_id}_{order_id}_{action}"`
2. Pass the key to downstream APIs so duplicate calls safely return the existing result without re-executing mutations.

```python
@tool
def charge_customer_tool(customer_id: str, amount_cents: int, config: RunnableConfig) -> str:
    """Charge a customer credit card."""
    thread_id = config.get("configurable", {}).get("thread_id", "default")
    idempotency_key = f"charge_{thread_id}_{customer_id}_{amount_cents}"
    
    # Gateway deduplicates requests with identical idempotency keys
    receipt = billing_client.charge(
        customer_id=customer_id,
        amount=amount_cents,
        idempotency_key=idempotency_key
    )
    return f"Charged {amount_cents} cents. Receipt: {receipt.id}"
```

