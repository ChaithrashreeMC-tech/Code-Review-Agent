"""
TC-014: Insufficient Evidence / Uncertain Review Case.
Review Context: Route function delegates dynamically to an external unresolved callback.
Agent must note uncertainty rather than asserting a false positive defect.
"""
from typing import TypedDict, Any
from langgraph.graph import StateGraph, START, END

class DynamicRouteState(TypedDict):
    data: dict

def step_node(state: DynamicRouteState) -> dict:
    return {"data": state.get("data", {})}

def dynamic_router(state: DynamicRouteState, custom_dispatcher: Any = None) -> str:
    # Routing depends on runtime injected callback not visible in this diff
    if custom_dispatcher:
        return custom_dispatcher(state)
    return "default_step"

def default_step(state: DynamicRouteState) -> dict:
    return {"data": {"status": "default"}}

def build_dynamic_graph(dispatcher: Any = None):
    builder = StateGraph(DynamicRouteState)
    builder.add_node("step", step_node)
    builder.add_node("default_step", default_step)
    
    builder.add_edge(START, "step")
    builder.add_conditional_edges(
        "step",
        lambda s: dynamic_router(s, dispatcher),
        {"default_step": "default_step"}
    )
    builder.add_edge("default_step", END)
    return builder.compile()

