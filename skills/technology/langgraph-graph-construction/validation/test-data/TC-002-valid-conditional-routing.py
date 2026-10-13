"""
TC-002: Valid Conditional Routing LangGraph StateGraph.
Uses add_conditional_edges with complete path_map routing.
"""
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class RouteState(TypedDict):
    value: int
    decision: str
    result: str

def evaluate_node(state: RouteState) -> dict:
    return {"decision": "high" if state["value"] > 10 else "low"}

def high_handler(state: RouteState) -> dict:
    return {"result": "high_processed"}

def low_handler(state: RouteState) -> dict:
    return {"result": "low_processed"}

def route_decision(state: RouteState) -> str:
    return state.get("decision", "low")

def build_conditional_graph():
    builder = StateGraph(RouteState)
    builder.add_node("evaluate", evaluate_node)
    builder.add_node("handle_high", high_handler)
    builder.add_node("handle_low", low_handler)
    
    builder.add_edge(START, "evaluate")
    builder.add_conditional_edges(
        "evaluate",
        route_decision,
        {
            "high": "handle_high",
            "low": "handle_low"
        }
    )
    builder.add_edge("handle_high", END)
    builder.add_edge("handle_low", END)
    return builder.compile()

graph = build_conditional_graph()

