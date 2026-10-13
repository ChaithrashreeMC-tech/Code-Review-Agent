"""TC-006: Unauthorized resume attempts are denied."""
from langgraph.types import Command

def resume_endpoint(graph, thread_id: str, payload: dict, request_user: dict):
    # DEFECT: Resume payload processed without verifying caller has approval permissions or matches assigned reviewer
    decision = payload.get("decision")
    return graph.invoke(Command(resume=decision), config={"configurable": {"thread_id": thread_id}})

