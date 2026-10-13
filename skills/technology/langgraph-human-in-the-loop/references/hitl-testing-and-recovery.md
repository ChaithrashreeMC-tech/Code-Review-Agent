# HITL Testing & Recovery

This reference provides testing patterns for verifying the entire interrupt, approval, rejection, and resumption lifecycle in LangGraph.

---

## 1. Testing Interrupt & Resume with Deterministic Mocks

Use `MemorySaver` for fast, isolated unit tests of interrupt and resume logic:

```python
# tests/test_hitl_workflow.py
import pytest
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command
from my_app.graphs.approval_graph import build_approval_graph

@pytest.mark.asyncio
async def test_successful_approval_flow():
    checkpointer = MemorySaver()
    graph = build_approval_graph(checkpointer=checkpointer)
    config = {"configurable": {"thread_id": "test_thread_1"}}
    
    # 1. Trigger initial run (pauses at interrupt)
    init_result = await graph.ainvoke({"order_id": "ORD-1", "amount": 2500}, config=config)
    
    state = graph.get_state(config)
    assert len(state.next) > 0  # Confirms graph is paused waiting for input
    
    # 2. Resume with approval decision
    resume_cmd = Command(resume={"approved": True, "reviewer_id": "mgr_1"})
    resumed_result = await graph.ainvoke(resume_cmd, config=config)
    
    # 3. Assert graph continued to completion with approved status
    final_state = graph.get_state(config)
    assert final_state.values["status"] == "COMPLETED_APPROVED"
```

---

## 2. Testing Rejection Safety (Regression Gating)

Always write explicit regression tests proving that a rejection CANNOT reach the consequential action node:

```python
@pytest.mark.asyncio
async def test_rejection_never_executes_payout():
    mock_payout_service = AsyncMock()
    checkpointer = MemorySaver()
    graph = build_approval_graph(checkpointer=checkpointer, payout_service=mock_payout_service)
    config = {"configurable": {"thread_id": "test_thread_reject"}}
    
    # Pause at review
    await graph.ainvoke({"order_id": "ORD-2", "amount": 9000}, config=config)
    
    # Resume with REJECTED
    resume_cmd = Command(resume={"approved": False, "reason": "Suspected fraud"})
    await graph.ainvoke(resume_cmd, config=config)
    
    final_state = graph.get_state(config)
    assert final_state.values["status"] == "REJECTED"
    # CRITICAL CHECK: Protected payout service must never have been called
    mock_payout_service.execute_payout.assert_not_called()
```

---

## 3. Testing Recovery Across Restarts

When testing restart durability:
1. Initialize with a persistent checkpointer (e.g. SQLite or PostgreSQL test container).
2. Execute up to the interrupt point and destroy the in-memory graph instance.
3. Instantiate a fresh graph object pointing to the same database.
4. Issue `Command(resume=...)` and verify execution resumes from the interrupted step without re-executing completed initial steps.

---

## 4. Key Review Checklist for HITL Workflows

| Area | Verification Item |
|---|---|
| **Resume Contract** | Does the interrupt node validate the resume payload schema before using it? |
| **Gating** | Does graph routing ensure rejections/cancellations terminate before reaching protected actions? |
| **Authorization** | Does the resume handler verify user and tenant ownership of the `thread_id`? |
| **Idempotency** | Do actions executed post-resume use idempotency keys to handle duplicate submissions? |
| **Audit Trail** | Are reviewer IDs, timestamps, and decision outcomes immutably logged? |
| **Testing** | Are there automated tests covering approval, rejection, and invalid resume payloads? |

