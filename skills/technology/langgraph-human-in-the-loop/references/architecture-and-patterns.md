# LangGraph Human-in-the-Loop: Architecture & Patterns

This reference document details interrupt mechanics, approval workflow design, checkpointing lifecycle, security authorization, and deterministic testing for LangGraph HITL applications.

---

## 1. Interrupts & Resume Mechanics

Use `interrupt()` to request human intervention and `Command(resume=...)` to resume:

```python
from langgraph.types import interrupt, Command
from langgraph.graph import StateGraph, START, END

def review_transaction_node(state: dict) -> Command[str]:
    # Interrupt pauses graph and yields payload to caller
    decision = interrupt({
        "prompt": f"Approve transaction of ${state['amount']} for order {state['order_id']}?",
        "order_id": state["order_id"],
        "amount": state["amount"]
    })
    
    # Process resume decision
    if decision.get("approved"):
        return Command(goto="process_payout", update={"approval_status": "APPROVED"})
    return Command(goto=END, update={"approval_status": "REJECTED"})

def process_payout_node(state: dict) -> dict:
    return {"payout_complete": True}
```

---

## 2. API Endpoint Resumption & Authorization

Resume execution through an authorized API endpoint:

```python
from fastapi import HTTPException
from langgraph.types import Command

async def resume_workflow_endpoint(thread_id: str, payload: dict, current_user: dict, graph):
    # 1. Check authorization
    if not current_user.get("is_approver"):
        raise HTTPException(status_code=403, detail="Unauthorized to approve workflow")
        
    # 2. Verify thread state exists
    config = {"configurable": {"thread_id": thread_id}}
    state_snapshot = graph.get_state(config)
    if not state_snapshot or not state_snapshot.next:
        raise HTTPException(status_code=404, detail="No pending interrupt found for thread")
        
    # 3. Resume graph execution
    result = graph.invoke(Command(resume=payload), config=config)
    return {"status": "SUCCESS", "result": result}
```

---

## 3. Idempotent Execution & Side-Effect Safety

Protect external operations from double-execution during resume or replay:

```python
import uuid

def execute_external_transfer_node(state: dict) -> dict:
    # Use deterministic idempotency key tied to thread and action
    idempotency_key = state.get("idempotency_key") or f"tx-{state['order_id']}"
    
    # Call bank API with idempotency key
    response = payment_gateway.transfer(
        amount=state["amount"],
        account_id=state["account_id"],
        idempotency_key=idempotency_key
    )
    return {"transfer_id": response.id, "transferred": True}
```

---

## 4. Multi-Stage Interrupt Flows

Coordinate multi-level approval hierarchies cleanly:

```python
def manager_review_node(state: dict) -> Command[str]:
    decision = interrupt({"prompt": "Manager approval required"})
    if not decision.get("approved"):
        return Command(goto=END, update={"status": "REJECTED_BY_MANAGER"})
    return Command(goto="compliance_review", update={"manager_approved": True})

def compliance_review_node(state: dict) -> Command[str]:
    decision = interrupt({"prompt": "Compliance review required"})
    if not decision.get("approved"):
        return Command(goto=END, update={"status": "REJECTED_BY_COMPLIANCE"})
    return Command(goto="execute_action", update={"compliance_approved": True})
```

