"""
TC-011: Runtime Invocation Error Not Caused by Graph Topology.
Topology compiles cleanly, but node implementation raises unhandled KeyError at invocation time.
"""
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class RuntimeFailureState(TypedDict):
    input_text: str
    metadata: dict
    output: str

def first_node(state: RuntimeFailureState) -> dict:
    return {"output": "pending"}

def crashing_node(state: RuntimeFailureState) -> dict:
    # DEFECT: Unhandled KeyError on uninitialized metadata key
    user_role = state["metadata"]["user_role"]
    return {"output": user_role}

def build_runtime_crash_graph():
    builder = StateGraph(RuntimeFailureState)
    builder.add_node("first", first_node)
    builder.add_node("crash", crashing_node)
    
    # Topology compiles fine
    builder.add_edge(START, "first")
    builder.add_edge("first", "crash")
    builder.add_edge("crash", END)
    return builder.compile()

