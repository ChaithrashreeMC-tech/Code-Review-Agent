# LangGraph Graph Construction Review Checklist

This checklist defines concrete review rules (`GRAPH01`–`GRAPH10`), detection patterns, good/bad code examples, and remediation guidance for assembling, compiling, and validating LangGraph state graphs.

---

## Rule Index

| ID | Rule Name | Objective |
|---|---|---|
| `GRAPH01` | Explicit State Schema Definition | Define graph state with explicit `TypedDict` or `BaseModel` annotations; forbid untyped `dict`. |
| `GRAPH02` | Pure and Associative Reducers | Use pure reducer functions (`operator.add`) without in-place list/dict mutations. |
| `GRAPH03` | Graph Topology Completeness | Ensure every node is reachable from `START` and has at least one valid path reaching `END`. |
| `GRAPH04` | Exhaustive Conditional Routing | Ensure conditional edge functions cover all possible return branches with explicit path maps. |
| `GRAPH05` | Dynamic Branching via `Command` | Ensure `Command(goto=...)` references declared graph node names or `END`. |
| `GRAPH06` | Safe Graph Compilation | Compile state graphs explicitly (`builder.compile()`) and validate graph structure before deployment. |
| `GRAPH07` | Parallel Execution Safety | Ensure parallel branches write to disjoint state keys or fields managed by associative reducers. |
| `GRAPH08` | State Immutability in Nodes | Return dictionary state diffs from node functions; never mutate input `state` in-place. |
| `GRAPH09` | Subgraph Boundary Encapsulation | Encapsulate subgraphs with explicit input/output schemas; avoid leaky state dependencies. |
| `GRAPH10` | Deterministic Graph Unit Testing | Test individual nodes and full graph topologies in unit tests without live external services. |

---

## Detailed Rule Checklist

### GRAPH01: Explicit State Schema Definition
- [ ] State schemas inherit from `TypedDict` or Pydantic `BaseModel`.
- [ ] All state fields have explicit type annotations.
- ❌ **Anti-pattern:** `builder = StateGraph(dict)` with nodes arbitrarily adding untyped keys.
- ✅ **Remediation:** Define `class ReviewState(TypedDict): diff: str; findings: list[str]` and pass to `StateGraph(ReviewState)`.

### GRAPH02: Pure and Associative Reducers
- [ ] Reducers used in `Annotated[T, reducer]` are pure functions (e.g. `operator.add`).
- [ ] Reducers never mutate existing accumulator arguments in-place.
- ❌ **Anti-pattern:** `def bad_reducer(a, b): a.extend(b); return a`.
- ✅ **Remediation:** `def safe_reducer(a, b): return list(a) + list(b)`.

### GRAPH03: Graph Topology Completeness
- [ ] `START` edge connects to an initial processing node.
- [ ] No orphaned / unreachable nodes exist in the graph.
- [ ] Every valid execution branch reaches `END`.
- ❌ **Anti-pattern:** `builder.add_node("orphan_node", ...)` with no edges connected to or from it.
- ✅ **Remediation:** Connect all nodes with `add_edge()` or conditional edges to ensure reachability.

### GRAPH04: Exhaustive Conditional Routing
- [ ] Conditional edge routing functions return only keys declared in the `path_map`.
- [ ] Default fallback branch is provided for unexpected outputs.
- ❌ **Anti-pattern:** `builder.add_conditional_edges("router", route_fn, {"approved": "payout"})` when `route_fn` can return `"rejected"`.
- ✅ **Remediation:** Provide exhaustive mapping: `{"approved": "payout", "rejected": END, "unknown": "fallback"}`.

### GRAPH05: Dynamic Branching via `Command`
- [ ] Nodes returning `Command(goto="target_node")` specify valid registered node names or `END`.
- ❌ **Anti-pattern:** `return Command(goto="non_existent_node")`.
- ✅ **Remediation:** Ensure target node string is registered in `builder.add_node()`.

### GRAPH06: Safe Graph Compilation
- [ ] Call `app = builder.compile()` with appropriate checkpointer or interrupts.
- [ ] Catch compilation validation errors (`InvalidUpdateError`, `GraphRecursionError`) during build/test.
- ❌ **Anti-pattern:** Attempting to invoke uncompiled `StateGraph` builder directly.
- ✅ **Remediation:** Call `builder.compile()` and expose the compiled `CompiledGraph` instance.

### GRAPH07: Parallel Execution Safety
- [ ] Concurrent nodes writing to the same state key must use `Annotated[..., reducer]`.
- ❌ **Anti-pattern:** Two parallel nodes returning `{"counter": 1}` where `counter: int` has no reducer (last write wins non-deterministically).
- ✅ **Remediation:** Use `Annotated[int, operator.add]` or write to separate keys: `{"node_a_counter": 1}`.

### GRAPH08: State Immutability in Nodes
- [ ] Nodes return a dictionary with only the updated fields (partial state update).
- [ ] Do not execute `state["items"].append(new_item)` inside node body.
- ❌ **Anti-pattern:** Mutating `state` parameter directly in place.
- ✅ **Remediation:** Return `{"items": [new_item]}` with `Annotated[list, operator.add]`.

### GRAPH09: Subgraph Boundary Encapsulation
- [ ] Subgraphs declare clean input and output schemas.
- [ ] Parent graphs pass only necessary state fields to subgraphs.
- ❌ **Anti-pattern:** Subgraphs reading and mutating unrelated parent state keys.
- ✅ **Remediation:** Add subgraph as node: `builder.add_node("subgraph", sub_app)`.

### GRAPH10: Deterministic Graph Unit Testing
- [ ] Graph execution paths are verified using isolated state payloads in pytest fixtures.
- ❌ **Anti-pattern:** Skipping graph connectivity tests or relying on end-to-end integration tests only.
- ✅ **Remediation:** Write unit tests for each conditional edge function and compile-time validation.

