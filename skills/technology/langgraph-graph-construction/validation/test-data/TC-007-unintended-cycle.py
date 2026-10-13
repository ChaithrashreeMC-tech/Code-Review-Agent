"""
TC-007: Unintended Infinite Cycle / Loop Defect.
Defect: Conditional edge routes back to loop node without decrementing/incrementing counter or having exit condition.
"""
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class LoopState(TypedDict):
    status: str
    counter: int

def loop_step(state: LoopState) -> dict:
    # DEFECT: Doesn't update counter or change status, causing infinite cycle
    return {"status": "retry"}

def should_continue(state: LoopState) -> str:
    # DEFECT: Always returns 'retry' because status never changes and counter is not checked
    if state.get("status") == "retry":
        return "retry"
    return "done"

def done_node(state: LoopState) -> dict:
    return {"status": "completed"}

def build_infinite_loop_graph():
    builder = StateGraph(LoopState)
    builder.add_node("loop_step", loop_step)
    builder.add_node("done_node", done_node)
    
    builder.add_edge(START, "loop_step")
    builder.add_conditional_edges(
        "loop_step",
        should_continue,
        {
            "retry": "loop_step",
            "done": "done_node"
        }
    )
    builder.add_edge("done_node", END)
    return builder.compile()

