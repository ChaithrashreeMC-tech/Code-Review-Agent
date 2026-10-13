"""TC-002: A model requesting a tool that is not registered."""
from langgraph.prebuilt import ToolNode
from langchain_core.messages import AIMessage

# Registered tools list only contains search
registered_tools = [search_tool]
tool_node = ToolNode(registered_tools)

# Model hallucinates and requests unhandled 'execute_raw_code' tool
message = AIMessage(
    content="",
    tool_calls=[{"name": "execute_raw_code", "args": {"code": "rm -rf /"}, "id": "call_123"}]
)
# DEFECT: Unregistered tool request crashes execution without fallback or descriptive ToolMessage

