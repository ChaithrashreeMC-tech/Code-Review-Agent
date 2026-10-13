"""TC-020: Distinguish application approval status from graph execution status."""
from langgraph.types import interrupt, Command
from langgraph.graph import StateGraph, START, END

def approval_step(state):
    decision = interrupt({"prompt": "Approve request?"})
    if not decision.get("approved"):
        # COMPLIANT: Business state is REJECTED, while graph execution cleanly finishes at END (COMPLETED)
        return Command(goto=END, update={"business_status": "REJECTED", "completed_successfully": True})
    return Command(goto="process_step", update={"business_status": "APPROVED"})

def process_step(state):
    return {"business_status": "PROCESSED", "completed_successfully": True}

builder = StateGraph(dict)
builder.add_node("approval", approval_step)
builder.add_node("process_step", process_step)
builder.add_edge(START, "approval")

