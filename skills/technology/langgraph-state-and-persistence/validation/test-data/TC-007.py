def restore_state_unsafe(user_id: str, thread_id: str):
    # Defect: unauthorized_thread_access due to missing_ownership_check
    config = {"configurable": {"thread_id": thread_id}}
    return graph.get_state(config)

