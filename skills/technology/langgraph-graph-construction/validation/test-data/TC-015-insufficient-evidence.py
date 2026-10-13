"""
TC-015: Potential Concern with Insufficient Evidence.
Review context has incomplete source for dynamic plugin router.
Skill must record uncertainty rather than inventing a confirmed defect.
"""
from typing import TypedDict, Any
from langgraph.graph import StateGraph, START, END

class PluginState(TypedDict):
    input_val: str

def base_node(state: PluginState) -> dict:
    return {}

def external_plugin_router(state: PluginState, runtime_registry: Any = None) -> str:
    # Target destinations depend on external runtime registry not visible in this diff
    if runtime_registry:
        return runtime_registry.resolve_target(state)
    return "default_target"

def default_target(state: PluginState) -> dict:
    return {}

def build_plugin_graph(runtime_registry: Any = None):
    builder = StateGraph(PluginState)
    builder.add_node("base", base_node)
    builder.add_node("default_target", default_target)
    
    builder.add_edge(START, "base")
    builder.add_conditional_edges("base", lambda s: external_plugin_router(s, runtime_registry))
    builder.add_edge("default_target", END)
    return builder.compile()

