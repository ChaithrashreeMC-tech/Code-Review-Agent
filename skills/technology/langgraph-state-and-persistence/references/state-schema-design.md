# State Schema Design & Typing

This reference provides guidance on designing, typing, initializing, and evolving LangGraph state schemas in Python.

---

## 1. Schema Definition Strategies

LangGraph supports `TypedDict`, Pydantic `BaseModel`, and Python `dataclasses` for graph state schemas.

| Schema Type | Best Suited For | Advantages | Considerations |
|---|---|---|---|
| **`TypedDict`** | Default for most LangGraph workflows. | Native dictionary syntax, fast serialization, zero runtime validation overhead. | Keys must be validated upstream or via typing tools; no default runtime instantiation without helpers. |
| **Pydantic `BaseModel`** | Complex domain validation, strict data coercion. | Automatic field validation, default values, built-in serialization helpers. | Slight performance overhead per node invocation; partial updates must adhere to model shapes. |
| **`dataclass`** | Object-oriented workflows requiring class methods. | Clean class syntax with type annotations. | Requires custom serialization setup or converters with some checkpointers. |

---

## 2. Typing Best Practices & Channel Contracts

### A. Required vs. Optional Fields (`NotRequired` vs `Optional`)
- **`Optional[T]`**: The key **must exist** in the dictionary, but its value may be `None`.
- **`NotRequired[T]`** (`typing_extensions` / Python 3.11+): The key **may be completely omitted** from the dictionary during initialization or partial updates.

```python
from typing import TypedDict, Optional, List
from typing_extensions import NotRequired

class WorkflowState(TypedDict):
    # Required at graph invocation startup
    session_id: str
    user_query: str
    
    # Optional value (key exists, value can be None)
    assigned_analyst: Optional[str]
    
    # Not required at startup (populated downstream by intermediate nodes)
    analysis_results: NotRequired[List[dict]]
    error_summary: NotRequired[str]
```

### B. Separate Input, Internal, and Output Schemas
When a graph's public caller should provide only a subset of fields, or only receive a clean subset of output fields, use separate schemas in `StateGraph`:

```python
from langgraph.graph import StateGraph
from typing import TypedDict

class WorkflowInput(TypedDict):
    user_query: str

class WorkflowInternal(TypedDict):
    user_query: str
    raw_documents: list[str]
    internal_scores: dict[str, float]
    final_answer: str

class WorkflowOutput(TypedDict):
    final_answer: str

# Compile with input and output schemas
builder = StateGraph(WorkflowInternal, input=WorkflowInput, output=WorkflowOutput)
```

> **False-Positive Safeguard:** Do NOT mandate separate input and output schemas when the external caller and the graph operate on the identical state contract.

---

## 3. The Three Dimensions of Versioning

When designing and maintaining LangGraph workflows, keep three distinct version concepts separate:

1. **Application State Schema Version**:
   - The application-defined contract (`schema_version: int = 1`).
   - Represents the shape of the business payload stored in channels.
2. **LangGraph Framework Version**:
   - The installed Python package version (e.g., `langgraph>=0.2.0`).
   - Dictates framework APIs (`StateGraph`, `add_messages`, `BaseCheckpointSaver`).
3. **Persistence Backend Storage Schema Version**:
   - The database DDL tables/indexes managed by persistence libraries (e.g. `langgraph-checkpoint-postgres` schema tables `checkpoints`, `checkpoint_blobs`, `checkpoint_writes`).

---

## 4. Schema Evolution & Deployment Compatibility

When persistent checkpoints outlive application deployments (such as multi-day Human-In-The-Loop sessions or long-running workflows):

1. **Forward/Backward Field Compatibility**:
   - Never remove or rename existing persisted fields without a migration strategy or default fallback in `state.get("field", default)`.
   - New fields added to state schemas must be marked as `NotRequired` or provide a default value to prevent deserialization errors on legacy checkpoints.
2. **Explicit Schema Versioning & Normalization**:
   - For long-lived durable workflows, include a `schema_version: int = 1` field in the state.
   - When loading older checkpoints, execute a normalization migration function if `checkpoint.schema_version < CURRENT_SCHEMA_VERSION`.

```python
def migrate_legacy_checkpoint(raw_state: dict) -> dict:
    """Normalize legacy checkpoint state to latest schema version."""
    state = raw_state.copy()
    version = state.get("schema_version", 1)
    
    if version < 2:
        # Schema v2 added required structured metadata
        state["metadata"] = state.get("metadata", {"source": "legacy_v1"})
        state["schema_version"] = 2
        
    return state
```


