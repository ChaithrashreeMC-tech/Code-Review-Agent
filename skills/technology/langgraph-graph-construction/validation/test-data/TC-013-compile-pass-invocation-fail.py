"""
TC-013: Graph Compiles Successfully but Fails at Invocation Time.
Defect: Topology compiles cleanly, but downstream node assumes 'required_metadata' exists in state
without upstream initialization, raising KeyError on invocation.
"""
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class RuntimeFailState(TypedDict):
    input_text: str
    required_metadata: dict
    output: str

def producer_node(state: RuntimeFailState) -> dict:
    # Only sets output, does NOT initialize required_metadata
    return {"output": "in_progress"}

def consumer_node(state: RuntimeFailState) -> dict:
    # DEFECT: Direct access to state["required_metadata"] raises KeyError on invocation
    user_id = state["required_metadata"]["user_id"]
    return {"output": f"processed for {user_id}"}

def build_runtime_fail_graph():
    builder = StateGraph(RuntimeFailState)
    builder.add_node("producer", producer_node)
    builder.add_node("consumer", consumer_node)
    
    # Compiles fine because topology and node registrations are valid
    builder.add_edge(START, "producer")
    builder.add_edge("producer", "consumer")
    builder.add_edge("consumer", END)
    
    return builder.compile()

