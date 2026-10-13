"""TC-001: Valid approval resumes the intended execution."""
from langgraph.types import interrupt, Command
from langgraph.graph import StateGraph, START, END

def review_node(state):
    decision = interrupt({"prompt": "Approve transaction?"})
    if decision.get("approved"):
        return Command(goto="payout_node", update={"status": "APPROVED"})
    return Command(goto=END, update={"status": "REJECTED"})

def payout_node(state):
    return {"payout_complete": True}

builder = StateGraph(dict)
builder.add_node("review", review_node)
builder.add_node("payout_node", payout_node)
builder.add_edge(START, "review")
# COMPLIANT: Valid approval resumes execution and properly routes to payout_node

