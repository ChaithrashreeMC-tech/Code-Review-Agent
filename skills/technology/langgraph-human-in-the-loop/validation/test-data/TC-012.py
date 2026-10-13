"""TC-012: Expired or cancelled approval requests cannot be used to perform the protected action."""
from datetime import datetime, timezone
from langgraph.types import Command

def resume_approval(graph, thread_id: str, decision: dict, expiry_time: datetime):
    # DEFECT: Processes approval payload without verifying if the request has expired or been cancelled
    return graph.invoke(Command(resume=decision), config={"configurable": {"thread_id": thread_id}})

