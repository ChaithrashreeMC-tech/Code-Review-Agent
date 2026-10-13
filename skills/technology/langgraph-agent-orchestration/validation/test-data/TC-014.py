# Valid external project with non-Clean-Architecture flat layout
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class SimpleWorkflowState(TypedDict):
    text: str
    result: str

def process_text(state: SimpleWorkflowState) -> dict:
    return {"result": state["text"].upper()}

builder = StateGraph(SimpleWorkflowState)
builder.add_node("process", process_text)
builder.add_edge(START, "process")
builder.add_edge("process", END)

workflow = builder.compile()

