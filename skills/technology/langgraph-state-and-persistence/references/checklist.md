# LangGraph State & Persistence Review Checklist

This checklist defines concrete review rules (`STATE01`–`STATE10`), detection patterns, good/bad code examples, and remediation guidance for managing state schemas, reducers, checkpointing, and thread persistence in LangGraph.

---

## Rule Index

| ID | Rule Name | Objective |
|---|---|---|
| `STATE01` | Explicit State Schema Definition | Define graph state with explicit typed fields; forbid untyped arbitrary dictionary updates. |
| `STATE02` | Deterministic Reducer Contracts | Use pure, associative reducers (`operator.add`, `add_messages`) without in-place mutation. |
| `STATE03` | Durable Production Checkpointing | Use durable persistent checkpointers (`PostgresSaver`, `AsyncSqliteSaver`) for production services. |
| `STATE04` | Checkpointer Lifecycle Management | Manage checkpointer connections via context managers or dependency injection pools. |
| `STATE05` | Thread Isolation & Boundary Protection | Enforce valid `thread_id` keys in execution configs; prevent cross-session state bleeding. |
| `STATE06` | Multi-Tenant Data Isolation | Enforce tenant scoping on `thread_id` or checkpointer namespaces to prevent cross-tenant access. |
| `STATE07` | Sensitive Data Masking | Redact or exclude PII, passwords, and API secrets from persisted graph checkpoints. |
| `STATE08` | State Serialization Safety | Ensure all state fields are serializable (strings, ints, lists, dicts, Pydantic models); avoid open sockets/DB handles. |
| `STATE09` | Checkpoint Recovery & Replay | Ensure interrupted or recovered threads resume safely without duplicate external side effects. |
| `STATE10` | Deterministic Persistence Testing | Test state checkpointing, resumption, and thread isolation in isolated test suites. |

---

## Detailed Rule Checklist

### STATE01: Explicit State Schema Definition
- [ ] State classes inherit from `TypedDict` or `BaseModel`.
- [ ] All keys have explicit type hints.
- ❌ **Anti-pattern:** Untyped state dictionary receiving arbitrary keys during node execution.
- ✅ **Remediation:** Define `class OrderState(TypedDict): order_id: str; total: float`.

### STATE02: Deterministic Reducer Contracts
- [ ] Reducers in `Annotated[T, reducer]` are associative and pure.
- [ ] Reducers return a new accumulator object rather than mutating the input in place.
- ❌ **Anti-pattern:** `def reducer(acc, item): acc.append(item); return acc`.
- ✅ **Remediation:** `def reducer(acc, item): return acc + [item]`.

### STATE03: Durable Production Checkpointing
- [ ] Production services requiring restart survival use persistent checkpointers (`PostgresSaver`, `SqliteSaver`).
- [ ] `MemorySaver` is reserved exclusively for ephemeral CLI scripts or unit tests.
- ❌ **Anti-pattern:** Deploying a multi-instance web service using `MemorySaver`.
- ✅ **Remediation:** Use `AsyncPostgresSaver.from_conn_string(db_url)`.

### STATE04: Checkpointer Lifecycle Management
- [ ] Checkpointer database connections or pools are closed properly via async context managers.
- ❌ **Anti-pattern:** Creating unpooled raw SQLite connections inside node functions on every tick.
- ✅ **Remediation:** Initialize checkpointer at application startup and inject into graph compilation.

### STATE05: Thread Isolation & Boundary Protection
- [ ] Graph execution configs require an explicit `configurable: {"thread_id": ...}`.
- [ ] Separate users/sessions never share the same hardcoded `thread_id`.
- ❌ **Anti-pattern:** Invoking graph with `thread_id="default"` for all incoming HTTP requests.
- ✅ **Remediation:** Generate unique UUIDs or user-scoped thread IDs per session.

### STATE06: Multi-Tenant Data Isolation
- [ ] Thread IDs include tenant prefix (e.g. `f"{tenant_id}:{session_id}"`) or verify tenant ownership.
- ❌ **Anti-pattern:** Accepting arbitrary client-supplied `thread_id` without verifying tenant authorization.
- ✅ **Remediation:** Validate that the requesting tenant owns the requested `thread_id` before querying checkpoints.

### STATE07: Sensitive Data Masking
- [ ] Credit cards, passwords, SSNs, and bearer tokens are omitted or masked before saving to state.
- ❌ **Anti-pattern:** Storing plaintext `api_key` or `password` in graph state saved to persistent database.
- ✅ **Remediation:** Store secrets in runtime environment config (`RunnableConfig`), not persistent graph state.

### STATE08: State Serialization Safety
- [ ] State fields contain only JSON/Msgpack-serializable types.
- ❌ **Anti-pattern:** Storing active DB sessions, raw socket objects, or unpicklable locks in state.
- ✅ **Remediation:** Pass DB sessions via dependency injection or request config, not in graph state.

### STATE09: Checkpoint Recovery & Replay
- [ ] Operations following a checkpoint resume are idempotent.
- ❌ **Anti-pattern:** Charging a credit card immediately upon resumption without checking if payment succeeded.
- ✅ **Remediation:** Check payment transaction status in state before executing charge.

### STATE10: Deterministic Persistence Testing
- [ ] Unit tests verify state recovery using in-memory or temporary SQLite checkpointers.
- ❌ **Anti-pattern:** Leaving checkpointing and resumption completely untested until production.
- ✅ **Remediation:** Write automated test simulating graph pause, restart, and resumption.

