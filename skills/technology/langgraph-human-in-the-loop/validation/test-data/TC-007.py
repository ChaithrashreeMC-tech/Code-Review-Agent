"""TC-007: Cross-tenant execution access is denied when tenant isolation is required."""
from langgraph.types import Command

def resume_tenant_execution(graph, request_tenant_id: str, thread_id: str, decision: dict):
    # DEFECT: Resumes thread without validating that the thread belongs to request_tenant_id
    config = {"configurable": {"thread_id": thread_id}}
    return graph.invoke(Command(resume=decision), config=config)

