"""
TC-010: Valid Graph Using Modular Package Conventions.
Follows clean separation between State, Nodes, Edges, and Graph assembly.
"""
from typing import TypedDict, Annotated, List
import operator
from langgraph.graph import StateGraph, START, END

# --- state.py representation ---
class PackageState(TypedDict):
    task: str
    steps_completed: Annotated[List[str], operator.add]
    final_output: str

# --- nodes.py representation ---
def planning_node(state: PackageState) -> dict:
    return {"steps_completed": ["planned"]}

def execution_node(state: PackageState) -> dict:
    return {"steps_completed": ["executed"], "final_output": f"Done: {state['task']}"}

# --- edges.py representation ---
def route_after_planning(state: PackageState) -> str:
    return "execute"

# --- graph.py assembly ---
def build_modular_package_graph():
    builder = StateGraph(PackageState)
    builder.add_node("planner", planning_node)
    builder.add_node("executor", execution_node)
    
    builder.add_edge(START, "planner")
    builder.add_conditional_edges("planner", route_after_planning, {"execute": "executor"})
    builder.add_edge("executor", END)
    
    return builder.compile()

graph = build_modular_package_graph()

