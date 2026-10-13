"""TC-017: Low-risk workflow without human approval requirement not incorrectly flagged for lacking interrupt."""
from langgraph.graph import StateGraph, START, END

def summarize_text(state):
    return {"summary": "Summarized content"}

builder = StateGraph(dict)
builder.add_node("summarize", summarize_text)
builder.add_edge(START, "summarize")
builder.add_edge("summarize", END)
# COMPLIANT: Safe read-only summarization workflow; no human approval requirement in specification

