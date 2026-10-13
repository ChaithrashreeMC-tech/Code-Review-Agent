def auth_node(state: dict) -> dict:
    # Defect: api_key_in_state storing sk-proj-secret-key in graph state
    return {"api_key_in_state": "sk-proj-secret-key-12345"}

