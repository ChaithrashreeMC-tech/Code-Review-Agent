# Approval Workflow Design

This reference provides guidance on designing robust approval, rejection, change-request, and multi-reviewer workflows in LangGraph applications.

---

## 1. Approval Decision Modeling

Reviewer inputs should use structured enums or explicit schemas rather than ambiguous strings:

| Decision | State Action | Next Graph Route | Required Metadata |
|---|---|---|---|
| **Approve** | Transition status to `APPROVED` | Route to protected consequential node (e.g. `execute_payout`) | `reviewer_id`, `timestamp` |
| **Reject** | Transition status to `REJECTED` | Route to termination or notification node (e.g. `notify_rejection`) | `rejection_reason`, `reviewer_id` |
| **Request Changes** | Transition status to `CHANGES_REQUESTED` | Route back to generation or drafting agent node | `feedback_comments`, `reviewer_id` |
| **Edit & Approve** | Apply human-edited fields to state | Route to validation node, then protected consequential node | `edited_fields`, `reviewer_id` |

---

## 2. Explicit Non-Approval Routing (Gating Consequential Operations)

> **Cardinal Rule of HITL Safety:**
> Graph routing MUST guarantee that a rejection, cancellation, or unknown decision can never fall through into an approval-only node.

```python
from langgraph.graph import StateGraph, START, END

def route_after_human_review(state: ReviewState) -> str:
    decision = state.get("approval_status")
    
    if decision == "APPROVED":
        return "execute_wire_transfer"
    elif decision == "REJECTED":
        return "handle_rejection"
    elif decision == "CHANGES_REQUESTED":
        return "refine_draft"
    else:
        # Strict fallback: unknown or unhandled decisions halt safely
        return "handle_invalid_decision"

builder = StateGraph(ReviewState)
builder.add_conditional_edges(
    "human_review_node",
    route_after_human_review,
    {
        "execute_wire_transfer": "execute_wire_transfer",
        "handle_rejection": "handle_rejection",
        "refine_draft": "refine_draft",
        "handle_invalid_decision": "handle_invalid_decision"
    }
)
```

---

## 3. Application Lifecycle Status vs. Graph Execution State

Do NOT conflate business domain status with LangGraph thread state:

```text
Application Record (PostgreSQL/REST API):
  Status: PENDING_REVIEW -> APPROVED | REJECTED | EXPIRED | CANCELLED
  Reviewer: usr_alice
  ExpiresAt: 2026-10-15T00:00:00Z

LangGraph Thread Execution:
  Thread ID: tenant_1:order_101
  Checkpoint State: Interrupted at superstep 3
  Resumed with: Command(resume={"approved": True})
```

- An application service coordinates the UI, timeout timers, and permission checks.
- When an approval expires or is cancelled in the application database, the service updates its DB record and either resumes the graph with a `CANCELLED` command or deletes the pending execution.

---

## 4. Multi-Reviewer Patterns

### A. Sequential Reviewers (Tier 1 Manager -> Tier 2 VP)
Model as sequential interrupt nodes: `manager_review_node` -> `vp_review_node`. Each node halts for its respective role.

### B. Parallel Review Consensus (Quorum / Majority)
1. An interrupt node yields review requests to multiple stakeholders.
2. The application service accumulates decisions in an external database.
3. When the quorum threshold is reached (e.g. 2 of 3 approvals), the service resumes the graph with the aggregated decision payload.

