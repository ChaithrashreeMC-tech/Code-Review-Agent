"""
TC-007: Valid Cycle with Bounded Termination Condition.
A cyclical graph with a retry counter that safely terminates at END.
This is completely VALID; false positive safeguards must prevent reporting an infinite loop.
"""
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class BoundedLoopState(TypedDict):
    retry_count: int
    is_success: bool

def process_attempt(state: BoundedLoopState) -> dict:
    return {"retry_count": state["retry_count"] + 1, "is_success": state["retry_count"] >= 2}

def should_retry(state: BoundedLoopState) -> str:
    # Guaranteed to exit when retry_count reaches limit
    if state["is_success"] or state["retry_count"] >= 3:
        return "exit"
    return "retry"

def finalize_node(state: BoundedLoopState) -> dict:
    return {}

def build_bounded_cycle_graph():
    builder = StateGraph(BoundedLoopState)
    builder.add_node("attempt", process_attempt)
    builder.add_node("finalize", finalize_node)
    
    builder.add_edge(START, "attempt")
    builder.add_conditional_edges(
        "attempt",
        should_retry,
        {
            "retry": "attempt",
            "exit": "finalize"
        }
    )
    builder.add_edge("finalize", END)
    return builder.compile()

graph = build_bounded_cycle_graph()

