from typing import TypedDict, List
from langgraph.graph import StateGraph, START

class ParallelConflictState(TypedDict):
    # Defect: missing_reducer causing conflicting_concurrent_write in fan-out
    results: List[str]

def branch_a(state: ParallelConflictState) -> dict:
    return {"results": ["a"]}

def branch_b(state: ParallelConflictState) -> dict:
    return {"results": ["b"]}

builder = StateGraph(ParallelConflictState)
builder.add_node("a", branch_a)
builder.add_node("b", branch_b)
builder.add_edge(START, "a")
builder.add_edge(START, "b")

