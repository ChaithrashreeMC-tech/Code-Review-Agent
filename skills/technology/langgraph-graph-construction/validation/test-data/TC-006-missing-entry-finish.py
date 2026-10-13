"""
TC-006: Missing Entry / Finish Configuration Defect.
Defect: Graph defines nodes but has no entry edge from START and no connection to END.
"""
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class MissingEntryState(TypedDict):
    msg: str

def work_node(state: MissingEntryState) -> dict:
    return {"msg": "done"}

def build_missing_entry_graph():
    builder = StateGraph(MissingEntryState)
    builder.add_node("work", work_node)
    # DEFECT: Missing builder.add_edge(START, "work") and builder.add_edge("work", END)
    return builder.compile()

