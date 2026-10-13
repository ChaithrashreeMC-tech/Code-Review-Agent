from langgraph.graph import StateGraph

builder = StateGraph(dict)
# Defect: invalid_api_call with non-existent method set_magic_router
builder.set_magic_router("node_a", "node_b")

