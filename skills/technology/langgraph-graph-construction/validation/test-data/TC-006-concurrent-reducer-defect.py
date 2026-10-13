"""
TC-006: Parallel Branches Updating the Same State Key Without Reducer.
Defect: Parallel branches write to 'logs' which lacks an Annotated reducer, causing InvalidUpdateError.
"""
from typing import TypedDict, List
from langgraph.graph import StateGraph, START, END

class UnreducedParallelState(TypedDict):
    logs: List[str]

def branch_1(state: UnreducedParallelState) -> dict:
    return {"logs": ["branch_1_done"]}

def branch_2(state: UnreducedParallelState) -> dict:
    return {"logs": ["branch_2_done"]}

def aggregator_node(state: UnreducedParallelState) -> dict:
    return {}

def build_parallel_defect_graph():
    builder = StateGraph(UnreducedParallelState)
    builder.add_node("b1", branch_1)
    builder.add_node("b2", branch_2)
    builder.add_node("agg", aggregator_node)
    
    # Parallel Fan-out
    builder.add_edge(START, "b1")
    builder.add_edge(START, "b2")
    
    # Fan-in
    builder.add_edge("b1", "agg")
    builder.add_edge("b2", "agg")
    builder.add_edge("agg", END)
    return builder.compile()

