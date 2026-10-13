# Security & Authorization in HITL Workflows

This reference documents reviewer authentication, tenant isolation, thread ownership verification, server-side validation, and audit logging for LangGraph approvals.

---

## 1. Reviewer Authentication & Thread Ownership

> **Cardinal Rule:** A `thread_id` or execution token is NOT an authorization mechanism.

Knowing a `thread_id` must never be sufficient to view or resume an approval. Every resume endpoint must enforce:
1. **Authentication**: Verify the caller's JWT/session identity.
2. **Tenant Isolation**: Verify the caller belongs to the tenant owning the execution (`tenant_id`).
3. **Role/Permission Verification**: Verify the caller holds the required role (e.g. `ROLE_FINANCIAL_APPROVER`) or is the explicitly assigned reviewer.

```python
# agents/services/approval_service.py
from agents.graphs.workflow import compiled_graph
from agents.services.auth import get_current_user, verify_thread_access

async def resume_workflow_endpoint(
    thread_id: str,
    decision_payload: dict,
    auth_header: str
):
    user = await get_current_user(auth_header)
    
    # 1. Enforce strict authorization check before touching checkpoint
    is_authorized = await verify_thread_access(
        user_id=user.id,
        tenant_id=user.tenant_id,
        thread_id=thread_id,
        required_role="approver"
    )
    if not is_authorized:
        raise PermissionError(f"User {user.id} is not authorized to resume thread {thread_id}")
        
    # 2. Server-side validation of decision payload
    validated_decision = validate_decision_schema(decision_payload, user_id=user.id)
    
    # 3. Resume graph execution with isolated config
    config = {"configurable": {"thread_id": f"{user.tenant_id}:{thread_id}"}}
    return await compiled_graph.ainvoke(Command(resume=validated_decision), config=config)
```

---

## 2. Server-Side Decision & Edit Validation

Never trust client-submitted approval payloads without server-side validation:
- **Enum Bounds**: Ensure `decision` is strictly one of `{"APPROVED", "REJECTED", "CHANGES_REQUESTED"}`.
- **Field Edits**: If the reviewer modified values (e.g. edited payout amount), validate that the new values comply with business constraints (e.g. `amount > 0` and within maximum limit).
- **Prompt Injection Defense**: If reviewer comments are interpolated into downstream LLM prompts, wrap them in data delimiter tags and sanitize adversarial instructions.

---

## 3. Comprehensive Audit Logging

All consequential HITL decisions must be recorded in an immutable audit ledger:

```python
async def record_audit_event(
    tenant_id: str,
    thread_id: str,
    reviewer_id: str,
    action: str,
    metadata: dict
):
    audit_entry = {
        "event_id": str(uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
        "tenant_id": tenant_id,
        "thread_id": thread_id,
        "actor": reviewer_id,
        "action": action, # e.g. "APPROVED_WIRE_TRANSFER"
        "decision_payload": sanitize_sensitive_data(metadata)
    }
    await audit_db.insert(audit_entry)
```

---

## 4. Protecting Sensitive Data

- Mask credit card numbers, passwords, and PII from reviewer comment logs and checkpoint snapshots.
- Ensure PostgreSQL checkpoint tables have encryption at rest enabled.

