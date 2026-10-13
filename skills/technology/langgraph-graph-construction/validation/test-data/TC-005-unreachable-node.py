"""
TC-005: Unreachable Node Defect.
Defect: A node is registered with builder.add_node() but has zero incoming edges from START or other nodes.
"""
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class UnreachState(TypedDict):
    data: str

def active_node(state: UnreachState) -> dict:
    return {"data": "active"}

def orphan_node(state: UnreachState) -> dict:
    # DEFECT: Registered but completely disconnected from graph flow
    return {"data": "orphan"}

def build_unreachable_graph():
    builder = StateGraph(UnreachState)
    builder.add_node("active", active_node)
    builder.add_node("orphan", orphan_node)  # DEFECT: Unreachable
    
    builder.add_edge(START, "active")
    builder.add_edge("active", END)
    # 'orphan' has no incoming edge
    return builder.compile()

