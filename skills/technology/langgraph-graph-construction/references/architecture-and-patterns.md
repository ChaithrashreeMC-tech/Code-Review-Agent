# LangGraph Graph Construction: Architecture & Patterns

This reference document details state schema design, reducer mechanics, node and edge routing, compilation rules, and validation testing for LangGraph state graphs.

---

## 1. State Schemas and Reducers

State definitions should be explicit TypedDict or Pydantic classes:

```python
from typing import Annotated, Optional
from operator import add
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class GraphState(TypedDict):
    # Field replaced on update
    query: str
    status: str
    
    # Reducers for appending/aggregating
    messages: Annotated[list[BaseMessage], add_messages]
    findings: Annotated[list[dict], add]
    retry_count: Annotated[int, lambda a, b: a + b]
```

### Pure Reducer Function Example
```python
def merge_unique_strings(existing: list[str], new_items: list[str]) -> list[str]:
    """Pure reducer that merges two lists without mutating the accumulator."""
    return list(dict.fromkeys(existing + new_items))
```

---

## 2. Nodes, Edges, and Routing

### A. Pure Node Functions
Nodes receive state and return partial updates:
```python
def analyze_node(state: GraphState) -> dict:
    new_findings = [{"rule": "SEC01", "severity": "high"}]
    return {
        "findings": new_findings,
        "status": "ANALYZED"
    }
```

### B. Conditional Edges & Routing Maps
```python
def routing_decision(state: GraphState) -> str:
    if state.get("status") == "ERROR":
        return "error_handler"
    if len(state.get("findings", [])) > 0:
        return "report_generator"
    return "end_clean"

builder.add_conditional_edges(
    "analyze_node",
    routing_decision,
    {
        "error_handler": "error_handler_node",
        "report_generator": "report_generator_node",
        "end_clean": END
    }
)
```

### C. Dynamic Routing with `Command`
```python
from langgraph.types import Command
from langgraph.graph import END

def review_step(state: GraphState) -> Command[str]:
    if state["retry_count"] > 3:
        return Command(goto=END, update={"status": "ABORTED"})
    return Command(goto="next_step", update={"retry_count": 1})
```

---

## 3. Graph Assembly & Compilation

Assemble nodes and edges into a `StateGraph`:

```python
from langgraph.graph import StateGraph, START, END

builder = StateGraph(GraphState)

# Add Nodes
builder.add_node("analyze_node", analyze_node)
builder.add_node("report_generator_node", report_generator_node)
builder.add_node("error_handler_node", error_handler_node)

# Add Static Edges
builder.add_edge(START, "analyze_node")
builder.add_edge("report_generator_node", END)
builder.add_edge("error_handler_node", END)

# Compile
app = builder.compile()
```

---

## 4. Graph Testing & Topological Verification

Unit test graph connectivity and routing logic deterministically:

```python
def test_routing_decision():
    state_with_error = {"status": "ERROR", "findings": []}
    assert routing_decision(state_with_error) == "error_handler"
    
    state_clean = {"status": "SUCCESS", "findings": []}
    assert routing_decision(state_clean) == "end_clean"

def test_graph_compilation():
    compiled = builder.compile()
    assert compiled is not None
```

