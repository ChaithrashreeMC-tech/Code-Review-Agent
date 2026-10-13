from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class StepAOutput(TypedDict):
    processed_token: str

class StepBInput(TypedDict):
    verified_auth_token: str

def node_a(state: dict) -> dict:
    # Emits 'processed_token'
    return {"processed_token": "token_abc"}

def node_b(state: dict) -> dict:
    # Expects 'verified_auth_token' - invalid_handoff due to missing_key
    token = state["verified_auth_token"]
    return {"done": token}

builder = StateGraph(dict)
builder.add_node("node_a", node_a)
builder.add_node("node_b", node_b)
builder.add_edge(START, "node_a")
builder.add_edge("node_a", "node_b")
builder.add_edge("node_b", END)
compiled = builder.compile()

