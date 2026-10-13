"""
TC-005: State Schema and In-Place Mutation Defect.
Defect: Node mutates state list directly in place and returns wrong type.
"""
from typing import TypedDict, List
from langgraph.graph import StateGraph, START, END

class BadState(TypedDict):
    items: List[str]
    count: int

def init_node(state: BadState) -> dict:
    return {"items": ["a"], "count": 1}

def mutator_node(state: BadState) -> dict:
    # DEFECT: Mutates state in-place directly and returns integer for items
    state["items"].append("b")
    return {"items": 999}

def build_schema_defect_graph():
    builder = StateGraph(BadState)
    builder.add_node("init", init_node)
    builder.add_node("mutator", mutator_node)
    builder.add_edge(START, "init")
    builder.add_edge("init", "mutator")
    builder.add_edge("mutator", END)
    return builder.compile()

