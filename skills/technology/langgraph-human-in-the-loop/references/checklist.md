# LangGraph Human-in-the-Loop Review Checklist

This checklist defines concrete review rules (`HITL01`–`HITL10`), detection patterns, good/bad code examples, and remediation guidance for interrupt-based human-in-the-loop (HITL) workflows, approval routing, state validation, and security controls in LangGraph.

---

## Rule Index

| ID | Rule Name | Objective |
|---|---|---|
| `HITL01` | Explicit Interrupt Mechanics | Use `interrupt(payload)` to pause graph execution; provide structured context for human review. |
| `HITL02` | Validated Resumption | Resume execution via `Command(resume=...)` targeting explicit `thread_id` and checkpoint state. |
| `HITL03` | Approval & Rejection Branching | Explicitly branch on human decisions; ensure rejection terminates or routes away from protected actions. |
| `HITL04` | Resume Payload Validation | Validate human decisions and edited inputs with Pydantic schemas or Enums before applying to state. |
| `HITL05` | Resume Authorization & RBAC | Enforce caller authentication and approval permissions prior to processing resume payloads. |
| `HITL06` | Multi-Tenant Resume Boundary | Enforce tenant isolation to prevent unauthorized cross-tenant thread resumption. |
| `HITL07` | Approval Expiry & Lifecycle | Reject expired or cancelled approval requests before resuming protected operations. |
| `HITL08` | Idempotency & Side-Effect Safety | Attach idempotency keys to external side effects following interrupt resumption to prevent duplicate executions. |
| `HITL09` | Audit Trail Recording | Record immutable audit logs capturing reviewer identity, timestamp, thread ID, and decision rationale. |
| `HITL10` | Business vs Execution Status | Distinguish domain approval outcome (`REJECTED`) from technical graph execution status (`COMPLETED`). |

---

## Detailed Rule Checklist

### HITL01: Explicit Interrupt Mechanics
- [ ] Pauses are triggered via `decision = interrupt({"prompt": "...", "data": ...})`.
- ❌ **Anti-pattern:** Using raw `input()` or thread-blocking polling loops inside node functions.
- ✅ **Remediation:** Call `interrupt()` and let LangGraph pause graph execution at a clean checkpoint.

### HITL02: Validated Resumption
- [ ] Resume calls use `graph.invoke(Command(resume=decision), config={"configurable": {"thread_id": ...}})`.
- ❌ **Anti-pattern:** Invoking graph with a new empty state dictionary instead of `Command(resume=...)`.
- ✅ **Remediation:** Pass `Command(resume=decision)` with the corresponding thread config.

### HITL03: Approval & Rejection Branching
- [ ] Graph explicitly handles both `approved` and `rejected` outcomes.
- ❌ **Anti-pattern:** Unconditional edge from review node to payment node regardless of whether review was approved.
- ✅ **Remediation:** Use `Command(goto="payment" if approved else END)`.

### HITL04: Resume Payload Validation
- [ ] Validate human input and edited state values against strict schemas before resumption.
- ❌ **Anti-pattern:** Applying raw unvalidated strings or unbounded numeric edits directly into financial state.
- ✅ **Remediation:** Validate payload with `ApprovalDecisionModel.model_validate(raw_payload)`.

### HITL05: Resume Authorization & RBAC
- [ ] Check caller roles and permissions at the API resume endpoint before resuming the graph.
- ❌ **Anti-pattern:** Any authenticated user can resume an executive-level approval thread.
- ✅ **Remediation:** Verify `current_user.has_permission("APPROVE_DISBURSEMENT")` in the API handler.

### HITL06: Multi-Tenant Resume Boundary
- [ ] Verify that the target `thread_id` belongs to the requesting tenant.
- ❌ **Anti-pattern:** Resuming threads across tenant boundaries based purely on a client-supplied `thread_id`.
- ✅ **Remediation:** Validate tenant ownership against the thread checkpointer before invoking resume.

### HITL07: Approval Expiry & Lifecycle
- [ ] Check if the approval window has expired before resuming.
- ❌ **Anti-pattern:** Resuming and executing a 30-day-old expired approval request.
- ✅ **Remediation:** Check `datetime.now(timezone.utc) < state["approval_deadline"]`.

### HITL08: Idempotency & Side-Effect Safety
- [ ] External side effects (payments, API calls) downstream from an interrupt use idempotency keys.
- ❌ **Anti-pattern:** Calling external payment gateway directly without checking if the transaction was already processed.
- ✅ **Remediation:** Pass deterministic `idempotency_key=f"payout-{thread_id}"` to the payment provider.

### HITL09: Audit Trail Recording
- [ ] Record reviewer ID, timestamp, and decision rationale in an immutable audit log.
- ❌ **Anti-pattern:** Completing a high-risk operation without recording who approved it.
- ✅ **Remediation:** Emit structured audit event `AuditLog.record(...)` upon approval execution.

### HITL10: Business vs Execution Status
- [ ] Rejections update business state (`status="REJECTED"`) and complete graph execution cleanly at `END`.
- ❌ **Anti-pattern:** Raising an unhandled Python Exception on user rejection to halt the graph.
- ✅ **Remediation:** Return `Command(goto=END, update={"business_status": "REJECTED"})`.

