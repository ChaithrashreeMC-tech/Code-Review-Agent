# Interrupts & Resume Mechanics

This reference documents interrupting graph execution for human input, detecting pending decisions, passing resume values, validating payloads, and handling multi-stage reviews in LangGraph.

---

## 1. Interrupt Lifecycle & Purpose

In LangGraph (0.2.x+), dynamic human-in-the-loop pauses are triggered using the `interrupt()` function inside node functions:

```python
from langgraph.types import interrupt, Command

def human_approval_node(state: OrderState) -> Command:
    # 1. Prepare payload presented to the human reviewer
    review_request = {
        "order_id": state["order_id"],
        "amount": state["amount"],
        "recipient": state["recipient"]
    }
    
    # 2. Pause execution and yield request to the caller/checkpoint
    decision: dict = interrupt(review_request)
    
    # 3. Execution resumes here when caller invokes graph with Command(resume=...)
    if decision.get("approved"):
        return Command(goto="process_payment", update={"status": "approved"})
    else:
        return Command(goto="cancel_order", update={"status": "rejected", "rejection_reason": decision.get("reason")})
```

---

## 2. Detecting Pending Interrupts & Supplying Resume Values

### A. Detecting Paused State
When a node calls `interrupt()`, execution halts at that superstep. The caller receives the interrupted graph state:

```python
config = {"configurable": {"thread_id": "order_thread_101"}}

# Initial invocation halts at interrupt()
result = graph.invoke({"order_id": "ORD-123", "amount": 5000}, config=config)

# Check pending interrupts in current state snapshot
state = graph.get_state(config)
if state.next:
    # Next node is waiting on human input
    pending_interrupt = state.tasks[0].interrupts[0].value
    print("Awaiting review for:", pending_interrupt)
```

### B. Resuming Execution with `Command(resume=...)`
To resume the paused execution, invoke the graph with a `Command(resume=...)` object on the same thread config:

```python
# Caller resumes with approved decision payload
resume_command = Command(resume={"approved": True, "reviewer_id": "usr_mgr_42"})
final_state = graph.invoke(resume_command, config=config)
```

> **Critical Rule:** Resuming is NOT calling `graph.invoke({"new": "input"}, config=config)` from scratch. Re-invoking with a standard input dictionary on an interrupted thread without `Command(resume=...)` will re-run nodes from the beginning or corrupt pending interrupt state.

---

## 3. Resume Payload Contract & Validation

Human-supplied resume values are external untrusted inputs. Always validate the resume structure before consuming it:

```python
from pydantic import BaseModel, Field

class ApprovalDecisionSchema(BaseModel):
    approved: bool
    reviewer_id: str
    rejection_reason: str = Field(default="")
    edited_amount: float | None = None

def validate_decision_node(raw_decision: dict) -> ApprovalDecisionSchema:
    try:
        return ApprovalDecisionSchema.model_validate(raw_decision)
    except Exception as e:
        raise ValueError(f"Malformed human review decision: {e}")
```

---

## 4. Multi-Stage Interrupts

When a workflow requires multiple human review stages (e.g. Legal Review -> Financial Approval):
1. Each stage calls `interrupt()` with its specific review context.
2. The checkpointer records the distinct interrupt state at each stage.
3. Resuming stage 1 advances the graph to stage 2, which then triggers its own `interrupt()`.
4. Ensure each stage inspects its respective resume contract and updates separate state channels.

