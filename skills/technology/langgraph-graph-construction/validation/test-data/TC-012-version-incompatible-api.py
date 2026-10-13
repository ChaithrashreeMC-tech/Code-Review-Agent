"""
TC-012: Version-Incompatible API Usage.
Defect: Code calls a non-existent / deprecated method `builder.bind_graph_entry()`
instead of standard `builder.add_edge(START, ...)` or `builder.set_entry_point(...)`.
"""
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class VersionState(TypedDict):
    val: str

def work_step(state: VersionState) -> dict:
    return {"val": "done"}

def build_version_incompatible_graph():
    builder = StateGraph(VersionState)
    builder.add_node("work", work_step)
    # DEFECT: Fictitious / invalid API call
    builder.bind_graph_entry("work")
    builder.add_edge("work", END)
    return builder.compile()

