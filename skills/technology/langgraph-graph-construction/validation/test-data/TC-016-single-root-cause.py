"""
TC-016: Single Root Cause Defect Generating Multiple Symptoms.
A missing schema channel causes downstream node failure, branch merge error, and router failure.
Skill must consolidate the root cause into a single primary finding (MOD01 / MAINT01)
rather than reporting duplicate findings across multiple dimensions.
"""
from typing import TypedDict, List
from langgraph.graph import StateGraph, START, END

class RootCauseState(TypedDict):
    # ROOT DEFECT: Missing 'analysis_report' field in state schema definition
    raw_query: str

def parse_node(state: RootCauseState) -> dict:
    return {"raw_query": state.get("raw_query", "").strip()}

def analyze_node(state: RootCauseState) -> dict:
    # Symptom: Tries to write to undeclared channel
    return {"analysis_report": "complete"}

def build_single_root_cause_graph():
    builder = StateGraph(RootCauseState)
    builder.add_node("parse", parse_node)
    builder.add_node("analyze", analyze_node)
    
    builder.add_edge(START, "parse")
    builder.add_edge("parse", "analyze")
    builder.add_edge("analyze", END)
    return builder.compile()

