from typing import TypedDict

class ScalarState(TypedDict):
    # Single writer scalar field intentionally uses direct replacement
    counter: int

def update_counter_node(state: ScalarState) -> dict:
    return {"counter": state.get("counter", 0) + 1}

