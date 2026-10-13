"""TC-010: Interrupted execution can recover after restart when durability is required."""
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph

builder = StateGraph(dict)
# DEFECT: Production service requiring durable multi-instance recovery compiled with in-memory MemorySaver
app = builder.compile(checkpointer=MemorySaver())

