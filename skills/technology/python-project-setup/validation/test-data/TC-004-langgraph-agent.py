# TC-004: LangGraph Agent Application Fixture
# Recognizes graph.py, state.py, nodes/, tools/

LANGGRAPH_CODE = """
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END

class AgentState(TypedDict):
    messages: list[str]
    current_step: str

workflow = StateGraph(AgentState)
"""

class LangGraphDetector:
    def __init__(self, file_tree: list[str]):
        self.file_tree = file_tree

    def is_langgraph_agent(self) -> bool:
        return "src/agent/graph.py" in self.file_tree and "src/agent/state.py" in self.file_tree

