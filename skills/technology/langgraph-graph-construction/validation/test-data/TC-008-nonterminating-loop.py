"""
TC-008: Genuinely Nonterminating Execution Path or Unsafe Loop.
Defect: Cycle routes back indefinitely without state mutation or exit condition.
"""
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class EndlessLoopState(TypedDict):
    status: str

def noop_node(state: EndlessLoopState) -> dict:
    return {}

def endless_router(state: EndlessLoopState) -> str:
    # DEFECT: Always returns 'loop', never exits
    return "loop"

def build_endless_graph():
    builder = StateGraph(EndlessLoopState)
    builder.add_node("step", noop_node)
    builder.add_edge(START, "step")
    builder.add_conditional_edges("step", endless_router, {"loop": "step"})
    return builder.compile()

