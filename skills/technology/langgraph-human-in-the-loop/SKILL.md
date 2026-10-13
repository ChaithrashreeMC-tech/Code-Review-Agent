---
name: langgraph-human-in-the-loop
description: >-
  Activate when designing, implementing, reviewing, testing, or troubleshooting human-in-the-loop (HITL)
  workflows, LangGraph interrupt and resume mechanics, approval/rejection decision gates, human-edited input
  validation, checkpoint-backed resumption, ownership authorization, audit trails, and idempotency in Python.
---

# LangGraph Human-in-the-Loop (HITL)

## 1. Purpose & Activation

This skill provides technical domain knowledge for architecting, validating, reviewing, and testing Human-in-the-Loop (HITL) workflows in LangGraph Python applications.

**Activate when tasks involve:**
- Introducing human approval, rejection, or review gates into a LangGraph workflow (`interrupt()`, `NodeInterrupt`, or interrupt-before/after).
- Handling graph pause and resumption (`Command(resume=...)` or state update resumptions).
- Processing reviewer decisions: approve, reject, request changes, or supply edited inputs.
- Validating and sanitizing human-provided resume values before continuing graph execution.
- Managing checkpoint-backed paused executions, thread ownership, and multi-tenant authorization.
- Securing approval boundaries: preventing replay attacks, duplicate submissions, and cross-user tampering.
- Enforcing audit logging for consequential actions and tracking review lifecycle states.
- Testing interrupted execution, resumption flows, timeouts, cancellations, and failure recoveries.

**Do NOT activate solely because:**
- An application has a standard web form or database approval flag unrelated to LangGraph execution.
- The task focuses strictly on graph edges, compile flags, or cycle topologies (delegate to `langgraph-graph-construction`).
- The task focuses strictly on multi-agent supervisor routing (delegate to `langgraph-agent-orchestration`).
- The task focuses strictly on state schemas, reducers, or checkpointer engine selection (delegate to `langgraph-state-and-persistence`).
- The task focuses strictly on tool schemas and `ToolNode` execution (delegate to `langgraph-tools-and-runtime`).

---

## 2. Scope & Skill Boundaries

```mermaid
flowchart LR
    subgraph InScope [" LangGraph Human-in-the-Loop (This Skill)"]
        Interrupts["Interrupt & Resume Mechanics"]
        Approvals["Approval & Rejection Workflow Design"]
        Lifecycle["Checkpoint-Backed Paused Execution Lifecycle"]
        Security["Reviewer Authorization & Audit Trails"]
        HITLTest["HITL Testing, Timeouts & Recovery"]
    end

    subgraph Boundaries [" Delegated Responsibilities"]
        GraphConst["Graph Construction -> Edges, Nodes & Compilation"]
        StatePersist["State & Persistence -> Schemas, Reducers & Storage Engines"]
        AgentOrch["Agent Orchestration -> Supervisors & Subgraphs"]
        ToolsRuntime["Tools & Runtime -> Tool Execution & Sandboxing"]
        EngSkills["Engineering Skills -> Finding Classification & 0-10 Scores"]
    end

    InScope -.-> Boundaries
```

---

## 3. Reference Map

| Sub-Task | Reference Document | Focus Areas |
|---|---|---|
| **Interrupts & Resume** | [`references/interrupts-and-resume.md`](references/interrupts-and-resume.md) | `interrupt()` function, pause detection, passing resume values via `Command(resume=...)`, validation contracts, multi-stage interrupts. |
| **Approval Workflow Design** | [`references/approval-workflow-design.md`](references/approval-workflow-design.md) | Approve, reject, request-changes flows, structured decision schemas, sequential vs parallel reviewers, explicit non-approval branches. |
| **Lifecycle & Checkpointing** | [`references/checkpointing-and-execution-lifecycle.md`](references/checkpointing-and-execution-lifecycle.md) | Checkpoint association, process restarts while paused, duplicate resume protection, expiration/cancellation, application vs graph status. |
| **Security & Authorization** | [`references/security-and-authorization.md`](references/security-and-authorization.md) | Reviewer auth, tenant isolation, preventing execution hijacking, server-side decision validation, immutable audit trails. |
| **Testing & Recovery** | [`references/hitl-testing-and-recovery.md`](references/hitl-testing-and-recovery.md) | Testing approval/rejection/timeout paths, deterministic mocking, verifying side-effect idempotency on retry, regression tests. |

---

## 4. Architectural Rules & False-Positive Safeguards

When designing, implementing, or reviewing LangGraph HITL workflows, follow these guidelines:

- **Interrupts Must Have a Resume Contract:** Explicitly define the expected structure, valid values, and validation rules for human resume payloads. Reject invalid values server-side.
- **Server-Side Decision Enforcement:** UI disablement is not security. All permissions, decisions, and edits must be validated and authorized at the API/service boundary before resuming graph execution.
- **Execution Ownership Verification:** A `thread_id` alone is not authorization. Verify authenticated user/tenant ownership before allowing state inspection or resumption.
- **Approval Must Gate the Consequential Action:** The graph topology must ensure protected operations (payments, deployments, data deletion) cannot execute if the reviewer rejects or cancels the request.
- **Retries Must Not Duplicate Side Effects:** Checkpointing resumes graph state, not external transaction status. Operations following approval must use idempotency keys to prevent duplicate executions upon process recovery or duplicate submissions.
- **Application Status vs Graph Status:** Do not conflate business lifecycle states (`pending_review`, `rejected`, `expired`) with LangGraph execution/checkpoint states. Maintain distinct application records where required.
- **Untrusted Human Input:** Treat reviewer-supplied text or edited arguments as untrusted. Validate constraints and sanitize content before feeding it downstream into tools or prompt contexts.
- **Approval Proportionality:** Do not mandate interrupts or human approvals for low-risk, read-only, or automated workflows. Evaluate necessity based on the operation's real-world consequences.
- **Consolidate Root Causes:** Report multiple symptoms stemming from a single approval or interrupt defect as one unified root-cause finding.

---

## 5. Engineering Skill Integration

This skill supplies human-in-the-loop domain expertise and delegates finding classification, scoring, and blocking to standard Engineering Skills:
1. **Identify HITL Defect**: Pinpoint the concrete defect with line and file evidence.
2. **Map to Applicable Engineering Dimension**:
   - **Security** ([`skill-eng-security`](../../engineering/skill-eng-security/SKILL.md)): Unauthorized resume operations, missing tenant isolation, tampering with approval decisions, missing audit logs.
   - **Business Logic** ([`skill-eng-business-logic`](../../engineering/skill-eng-business-logic/SKILL.md)): Rejection branch continuing into approved action, missing validation on edited inputs, duplicate side effects on repeated approval submission.
   - **Maintainability** ([`skill-eng-maintainability`](../../engineering/skill-eng-maintainability/SKILL.md)): Undocumented resume payload contracts, brittle approval status mapping, hardcoded reviewer roles.
   - **Performance** ([`skill-eng-performance`](../../engineering/skill-eng-performance/SKILL.md)): Polling approval status in tight loops, redundant checkpoint writes during pause states.
   - **Modularity** ([`skill-eng-modularity`](../../engineering/skill-eng-modularity/SKILL.md)): Direct coupling between graph nodes and approval UI models, bypassing Application-layer review services.
3. **Delegate Scoring**: Use the platform's native 0–10 scale and Gate policies; never invent local scoring rubrics.

