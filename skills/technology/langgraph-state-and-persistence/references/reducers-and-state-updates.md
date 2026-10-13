# Reducers & State Updates

This reference documents state update semantics, channel reducers, partial state returns, avoiding harmful mutations, and handling parallel branch writes.

---

## 1. State Update Semantics in LangGraph

By default, when a node returns a dictionary `{"key": new_value}`, LangGraph performs a **direct key replacement/overwrite**:
- `state[key] = new_value`

When multiple nodes update the same key, or when a channel needs list accumulation or custom merging, use `typing.Annotated` with a reducer function.

---

## 2. Reducer Selection Rules

| Channel Type | Recommended Reducer | Mechanism | Notes |
|---|---|---|---|
| **Scalar / Status / Single-Writer** | Default (No Reducer) | Direct Overwrite | Do NOT add reducers to fields meant to hold the latest single value (e.g. `status`, `current_step`). |
| **Ordered Event / Audit List** | `Annotated[list[T], operator.add]` | List Concatenation | Appends items returned by nodes into the existing list. |
| **Chat / Message History** | `Annotated[Sequence[BaseMessage], add_messages]` | ID-Aware Message Merge | Appends new messages, updates messages with matching IDs, supports deletion. |
| **Dictionary Merging / Conflict Resolution** | `Annotated[dict, custom_merge_fn]` | Custom Immutably Merged Dict | Combines keys or resolves conflicting updates deterministically. |

---

## 3. Reducer Types & Usage Patterns

### A. List Accumulation (`operator.add`)
For standard lists where each node appends new items:

```python
import operator
from typing import Annotated, List, TypedDict

class PipelineState(TypedDict):
    task_id: str
    audit_log: Annotated[List[str], operator.add]
```

### B. Message History (`add_messages`)
For conversational chat histories where messages may be appended, updated by ID, or overwritten:

```python
from typing import Annotated, Sequence
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from typing import TypedDict

class ChatState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
```

### C. Custom Merge Reducer (Dictionary/Set Merging)
For merging dictionaries or resolving conflict priorities:

```python
from typing import Annotated, Dict, Any, TypedDict

def merge_metadata(left: Dict[str, Any], right: Dict[str, Any]) -> Dict[str, Any]:
    """Custom reducer combining metadata dictionaries immutably."""
    merged = left.copy() if left else {}
    if right:
        merged.update(right)
    return merged

class DocumentState(TypedDict):
    doc_id: str
    metadata: Annotated[Dict[str, Any], merge_metadata]
```

---

## 4. Partial Returns vs. In-Place Mutations

### ✅ Correct Pattern: Returning Partial Dictionaries
Nodes should read state immutably and return **only** the keys they update:

```python
def classify_intent_node(state: WorkflowState) -> dict:
    # Read state immutably
    query = state["user_query"]
    intent = "billing" if "invoice" in query.lower() else "general"
    
    # Return partial update dictionary
    return {"assigned_intent": intent}
```

### ❌ Mutation Defect vs. Safe Modification
> **Evidence Rule for In-Place Mutation Defects:**
> Modifying mutable objects in-place (`state["list"].append(...)`) is a defect **only when**:
> 1. It bypasses LangGraph channel tracking (returning an empty `{}` or omitting the key), causing checkpoints or subsequent nodes to miss the update.
> 2. It causes aliasing bugs across concurrent parallel branches or checkpoint rollbacks.
>
> If a node locally modifies a copied data structure and returns it in the update dict (`{"list": modified_copy}`), it is safe and compliant.

```python
def bad_node_mutating_in_place(state: WorkflowState) -> dict:
    # VIOLATION: Directly mutating shared state list in-place and returning empty dict
    state["audit_log"].append("processed_by_node")
    state["metadata"]["processed"] = True
    
    # LangGraph is unaware of internal object mutations; checkpoints and rollbacks will desynchronize
    return {}
```

---

## 5. Parallel Branch Writes & Fan-Out Conflicts

When a graph branches concurrently (fan-out), two nodes executing in parallel within the same superstep cannot write to the same channel unless that channel has an `Annotated` reducer.

- **Without Reducer**: LangGraph raises `InvalidUpdateError` due to conflicting concurrent writes to a single-writer channel.
- **With Reducer**: LangGraph passes each branch output sequentially to the reducer function to produce the merged state.


