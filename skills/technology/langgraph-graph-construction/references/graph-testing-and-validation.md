# Graph Testing and Validation in LangGraph

This guide covers unit and integration testing strategies for LangGraph graphs, focusing on compilation verification, deterministic state transitions, branch coverage, loop termination boundaries, and state contract validation.

---

## 1. Principles of Deterministic Graph Testing

1. **Deterministic Test Nodes**: In unit tests, replace live LLMs, API clients, and database queries with stubbed/deterministic node functions that return predictable state dictionaries.
2. **Compile-Time vs Run-Time Testing**:
   - Verify that `builder.compile()` succeeds without topology errors.
   - Verify that `graph.invoke(mock_state)` yields the expected state transformations.
3. **Exhaustive Branch Coverage**: Supply mock input states to exercise every destination in conditional edge `path_map` dictionaries.

---

## 2. Unit Testing Patterns

### A. Graph Compilation & Structure Test
```python
import pytest
from my_app.graph import build_workflow_graph

def test_graph_compilation_and_nodes():
    """Verify graph compiles cleanly and registers all required nodes."""
    graph = build_workflow_graph()
    assert graph is not None
    assert "fetch" in graph.nodes
    assert "process" in graph.nodes
```

### B. Conditional Route Coverage Test
```python
def test_conditional_routing_branches():
    """Test every conditional branch with deterministic input state."""
    graph = build_workflow_graph()
    
    # Test branch 1: Valid review
    pass_result = graph.invoke({"code_diff": "clean code", "has_violations": False})
    assert pass_result["status"] == "approved"
    
    # Test branch 2: Violations present
    fail_result = graph.invoke({"code_diff": "bad code", "has_violations": True, "retry_count": 0})
    assert fail_result["status"] == "remediated"
```

### C. Bounded Loop Termination Test
```python
def test_loop_terminates_at_max_retries():
    """Ensure cyclic workflows do not loop infinitely and exit at the defined boundary."""
    graph = build_workflow_graph()
    
    # Supply state at maximum retry threshold
    state_at_limit = {"retry_count": 3, "has_violations": True}
    result = graph.invoke(state_at_limit)
    
    # Assert loop terminated at the fallback/escalate node
    assert result["status"] == "escalated"
```

### D. Parallel Reducer Merge Test
```python
def test_concurrent_reducer_aggregation():
    """Verify parallel branch updates are merged by reducers without collision."""
    graph = build_fanout_graph()
    initial_state = {"findings": []}
    
    result = graph.invoke(initial_state)
    
    # Ensure findings from both parallel branches were accumulated
    assert len(result["findings"]) == 2
```

---

## 3. Review Checklist for Graph Tests

- [ ] **Deterministic Stubs**: Are graph tests free of unmocked external LLM calls and network operations?
- [ ] **Full Route Coverage**: Are all keys in conditional `path_map` dictionaries exercised by test cases?
- [ ] **Loop Boundary Checks**: Are loop termination conditions tested with boundary inputs?
- [ ] **State Schema Assertions**: Do tests assert that the final returned dictionary conforms to the declared state schema?
