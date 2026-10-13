"""
TC-009: Concurrent Reducer Defect.
Defect: Parallel branches write to the same list field without an Annotated reducer, causing InvalidUpdateError in LangGraph.
"""
from typing import TypedDict, List
from langgraph.graph import StateGraph, START, END

class UnreducedState(TypedDict):
    # DEFECT: 'logs' is a plain List without Annotated[List[str], operator.add] or add_messages
    logs: List[str]
    summary: str

def branch_a(state: UnreducedState) -> dict:
    return {"logs": ["branch_a_done"]}

def branch_b(state: UnreducedState) -> dict:
    return {"logs": ["branch_b_done"]}

def aggregate_logs(state: UnreducedState) -> dict:
    return {"summary": f"Collected {len(state.get('logs', []))} logs"}

def build_concurrent_defect_graph():
    builder = StateGraph(UnreducedState)
    builder.add_node("branch_a", branch_a)
    builder.add_node("branch_b", branch_b)
    builder.add_node("aggregator", aggregate_logs)
    
    # Parallel Fan-Out
    builder.add_edge(START, "branch_a")
    builder.add_edge(START, "branch_b")
    
    # Fan-In (will fail concurrently without a reducer on 'logs')
    builder.add_edge("branch_a", "aggregator")
    builder.add_edge("branch_b", "aggregator")
    builder.add_edge("aggregator", END)
    return builder.compile()

