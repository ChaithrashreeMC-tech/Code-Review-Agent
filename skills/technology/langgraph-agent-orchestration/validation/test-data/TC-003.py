import operator
from typing import Annotated, List, TypedDict
from langgraph.graph import StateGraph, START, END

class ParallelReviewState(TypedDict):
    content: str
    reviews: Annotated[List[dict], operator.add]
    final_decision: str

def sec_reviewer(state: ParallelReviewState) -> dict:
    return {"reviews": [{"reviewer": "sec", "status": "pass"}]}

def perf_reviewer(state: ParallelReviewState) -> dict:
    return {"reviews": [{"reviewer": "perf", "status": "pass"}]}

def aggregator(state: ParallelReviewState) -> dict:
    # Resilient aggregation handling multiple branch outputs
    all_passed = all(r.get("status") == "pass" for r in state.get("reviews", []))
    return {"final_decision": "APPROVED" if all_passed else "REJECTED"}

builder = StateGraph(ParallelReviewState)
builder.add_node("sec_reviewer", sec_reviewer)
builder.add_node("perf_reviewer", perf_reviewer)
builder.add_node("aggregator", aggregator)

builder.add_edge(START, "sec_reviewer")
builder.add_edge(START, "perf_reviewer")
builder.add_edge("sec_reviewer", "aggregator")
builder.add_edge("perf_reviewer", "aggregator")
builder.add_edge("aggregator", END)

compiled_parallel = builder.compile()

