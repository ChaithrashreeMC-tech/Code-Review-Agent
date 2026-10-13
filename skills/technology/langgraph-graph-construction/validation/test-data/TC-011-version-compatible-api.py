"""
TC-011: Version-Compatible Graph Construction.
Demonstrates clean usage of LangGraph 0.2+ / 1.x START and END edge bindings.
"""
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class ModernState(TypedDict):
    content: str
    is_valid: bool

def validator_node(state: ModernState) -> dict:
    return {"is_valid": len(state["content"]) > 0}

def build_version_compatible_graph():
    builder = StateGraph(ModernState)
    builder.add_node("validator", validator_node)
    
    # Modern standard START / END edge bindings
    builder.add_edge(START, "validator")
    builder.add_edge("validator", END)
    
    return builder.compile()

graph = build_version_compatible_graph()

