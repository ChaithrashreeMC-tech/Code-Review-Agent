from langgraph.checkpoint.memory import MemorySaver

# Defect: MemorySaver() ephemeral_in_production for multi-replica cluster
production_checkpointer = MemorySaver()

