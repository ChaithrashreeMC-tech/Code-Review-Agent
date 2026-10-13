"""TC-002: Rejection cannot continue into an approval-only operation."""
from langgraph.types import interrupt
from langgraph.graph import StateGraph, START

def faulty_review_node(state):
    decision = interrupt({"prompt": "Approve wire transfer?"})
    # DEFECT: Rejection falls through into execute_wire_transfer without branching
    return {"reviewer_decision": decision.get("approved")}

def execute_wire_transfer(state):
    bank_client.transfer(state["amount"])
    return {"transferred": True}

builder = StateGraph(dict)
builder.add_node("review", faulty_review_node)
builder.add_node("payout", execute_wire_transfer)
builder.add_edge(START, "review")
builder.add_edge("review", "payout") # Direct unconditional edge allows rejected execution to pay!

