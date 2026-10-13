"""TC-013: Multiple interrupt stages resume at the correct stage."""
from langgraph.types import interrupt, Command
from langgraph.graph import StateGraph, START, END

def manager_review(state):
    mgr_approval = interrupt({"prompt": "Manager approval required"})
    if not mgr_approval.get("approved"):
        return Command(goto=END, update={"status": "REJECTED_BY_MANAGER"})
    return Command(goto="compliance_review", update={"manager_approved": True})

def compliance_review(state):
    comp_approval = interrupt({"prompt": "Compliance review required"})
    if not comp_approval.get("approved"):
        return Command(goto=END, update={"status": "REJECTED_BY_COMPLIANCE"})
    return Command(goto="execute_action", update={"compliance_approved": True})

def execute_action(state):
    return {"status": "SUCCESS"}

builder = StateGraph(dict)
builder.add_node("manager_review", manager_review)
builder.add_node("compliance_review", compliance_review)
builder.add_node("execute_action", execute_action)
builder.add_edge(START, "manager_review")
# COMPLIANT: Multi-stage review cleanly tracks stages and resumes at correct step

