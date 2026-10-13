from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END

class RouterState(TypedDict):
    query_type: str
    response: str

def fast_handler(state: RouterState) -> dict:
    return {"response": "Fast response"}

def deep_handler(state: RouterState) -> dict:
    return {"response": "Deep research response"}

def route_query(state: RouterState) -> Literal["fast", "deep"]:
    if state.get("query_type") == "quick":
        return "fast"
    return "deep"

builder = StateGraph(RouterState)
builder.add_node("fast", fast_handler)
builder.add_node("deep", deep_handler)

builder.add_conditional_edges(
    START,
    route_query,
    {"fast": "fast", "deep": "deep"}
)
builder.add_edge("fast", END)
builder.add_edge("deep", END)

compiled_conditional = builder.compile()

