"""TC-009: Concurrent decisions follow the application's conflict policy."""
from langgraph.types import Command

def handle_concurrent_approval(graph, thread_id: str, decision: dict):
    # DEFECT: Blind invoke without state lock or version check, allowing race conditions between concurrent reviewers
    return graph.invoke(Command(resume=decision), config={"configurable": {"thread_id": thread_id}})

