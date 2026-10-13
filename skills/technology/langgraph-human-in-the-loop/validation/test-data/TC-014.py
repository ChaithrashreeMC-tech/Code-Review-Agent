"""TC-014: Audit events are recorded according to requirements."""
from langgraph.types import interrupt

def sensitive_action_node(state):
    decision = interrupt({"prompt": "Approve database drop"})
    if decision.get("approved"):
        # DEFECT: Modifies production resource without recording reviewer ID, timestamp, or decision rationale in audit log
        perform_db_drop()
        return {"dropped": True}
    return {"dropped": False}

def perform_db_drop():
    pass

