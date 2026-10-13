# State Security & Testing

This reference documents sensitive data minimization, large payload handling, and deterministic unit testing for state transitions, reducers, and checkpoint recovery.

---

## 1. Sensitive Data in State & Checkpoints

Checkpointed graph state is persisted to long-term database storage. Therefore:

1. **No Credentials in State Channels**: Never store raw API keys, bearer tokens, passwords, or cryptographic private keys in graph state channels. Pass credentials via configuration or runtime context (`RunnableConfig`), not state dictionaries.
2. **PII Minimization & Redaction**: Store only pseudonymous identifiers (e.g. `user_id`, `account_id`) in state rather than raw personal identifying information (SSN, credit card numbers).
3. **Log & Checkpoint Sanitization**: Ensure sensitive input fields are filtered or redacted before state serialization.
4. **Encryption at Rest**: Ensure the underlying database tables (e.g. PostgreSQL tables holding checkpoint blobs) have encryption at rest enabled.

---

## 2. Payload Minimization & External Object References

Persisting large raw binaries or multi-megabyte documents in state channels causes severe performance bottlenecks, database bloat, and serialization latency.

### ✅ Recommended Patterns: References & Access Control

| Reference Pattern | Best Suited For | Security Consideration |
|---|---|---|
| **Stable Object ID (`doc_id`)** | Internal microservices, database entities. | Access control is enforced at query time by the downstream service. |
| **Short-Lived Signed URL (`s3_presigned_url`)** | Direct client downloads, temporary artifact access. | Never store permanent signed URLs in durable checkpoints; generate ephemeral URLs just-in-time. |
| **Storage URI (`s3://bucket/path`)** | Durable pipeline processing between nodes. | Access credentials remain outside graph state in IAM / environment config. |

```python
from typing import TypedDict

class DocumentProcessingState(TypedDict):
    doc_id: str
    s3_storage_uri: str          # Reference pointer (e.g. 's3://bucket/docs/123.pdf')
    extracted_text_summary: str  # Compact summarized text (under a few KB)
```

### ❌ Anti-Pattern: Embedding Raw Binaries in State
```python
# VIOLATION: Storing megabytes of raw bytes in graph state channels
class BadState(TypedDict):
    raw_pdf_bytes: bytes         # Inflates DB checkpoint storage and slows every node transition
```

---

## 3. Testing State Transitions & Recovery Deterministically

### A. Testing Custom Reducers in Isolation
```python
# tests/test_reducers.py
from agents.graphs.review.reducers import merge_findings

def test_merge_findings_reducer():
    left = [{"id": "F1", "severity": "low"}]
    right = [{"id": "F2", "severity": "high"}]
    merged = merge_findings(left, right)
    assert len(merged) == 2
    assert {f["id"] for f in merged} == {"F1", "F2"}
```

### B. Testing Checkpoint Restoration with `MemorySaver`
```python
# tests/test_checkpoint_resumption.py
import pytest
from langgraph.checkpoint.memory import MemorySaver
from agents.graphs.workflow import build_workflow_graph

@pytest.mark.asyncio
async def test_resumes_from_checkpoint():
    checkpointer = MemorySaver()
    graph = build_workflow_graph(checkpointer=checkpointer)
    config = {"configurable": {"thread_id": "test_session_1"}}
    
    # Run step 1
    await graph.ainvoke({"input_text": "step 1 query"}, config=config)
    
    # Retrieve checkpointed state
    snapshot = graph.get_state(config)
    assert snapshot.values["input_text"] == "step 1 query"
```


