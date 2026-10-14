# LangGraph State & Persistence: Architecture & Patterns

This reference document details state schema design, reducer implementation, checkpointer configuration, thread isolation, and data protection for LangGraph applications.

---

## 1. State Schemas and Reducer Patterns

Define graph state schemas using `TypedDict` or Pydantic `BaseModel`:

```python
from typing import Annotated, Optional
from operator import add
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentSessionState(TypedDict):
    session_id: str
    user_id: str
    tenant_id: str
    
    # Reducers for accumulating data across nodes
    messages: Annotated[list[BaseMessage], add_messages]
    logs: Annotated[list[str], add]
    retry_count: Annotated[int, lambda a, b: a + b]
```

### Custom Pure Reducer
```python
def deduplicate_list_reducer(existing: list[str], updates: list[str]) -> list[str]:
    """Pure reducer that merges lists without in-place mutation."""
    return list(dict.fromkeys(existing + updates))
```

---

## 2. Checkpointers & Storage Backends

### A. Ephemeral Checkpointer (Development / Unit Tests)
```python
from langgraph.checkpoint.memory import MemorySaver

# Use ONLY in unit tests or ephemeral CLI scripts
checkpointer = MemorySaver()
app = builder.compile(checkpointer=checkpointer)
```

### B. Persistent SQLite Checkpointer (Local / Small Services)
```python
import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver

# Synchronous or async SQLite checkpointer
conn = sqlite3.connect("checkpoints.db", check_same_thread=False)
checkpointer = SqliteSaver(conn)
app = builder.compile(checkpointer=checkpointer)
```

### C. Persistent PostgreSQL Checkpointer (Production Microservices)
```python
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

async def get_compiled_graph(db_pool):
    checkpointer = AsyncPostgresSaver(db_pool)
    await checkpointer.setup()
    return builder.compile(checkpointer=checkpointer)
```

---

## 3. Thread Isolation and Multi-Tenancy

Always execute graph invocations with an explicit `thread_id` and enforce tenant scoping:

```python
def run_user_session(graph, tenant_id: str, user_id: str, session_id: str, input_data: dict):
    # Tenant-scoped thread ID ensures multi-tenant isolation
    scoped_thread_id = f"{tenant_id}:{user_id}:{session_id}"
    
    config = {
        "configurable": {
            "thread_id": scoped_thread_id
        }
    }
    
    return graph.invoke(input_data, config=config)
```

---

## 4. State Recovery and Inspection

Inspect current checkpoint state or resume interrupted executions:

```python
# Inspect current state
state_snapshot = app.get_state(config)
print("Current node:", state_snapshot.next)
print("Current values:", state_snapshot.values)

# Get state history
for snapshot in app.get_state_history(config):
    print(snapshot.config["configurable"]["checkpoint_id"], snapshot.values)
```

