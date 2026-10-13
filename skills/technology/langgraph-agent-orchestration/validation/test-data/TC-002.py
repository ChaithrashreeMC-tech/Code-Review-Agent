from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class PipelineState(TypedDict):
    raw_data: str
    validated_data: str
    summary: str

def validate_node(state: PipelineState) -> dict:
    return {"validated_data": state["raw_data"].strip()}

def summarize_node(state: PipelineState) -> dict:
    return {"summary": f"Summary of {state['validated_data']}"}

builder = StateGraph(PipelineState)
builder.add_node("validate", validate_node)
builder.add_node("summarize", summarize_node)

builder.add_edge(START, "validate")
builder.add_edge("validate", "summarize")
builder.add_edge("summarize", END)

compiled_pipeline = builder.compile()

