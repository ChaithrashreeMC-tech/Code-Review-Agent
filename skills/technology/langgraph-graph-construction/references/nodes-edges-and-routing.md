# Nodes, Edges, and Routing in LangGraph

This guide covers node contracts, linear and conditional edge construction, destination path maps, cycle safety, and routing defect detection in LangGraph.

---

## 1. Node Function Contracts

A LangGraph node is a callable that receives the current graph state (and optional `RunnableConfig`) and returns a partial state update dictionary:

```python
from typing import Any, Dict
from langchain_core.runnables import RunnableConfig

def analyze_node(state: Dict[str, Any], config: RunnableConfig = None) -> Dict[str, Any]:
    # Read state safely
    diff = state.get("code_diff", "")
    # Perform node logic
    result = {"status": "analyzed", "findings": ["SEC02: Hardcoded secret"]}
    # Return partial update dictionary
    return result
```

---

## 2. Registering Nodes & Connecting Edges

### A. Node Registration
Nodes are registered with unique string identifiers:
```python
from langgraph.graph import StateGraph, START, END

builder = StateGraph(AgentState)
builder.add_node("analyze", analyze_node)
builder.add_node("remediate", remediate_node)
builder.add_node("report", report_node)
```

### B. Linear Edges
Connect sequential nodes directly:
```python
builder.add_edge(START, "analyze")
builder.add_edge("remediate", "report")
builder.add_edge("report", END)
```

### C. Conditional Routing & Path Maps
Route functions inspect state and return a routing label. An explicit `path_map` maps returned strings to registered destination nodes or `END`:

```python
def route_review(state: AgentState) -> str:
    if state.get("retry_count", 0) >= 3:
        return "escalate"
    if state.get("has_violations", False):
        return "fix"
    return "pass"

builder.add_conditional_edges(
    "analyze",
    route_review,
    {
        "fix": "remediate",
        "escalate": "report",
        "pass": "report"
    }
)
```

---

## 3. Parallel Branching, Convergence & Cycles

1. **Parallel Fan-Out & Fan-In**:
   ```python
   # Fan-out: Single source triggers parallel execution
   builder.add_edge(START, "security_check")
   builder.add_edge(START, "performance_check")
   
   # Fan-in: Convergence on aggregator node
   builder.add_edge("security_check", "aggregator")
   builder.add_edge("performance_check", "aggregator")
   ```
2. **Bounded Cycles vs Unbounded Loops**:
   - **Valid Bounded Cycle**: Node loop includes an iteration counter increment or state status transition that guarantees exit (e.g. `state["retry_count"] >= 3 -> END`).
   - **Defective Unbounded Loop**: Route always directs back to the source node without modifying state or evaluating a maximum iteration limit.

---

## 4. Valid vs Defective Routing Examples

###  Valid: Bounded Loop with Exit Safeguard
```python
def step_node(state: LoopState) -> dict:
    return {"retry_count": state["retry_count"] + 1}

def route_fn(state: LoopState) -> str:
    if state["retry_count"] >= 3:
        return "done"
    return "retry"

builder.add_conditional_edges("step", route_fn, {"retry": "step", "done": "finalize"})
```

### ❌ Defective: Unmapped Route Destination & Unregistered Node Reference
```python
def bad_route(state: BadState) -> str:
    return "unexpected_label"  # DEFECT: Label not in path_map

builder.add_conditional_edges(
    "step",
    bad_route,
    {"valid_label": "nonexistent_node"}  # DEFECT: 'nonexistent_node' never added via add_node
)
```

---

## 5. Review Checklist & False-Positive Safeguards

- [ ] **False-Positive Guard: Bounded Cycles**: Do NOT flag a cycle as an infinite loop if state counters, error thresholds, or status transitions ensure loop termination.
- [ ] **False-Positive Guard: Conditional Reachability**: Do NOT flag a node as missing an incoming edge if a conditional edge's `path_map` targets it.
- [ ] **Genuine Defect: Unmapped Return Value**: Can the route function return a string not present in the conditional edge's `path_map`?
- [ ] **Genuine Defect: Unregistered Destination**: Does `add_edge` or `path_map` reference a node name that was never registered with `add_node`?
- [ ] **Genuine Defect: Nonterminating Cycle**: Does a cyclic edge lack any termination condition or loop counter?
