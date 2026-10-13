"""
TC-010: Compile-Time Graph Construction Error.
Defect: builder.add_edge references an unregistered node identifier, causing compile-time failure.
"""
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class CompileErrState(TypedDict):
    val: int

def init_step(state: CompileErrState) -> dict:
    return {"val": 1}

def build_broken_compile_graph():
    builder = StateGraph(CompileErrState)
    builder.add_node("init", init_step)
    builder.add_edge(START, "init")
    # DEFECT: 'ghost_processor' was never registered with add_node
    builder.add_edge("init", "ghost_processor")
    builder.add_edge("ghost_processor", END)
    return builder.compile()

