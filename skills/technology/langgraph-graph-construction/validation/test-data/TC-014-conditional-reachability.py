"""
TC-014: Apparent Unreachable Node That Is Reachable via Conditional Path Map.
'remediate' node lacks a direct linear `builder.add_edge(...)` to it, but is the target
of a conditional edge's path_map.
This is completely VALID; false positive safeguards must not flag it as an orphaned node.
"""
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class DynamicPathState(TypedDict):
    status: str
    action: str

def check_node(state: DynamicPathState) -> dict:
    return {"action": "fix" if state["status"] == "error" else "ok"}

def route_action(state: DynamicPathState) -> str:
    return state["action"]

def remediate_node(state: DynamicPathState) -> dict:
    return {"status": "fixed"}

def build_conditional_reachability_graph():
    builder = StateGraph(DynamicPathState)
    builder.add_node("check", check_node)
    builder.add_node("remediate", remediate_node)  # Reachable via conditional edge
    
    builder.add_edge(START, "check")
    # 'remediate' is reachable through this path_map:
    builder.add_conditional_edges(
        "check",
        route_action,
        {
            "fix": "remediate",
            "ok": END
        }
    )
    builder.add_edge("remediate", END)
    return builder.compile()

graph = build_conditional_reachability_graph()

