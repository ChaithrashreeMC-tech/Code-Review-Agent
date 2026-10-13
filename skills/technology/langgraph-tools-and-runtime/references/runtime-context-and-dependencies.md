# Runtime Context & Dependencies

This reference provides guidance on passing runtime configuration, injecting dependencies, managing multi-tenant context, and accessing application services within LangGraph tools.

---

## 1. Runtime Configuration vs. State Channels

In LangGraph, data is passed through two distinct mechanisms:

| Dimension | LangGraph State Channels | `RunnableConfig` / Runtime Context |
|---|---|---|
| **Purpose** | Domain data accumulated and transformed across nodes (e.g. `messages`, `findings`). | Request-scoped infrastructure metadata (e.g. `user_id`, `tenant_id`, `api_key`, `tracing_id`). |
| **Persistence** | Serialized into checkpoints (PostgreSQL, SQLite). | Ephemeral; passed at execution time via `config={"configurable": {...}}`. |
| **Security Rule** | Do NOT store raw secrets, auth headers, or DB pool objects. | Safe for passing runtime context and injected dependencies. |

---

## 2. Injected Arguments & Context (`InjectedToolArg`, `RunnableConfig`)

LangChain / LangGraph supports injecting context directly into tool signatures without exposing those fields to the LLM model schema:

```python
from typing import Annotated
from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from langgraph.prebuilt import InjectedState

@tool
def lookup_account_details(
    account_number: str,
    config: RunnableConfig,
) -> dict:
    """Fetch account summary by account number."""
    # 1. Extract tenant and user metadata from runtime configuration
    configurable = config.get("configurable", {})
    tenant_id = configurable.get("tenant_id")
    user_id = configurable.get("user_id")
    
    if not tenant_id:
        raise ValueError("Missing required tenant_id in execution configuration")
        
    # 2. Delegate to application service with tenant isolation
    return account_service.get_account(tenant_id=tenant_id, account_number=account_number)
```

> **API Note:** `InjectedToolArg` or accepting `config: RunnableConfig` as a parameter excludes the injected field from the tool's JSON schema sent to OpenAI/Anthropic, ensuring the LLM cannot tamper with tenant IDs or system parameters.

---

## 3. Dependency Injection & Service Delegation

### ✅ Recommended Pattern: Delegating to Application Services
Tools should act as thin protocol adapters delegating to pre-configured Application-layer services:

```python
# agents/tools/billing_tools.py
from my_app.application.billing_service import BillingService

def make_billing_tools(billing_service: BillingService):
    @tool
    async def cancel_subscription(subscription_id: str, reason: str, config: RunnableConfig) -> str:
        """Cancel an active billing subscription."""
        user_id = config["configurable"]["user_id"]
        result = await billing_service.cancel(user_id=user_id, sub_id=subscription_id, reason=reason)
        return f"Subscription {subscription_id} cancelled. Status: {result.status}"
    
    return [cancel_subscription]
```

### ❌ Anti-Pattern: Ad-Hoc Infrastructure & Raw DB Access in Tools
```python
# VIOLATION: Instantiating raw database sessions or HTTP clients inside each tool call
@tool
def bad_tool_direct_db_query(user_id: str) -> dict:
    """Direct DB query bypassing application architecture and pooling."""
    import psycopg2 # Ad-hoc DB connection created per invocation
    conn = psycopg2.connect("postgresql://...")
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM users WHERE id = '{user_id}'") # SQL injection risk!
    return cursor.fetchall()
```

---

## 4. Multi-Tenant Context Propagation

In multi-tenant systems:
1. Always extract the `tenant_id` from trusted runtime config (`config["configurable"]["tenant_id"]`), **never** trust model-generated tenant parameters.
2. Pass the tenant ID to the underlying storage/service queries to ensure strict isolation.
3. Validate that runtime config is present before executing any data retrieval.

