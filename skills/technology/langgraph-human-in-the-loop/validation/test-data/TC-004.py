"""TC-004: Edited human input is validated before continuation."""
from langgraph.types import interrupt

def apply_human_edits_node(state):
    human_input = interrupt({"prompt": "Edit transaction amount"})
    # DEFECT: Directly assigning edited_amount without business rule validation (negative or unbounded values)
    edited_amount = human_input["edited_amount"] # e.g. -50000.0 or non-numeric
    return {"amount": edited_amount}

