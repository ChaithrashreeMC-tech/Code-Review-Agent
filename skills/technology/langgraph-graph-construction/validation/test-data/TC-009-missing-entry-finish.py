"""
TC-009: Invalid Entry or Terminal Configuration.
Defect: Graph defines nodes but omits connection from START and connection to END.
"""
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class MissingEndpointsState(TypedDict):
    data: str

def work_node(state: MissingEndpointsState) -> dict:
    return {"data": "done"}

def build_missing_endpoints_graph():
    builder = StateGraph(MissingEndpointsState)
    builder.add_node("work", work_node)
    # DEFECT: Missing START and END edge bindings
    return builder.compile()

