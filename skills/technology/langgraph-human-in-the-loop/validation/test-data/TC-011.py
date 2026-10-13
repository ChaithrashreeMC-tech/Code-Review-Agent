"""TC-011: Missing or expired checkpoints are handled explicitly."""
from langgraph.types import Command

def resume_task(graph, thread_id: str, decision: dict):
    # DEFECT: Fails to check graph.get_state() or handle missing/expired checkpoint prior to resumption
    state = graph.get_state({"configurable": {"thread_id": thread_id}})
    current_val = state.values["critical_data"]  # Raises unhandled KeyError/AttributeError if state is empty/expired
    return graph.invoke(Command(resume=decision), config={"configurable": {"thread_id": thread_id}})

