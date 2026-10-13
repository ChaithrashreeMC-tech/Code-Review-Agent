from langgraph.graph import StateGraph, START

def loop_node(state: dict) -> dict:
    return {"counter": state.get("counter", 0) + 1}

def forever_router(state: dict) -> str:
    # Defect: unbounded_loop without termination condition and missing_recursion_limit
    return "loop"

builder = StateGraph(dict)
builder.add_node("loop", loop_node)
builder.add_edge(START, "loop")
builder.add_conditional_edges("loop", forever_router, {"loop": "loop"})
compiled = builder.compile()

