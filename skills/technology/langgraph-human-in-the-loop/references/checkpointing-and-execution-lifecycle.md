# Checkpointing & Paused Execution Lifecycle

This reference documents checkpoint management for paused executions, service restarts during review, duplicate resume prevention, and side-effect safety.

---

## 1. Why Resumable HITL Requires Durable Checkpointing

In production multi-turn or human-in-the-loop applications:
- Reviewers may take minutes, hours, or days to respond.
- API service replicas restart, scale down, or deploy updates in the interim.
- **Durable Checkpointing (`PostgresSaver`)** is mandatory for persisting interrupted execution state across service restarts and multiple server replicas.
- **In-Memory (`MemorySaver`)** is suitable ONLY for automated unit tests or ephemeral local development.

```python
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

async def get_production_graph(pool):
    checkpointer = AsyncPostgresSaver(pool)
    # Ensure tables exist
    await checkpointer.setup()
    return workflow.compile(checkpointer=checkpointer)
```

---

## 2. Service Restarts & Crash Recovery While Paused

When an execution pauses at `interrupt()`:
1. The checkpointer writes the exact graph state and next pending task to the PostgreSQL database.
2. If the API server crashes or restarts immediately after, no state is lost.
3. When the human reviewer eventually clicks "Approve", any healthy API replica loads the checkpoint using the `thread_id` and resumes execution cleanly from the interrupt point.

---

## 3. Duplicate Resume Submissions & Concurrency Guards

A common defect in web approval portals is the **double-click / duplicate submission**:
- Reviewer clicks "Approve" twice in rapid succession.
- Two simultaneous HTTP requests attempt to resume the same `thread_id`.

### Defect Mitigation:
1. **Application-Level State Lock**: The approval service sets `status = 'PROCESSING'` in the relational DB using optimistic locking (`UPDATE approvals SET status = 'PROCESSING' WHERE id = :id AND status = 'PENDING'`). If zero rows are updated, reject the second request.
2. **Idempotency Keys**: Consequential actions immediately following resume must pass an `idempotency_key = f"{thread_id}:{approval_id}"` to external payment/action gateways.

> **Critical Safety Principle:**
> Checkpointing guarantees state restoration, NOT exactly-once execution of downstream external side effects. Always enforce idempotency on operations following resume.

---

## 4. Expired, Cancelled, & Incompatible Checkpoints

- **Expired Approvals**: If an approval TTL expires, the application service marks the approval record expired and disallows resumption.
- **Schema Changes Across Deployments**: If an application deploys state schema changes while an approval is pending, ensure legacy checkpoints can deserialize without errors (use `NotRequired` fields or default values).
- **Cleanup & Retention**: Implement background TTL purge policies to clean up completed or expired checkpoints after their audit retention period.

