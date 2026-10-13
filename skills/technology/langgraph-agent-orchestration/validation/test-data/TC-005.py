from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END

class SupervisorState(TypedDict):
    task: str
    iteration_count: int
    worker_output: str

def worker_node(state: SupervisorState) -> dict:
    return {
        "worker_output": f"Done work for: {state['task']}",
        "iteration_count": state.get("iteration_count", 0) + 1
    }

def supervisor_router(state: SupervisorState) -> Literal["worker", "END"]:
    # Bounded termination guardrail
    if state.get("iteration_count", 0) >= 3:
        return "END"
    return "worker"

builder = StateGraph(SupervisorState)
builder.add_node("worker", worker_node)

builder.add_conditional_edges(
    START,
    supervisor_router,
    {"worker": "worker", "END": END}
)
builder.add_conditional_edges(
    "worker",
    supervisor_router,
    {"worker": "worker", "END": END}
)

compiled_supervisor = builder.compile()

