"""
TC-013: Valid Graph Using Single-File / Alternative Package Layout.
Graph is fully self-contained in a single module without a 4-file package structure.
This is completely VALID; false positive safeguards must not flag it as an architectural defect.
"""
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class SingleFileState(TypedDict):
    input_text: str
    output_text: str

def format_text(state: SingleFileState) -> dict:
    return {"output_text": state["input_text"].strip().upper()}

def build_single_file_graph():
    builder = StateGraph(SingleFileState)
    builder.add_node("format", format_text)
    builder.add_edge(START, "format")
    builder.add_edge("format", END)
    return builder.compile()

graph = build_single_file_graph()

