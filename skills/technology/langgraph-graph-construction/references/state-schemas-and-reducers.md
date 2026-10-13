# State Schemas and Reducers in LangGraph

This guide covers state schema definition, update semantics, channel reducers, intentional replacements versus merges, and state defect detection in LangGraph.

---

## 1. Supported State Schema Patterns

LangGraph supports `TypedDict`, `dataclass`, or Pydantic `BaseModel` for graph state. Follow the existing repository's conventions and verified LangGraph version.

### A. `TypedDict` State (Standard & Recommended)
```python
from typing import TypedDict, Annotated, List, Optional
import operator
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    # Overwrite Channels: Subsequent node writes intentionally replace previous values
    query: str
    current_step: str
    retry_count: int
    last_error: Optional[str]
    
    # Reducer Channels: Node updates are merged/appended using reducer functions
    messages: Annotated[List[BaseMessage], add_messages]
    logs: Annotated[List[str], operator.add]
    intermediate_artifacts: Annotated[List[dict], operator.add]
```

### B. Pydantic `BaseModel` State (When Validation is Required)
```python
from pydantic import BaseModel, Field
from typing import Annotated, List
import operator

class ValidatedState(BaseModel):
    query: str = Field(..., description="User prompt")
    step_count: int = Field(default=0)
    history: Annotated[List[str], operator.add] = Field(default_factory=list)
```

---

## 2. Partial State Updates & Update Semantics

1. **Partial Dictionary Return**: Nodes return a dictionary containing **only modified keys**:
   ```python
   def increment_step(state: AgentState) -> dict:
       # Return ONLY updated fields; do NOT copy and return the entire state dict
       return {"current_step": "verification", "retry_count": state["retry_count"] + 1}
   ```
2. **Replacement vs Reducer Semantics**:
   - **Replacement (Default)**: For scalar fields (`status`, `retry_count`, `active_agent`), nodes return the new value and LangGraph overwrites the channel. This is standard and valid.
   - **Reducer Merges (`Annotated[T, reducer_fn]`)**: Required when multiple node outputs should accumulate (e.g. appending messages or merging lists).
3. **Concurrent Fan-Out Updates**:
   - When parallel branches execute simultaneously and write to the same field, that field **MUST** have an `Annotated` reducer configured.
   - If parallel branches write to an unreduced channel, LangGraph raises `InvalidUpdateError`.

---

## 3. Valid vs Defective Code Examples

###  Valid: Intentional Replacement & Safe Parallel Reducer
```python
class ValidReviewState(TypedDict):
    status: str                                     # Overwrite is intentional
    findings: Annotated[List[str], operator.add]     # Parallel fan-in merge

def sec_node(state: ValidReviewState) -> dict:
    return {"findings": ["SEC01: SQL injection detected"]}

def perf_node(state: ValidReviewState) -> dict:
    return {"findings": ["PERF01: N+1 query detected"]}
```

### ❌ Defective: Unreduced Concurrent Channel Write
```python
class DefectiveState(TypedDict):
    # DEFECT: Missing Annotated[List[str], operator.add]
    findings: List[str]

# Parallel branches sec_node and perf_node writing to 'findings' concurrently
# will crash with InvalidUpdateError in LangGraph!
```

---

## 4. Review Checklist & False-Positive Safeguards

- [ ] **False-Positive Guard: Intentional Overwrites**: Do NOT flag scalar fields (`status`, `query`, `counter`) lacking reducers as bugs if replacement is the intended design.
- [ ] **Genuine Defect: Concurrent Unreduced Channel**: Do parallel branches write to the same list/dict key without an `Annotated` reducer?
- [ ] **Genuine Defect: In-Place Mutation**: Does a node mutate input state directly (e.g. `state["logs"].append(...)`) instead of returning `{"logs": [...]}`?
- [ ] **Genuine Defect: Type Mismatch**: Does a node return a value whose type contradicts the schema (e.g. returning `int` for a `List[str]` field)?
