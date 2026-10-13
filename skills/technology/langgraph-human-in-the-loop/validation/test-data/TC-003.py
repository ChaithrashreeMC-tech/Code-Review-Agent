"""TC-003: Invalid decision values are rejected or handled according to policy."""
from langgraph.types import interrupt

def unvalidated_decision_node(state):
    # DEFECT: Consuming raw arbitrary decision string without validating against allowed enum
    raw_decision = interrupt({"prompt": "Select decision: APPROVE or REJECT"})
    # Free-form string bypasses enum validation
    state_update = {"status": raw_decision["status"].upper()} # Crashes with KeyError/AttributeError if malformed
    return state_update

