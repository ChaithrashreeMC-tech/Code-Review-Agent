"""TC-018: Workflow not requiring durable resumption not automatically flagged for lacking persistent checkpointer."""
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph

# Unit test / CLI script that does not require persistent multi-node resumption
builder = StateGraph(dict)
checkpointer = MemorySaver()
app = builder.compile(checkpointer=checkpointer)
# COMPLIANT: Ephemeral test utility where MemorySaver is appropriate

