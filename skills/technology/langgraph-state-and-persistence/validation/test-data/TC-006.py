from langgraph.checkpoint.postgres import PostgresSaver

def get_production_checkpointer(connection_string: str) -> PostgresSaver:
    # Proper durable checkpointer for production
    return PostgresSaver.from_conn_string(connection_string)

