"""
TC-004: Edge Referencing an Unregistered Node.
Defect: builder.add_edge points to a node name that was never registered with add_node.
"""
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class SimpleState(TypedDict):
    val: int

def init_node(state: SimpleState) -> dict:
    return {"val": 1}

def build_unregistered_edge_graph():
    builder = StateGraph(SimpleState)
    builder.add_node("init_node", init_node)
    builder.add_edge(START, "init_node")
    # DEFECT: 'nonexistent_processor' was never registered via builder.add_node()
    builder.add_edge("init_node", "nonexistent_processor")
    builder.add_edge("nonexistent_processor", END)
    return builder.compile()

