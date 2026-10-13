from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class QuickWorkflowState(TypedDict):
    input: str
    output: str

def quick_node(state: QuickWorkflowState) -> dict:
    return {"output": state["input"].strip()}

builder = StateGraph(QuickWorkflowState)
builder.add_node("quick", quick_node)
builder.add_edge(START, "quick")
builder.add_edge("quick", END)

# Ephemeral graph intentionally does not use checkpointer
ephemeral_graph = builder.compile()

