# Graph Compilation and Connectivity in LangGraph

This guide covers graph assembly, compilation, entry and finish configuration, topology reachability, package exports, and version compatibility in LangGraph.

---

## 1. Graph Assembly & Compilation Lifecycle

Graph construction follows a structured lifecycle:

1. **Schema Instantiation**: Create a `StateGraph(StateSchema)`.
2. **Topology Configuration**: Register all node callables (`add_node`) and define edge connections (`add_edge`, `add_conditional_edges`).
3. **Compilation**: Call `.compile()` to validate graph topology and build a `CompiledStateGraph` runnable.

```python
from langgraph.graph import StateGraph, START, END
from my_app.state import WorkflowState
from my_app.nodes import fetch_data, process_data

def build_workflow_graph():
    builder = StateGraph(WorkflowState)
    builder.add_node("fetch", fetch_data)
    builder.add_node("process", process_data)
    
    builder.add_edge(START, "fetch")
    builder.add_edge("fetch", "process")
    builder.add_edge("process", END)
    
    return builder.compile()

workflow = build_workflow_graph()
__all__ = ["workflow", "build_workflow_graph"]
```

---

## 2. Compile-Time vs Runtime Invocation Failures

It is critical to distinguish between graph construction defects and runtime invocation errors:

| Error Type | Detection Point | Examples & Root Causes | Handling |
|---|---|---|---|
| **Compile-Time Error** | Caught during `builder.compile()` | Unknown node in `add_edge`, missing entry point, invalid graph topology | Graph Construction Defect (Modularity / Maintainability) |
| **Runtime Invocation Error** | Caught during `graph.invoke()` | Node body raises unhandled `KeyError`, external database/tool timeout | Node Implementation / Tool / Business Logic Defect |
| **Persistence / Checkpointer** | Caught during state save/resume | Checkpointer serialization error, database lock | State & Persistence Skill |

---

## 3. Package Layout & Export Conventions

LangGraph graphs may be organized in either modular packages or standalone files:

- **Modular Layout**: Clean separation into `state.py`, `nodes/`, `edges.py`, `graph.py`.
- **Single-File Layout**: Lightweight graphs self-contained in a single module (e.g. `workflow.py`).

*False-Positive Guard: Never report an unconventional or single-file package layout as a graph construction defect if the code compiles cleanly and adheres to the host project's architecture.*

---

## 4. Version Compatibility & Verified APIs

Always verify the project's dependency lockfile before recommending APIs:

- **LangGraph 0.2+ / 1.x**:
  - `from langgraph.graph import StateGraph, START, END`
  - `builder.add_edge(START, "first_node")`
  - `builder.add_edge("last_node", END)`
  - `from langgraph.graph import MessagesState`
- **Legacy LangGraph (< 0.2)**:
  - `builder.set_entry_point("first_node")`
  - `builder.set_finish_point("last_node")`
- **Unverified Version**: If dependency metadata is unavailable, note the version uncertainty and prefer standard portable patterns.

---

## 5. Review Checklist & False-Positive Safeguards

- [ ] **False-Positive Guard: Dynamic Reachability**: Do NOT flag a node as unreachable before checking all conditional edge `path_map` targets.
- [ ] **False-Positive Guard: Package Layout**: Do NOT demand a 4-file modular package layout when a single-file graph is intentional and valid.
- [ ] **Genuine Defect: Missing Entry Point**: Does the graph lack an entry edge from `START` (or `set_entry_point`)?
- [ ] **Genuine Defect: Compile-Time Broken Edge**: Does an edge connect to a non-existent or misspelled node name?
