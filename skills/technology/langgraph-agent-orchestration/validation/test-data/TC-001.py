from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class AgentState(TypedDict):
    input: str
    output: str

def agent_node(state: AgentState) -> dict:
    return {"output": f"Processed: {state['input']}"}

builder = StateGraph(AgentState)
builder.add_node("agent", agent_node)
builder.add_edge(START, "agent")
builder.add_edge("agent", END)

compiled_graph = builder.compile()

