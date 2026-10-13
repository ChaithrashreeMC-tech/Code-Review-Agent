"""TC-004: Tool-call results not being associated with the correct invocation."""
from langchain_core.messages import ToolMessage

def custom_tool_executor_node(state):
    last_message = state["messages"][-1]
    results = []
    for call in last_message.tool_calls:
        res = execute_tool(call["name"], call["args"])
        # DEFECT: Missing tool_call_id association causes downstream API rejection
        results.append(ToolMessage(content=str(res), tool_call_id=""))
    return {"messages": results}

