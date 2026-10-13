# Checkpointing & Thread Isolation

This reference documents checkpoint lifecycles, superstep boundaries, thread ID management, multi-tenant isolation, authorization checks, and durable storage strategies.

---

## 1. Checkpoint Lifecycle & Execution Supersteps

In LangGraph, execution advances in discrete synchronization steps called **supersteps**:
1. At each superstep, active nodes execute concurrently or sequentially.
2. When all nodes in the superstep complete, their state updates are applied via channel reducers.
3. The checkpointer persists an immutable checkpoint containing:
   - Complete state channel values.
   - Next pending node targets (execution boundary).
   - Checkpoint metadata (thread ID, step counter, timestamp).

```text
Superstep 1: [Node A] executes -> Reducers applied -> Checkpoint (Thread: T1, Step: 1)
                                                                 |
                                                                 v
Superstep 2: [Node B, Node C] in parallel -> Reducers applied -> Checkpoint (Thread: T1, Step: 2)
                                                                 |
                                                                 v
Interrupted / Paused (Awaiting Human Review) -> Resumes exactly from Step 2 boundary
```

---

## 2. Distinguishing State Boundaries

Keep these three concepts cleanly separated:
1. **Execution State Boundary**: The ephemeral snapshot recorded in checkpoints allowing resumption of interrupted graphs.
2. **Conversation History**: The accumulated message thread (e.g. `messages` channel) exchanged between user and agent.
3. **External Side Effects**: Real-world operations (charges, emails, DB writes) outside the graph boundary that checkpoints do not natively rollback.

---

## 3. Thread Identifiers vs. Tenant & User Authorization

### Cardinal Rules of Thread Isolation:
1. **Thread ID Scope**: A `thread_id` identifies a specific execution stream or conversation session.
2. **Thread ID is NOT Authorization**: Knowing or guessing a `thread_id` does NOT grant permission to view or manipulate state.
3. **Tenant & User Verification**: Always verify that the authenticated caller owns the requested `thread_id` prior to retrieving state or resuming execution:

```python
# agents/services/chat_service.py
from agents.graphs.chat_graph import compiled_graph
from agents.services.auth import verify_user_owns_thread

async def handle_user_message(user_id: str, tenant_id: str, thread_id: str, message: str) -> dict:
    # 1. Enforce tenant and user authorization BEFORE accessing checkpoint state
    if not await verify_user_owns_thread(user_id=user_id, tenant_id=tenant_id, thread_id=thread_id):
        raise PermissionError(f"User {user_id} is not authorized for thread {thread_id}")
    
    # 2. Invoke graph with isolated thread configuration
    config = {
        "configurable": {
            "thread_id": f"{tenant_id}:{user_id}:{thread_id}"
        }
    }
    return await compiled_graph.ainvoke({"user_message": message}, config=config)
```

---

## 4. Concurrency & Race Conditions

When multiple incoming HTTP requests or background jobs target the same `thread_id` simultaneously:
- **Lock Contention**: Checkpointers using relational databases (e.g. `PostgresSaver`) enforce row-level locking or optimistic concurrency checks.
- **Race Condition Safeguard**: Enforce per-thread concurrency locks at the API gateway or service boundary to avoid simultaneous graph mutations on the same active thread.

---

## 5. Storage Backends & Checkpointer Selection

| Checkpointer | Persistence Durability | Best Suited For | Deployment Notes |
|---|---|---|---|
| `MemorySaver` | In-Memory (Ephemeral) | Unit tests, local development, single-turn workflows. | Lost on process restart; does not work across multi-replica deployments. |
| `PostgresSaver` / `AsyncPostgresSaver` | Durable Relational DB | Production multi-replica deployments, multi-turn chat, human-in-the-loop. | Requires database tables/migrations (`langgraph-checkpoint-postgres`). |
| `SqliteSaver` / `AsyncSqliteSaver` | Durable Local File | Single-instance services, embedded tools, desktop clients. | File lock contention under high concurrent writes. |
| `RedisSaver` | Durable In-Memory / Distributed | High-throughput sessions with TTL eviction policies. | Configure key expiration and eviction policies to prevent unbounded memory growth. |

---

## 6. Retention & Cleanup Policies

- Set explicit Time-To-Live (TTL) or schedule cleanup workers for old checkpoints.
- Ensure compliance with data retention requirements (e.g. GDPR right-to-be-forgotten) by providing mechanisms to purge all checkpoint history for a specific `user_id` or `thread_id`.


