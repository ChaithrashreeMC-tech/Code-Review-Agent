"""
TC-012: Distinguishing Graph Construction from Persistence & Tool Runtime.
The graph construction is completely valid. An external SQLite connection or tool runner error
is an external runtime/persistence concern, not a graph construction defect.
"""
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class ExternalConcernState(TypedDict):
    query: str
    response: str

def query_node(state: ExternalConcernState) -> dict:
    return {"response": f"Echo: {state['query']}"}

def build_valid_topology_graph():
    # Graph structure is completely valid
    builder = StateGraph(ExternalConcernState)
    builder.add_node("query", query_node)
    builder.add_edge(START, "query")
    builder.add_edge("query", END)
    return builder.compile()

graph = build_valid_topology_graph()

