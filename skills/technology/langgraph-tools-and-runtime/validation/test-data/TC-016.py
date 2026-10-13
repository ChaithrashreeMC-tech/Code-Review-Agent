"""TC-016: False positive where a direct graph node is appropriate and no ToolNode is required."""
from langgraph.graph import StateGraph, START, END

async def deterministic_document_parsing_node(state):
    # Direct service call in deterministic pipeline without ToolNode
    parsed_data = await document_parser_service.parse(state["raw_text"])
    return {"parsed_document": parsed_data}

builder = StateGraph(dict)
builder.add_node("parser", deterministic_document_parsing_node)
builder.add_edge(START, "parser")
builder.add_edge("parser", END)
# COMPLIANT: Deterministic pipeline appropriately uses direct node instead of ToolNode (False Positive Guard)

