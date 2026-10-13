"""
TC-001: Valid Linear LangGraph StateGraph.
Constructs a valid sequential pipeline from START to node1 to node2 to END.
"""
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class LinearState(TypedDict):
    input_text: str
    processed_text: str
    status: str

def step_one(state: LinearState) -> dict:
    return {"processed_text": state["input_text"].strip()}

def step_two(state: LinearState) -> dict:
    return {"status": "completed"}

def build_linear_graph():
    builder = StateGraph(LinearState)
    builder.add_node("step_one", step_one)
    builder.add_node("step_two", step_two)
    builder.add_edge(START, "step_one")
    builder.add_edge("step_one", "step_two")
    builder.add_edge("step_two", END)
    return builder.compile()

graph = build_linear_graph()

