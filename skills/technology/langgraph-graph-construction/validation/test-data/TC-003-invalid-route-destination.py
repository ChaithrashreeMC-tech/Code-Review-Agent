"""
TC-003: Invalid Route Destination Defect.
Route function returns a label that is not present in path_map / not registered as a node.
"""
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class BadRouteState(TypedDict):
    status: str

def check_status(state: BadRouteState) -> dict:
    return {"status": "unknown_error"}

def route_fn(state: BadRouteState) -> str:
    # Defect: Returns 'unhandled_case' which is not in the path_map
    if state["status"] == "unknown_error":
        return "unhandled_case"
    return "ok"

def ok_node(state: BadRouteState) -> dict:
    return {"status": "success"}

def build_bad_route_graph():
    builder = StateGraph(BadRouteState)
    builder.add_node("check", check_status)
    builder.add_node("ok", ok_node)
    builder.add_edge(START, "check")
    # DEFECT: path_map only defines 'ok', but route_fn can return 'unhandled_case'
    builder.add_conditional_edges(
        "check",
        route_fn,
        {
            "ok": "ok"
        }
    )
    builder.add_edge("ok", END)
    return builder.compile()

