"""
TC-008: State Schema Mismatch Defect.
Defect: Node returns an incompatible data type for a state field (e.g. integer instead of list).
"""
from typing import TypedDict, List
from langgraph.graph import StateGraph, START, END

class MismatchState(TypedDict):
    tags: List[str]
    count: int

def init_tags(state: MismatchState) -> dict:
    return {"tags": ["init"]}

def bad_producer(state: MismatchState) -> dict:
    # DEFECT: Returns a single int for 'tags' field which is declared as List[str]
    return {"tags": 12345}

def consumer_node(state: MismatchState) -> dict:
    # Crashes if tags is not an iterable / list
    return {"count": len(state["tags"])}

def build_schema_mismatch_graph():
    builder = StateGraph(MismatchState)
    builder.add_node("init", init_tags)
    builder.add_node("producer", bad_producer)
    builder.add_node("consumer", consumer_node)
    
    builder.add_edge(START, "init")
    builder.add_edge("init", "producer")
    builder.add_edge("producer", "consumer")
    builder.add_edge("consumer", END)
    return builder.compile()

