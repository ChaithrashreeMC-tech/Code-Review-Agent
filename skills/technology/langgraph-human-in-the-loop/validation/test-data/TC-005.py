"""TC-005: Resume targets the correct execution and checkpoint."""
from langgraph.types import Command

async def handle_resume_service(thread_id: str, decision: dict, graph):
    # COMPLIANT: Explicitly targets specific thread configuration with validated Command
    config = {"configurable": {"thread_id": f"verified_thread_{thread_id}"}}
    return await graph.ainvoke(Command(resume=decision), config=config)

