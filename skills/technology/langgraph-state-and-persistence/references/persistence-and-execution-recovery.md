# Persistence & Execution Recovery

This reference documents crash recovery, retries, node replay, side-effect idempotency, post-action persistence failures, and backend error handling in LangGraph.

---

## 1. Execution Recovery & Node Replay

When a graph run fails or the host process restarts:

1. **State Restoration**: LangGraph loads the latest valid checkpoint for the `thread_id` and resumes execution from the interrupted node.
2. **Replaying Nodes**: Resumed nodes will execute again with the state recorded in the last checkpoint.

```text
Step 1: Checkpoint (State: initial) -> Node A succeeds -> Checkpoint (State: after_A)
Step 2: Node B executes -> Node B crashes midway
Recovery: LangGraph reloads Checkpoint (State: after_A) -> Node B re-executes from start
```

---

## 2. Idempotency for External Side Effects

> **Critical Rule:** Checkpointing guarantees graph state recovery, NOT external side-effect exactly-once execution.

If a node performs an external side effect (e.g. charging a credit card, sending an email, writing to an external database):
- Ensure operations use **idempotency keys** derived from `thread_id` and step count:
  - `idempotency_key = f"{thread_id}:{step_count}:{action_type}"`
- Check whether the external action was already completed before repeating it on node replay.

```python
async def process_payment_node(state: PaymentState) -> dict:
    payment_id = state["payment_id"]
    idempotency_key = f"pay_{payment_id}_{state.get('attempt_count', 0)}"
    
    # Delegate to idempotent payment service with explicit key
    result = await payment_service.charge(
        amount=state["amount"],
        idempotency_key=idempotency_key
    )
    return {"payment_status": result.status, "transaction_id": result.tx_id}
```

---

## 3. Post-Action Persistence Failures & Reconciliation

A specific failure scenario occurs when:
1. A node successfully executes an external side-effect (e.g., charge processed at payment gateway).
2. The checkpointer write to PostgreSQL fails immediately afterward (e.g. DB connection timeout).
3. On graph recovery/restart, the node will be re-executed from the previous checkpoint.

### Mitigation Strategies:
- **Idempotency Keys**: Ensure the external API recognizes the duplicate request and returns the existing result without executing twice.
- **Pre-action State Flagging**: Store a pending transaction intent in state prior to side-effect execution.
- **Reconciliation Check**: On node entry, check if the external entity already exists before triggering creation.

---

## 4. Handling Checkpointer Read/Write Failures

1. **Transient Database Errors**: Wrap checkpointer operations in retry policies with exponential backoff for network or lock contention errors.
2. **Graceful Diagnostics**: If checkpointing fails on a non-critical step, log the persistence failure and alert monitoring systems rather than crashing without diagnostics.
3. **Transaction Safety**: Use database-backed checkpointers with transactional commit boundaries (`AsyncPostgresSaver`) to prevent corrupted half-written state snapshots.

