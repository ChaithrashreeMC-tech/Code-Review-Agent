# Orchestration Testing & Runtime Guardrails

This reference documents the patterns for enforcing orchestration guardrails (recursion limits, timeouts, token budgets, evidence integrity) and testing agent workflows deterministically.

---

## 1. Orchestration Guardrails (Mandatory Enforcement)

Guardrails must be enforced using concrete runtime mechanisms, not passive comments or docstrings:

| Guardrail | Enforcement Mechanism | Implementation Boundary |
|---|---|---|
| **Recursion / Step Limit** | Pass `{"recursion_limit": N}` in `config` on `ainvoke`/`astream`. | Invocations in `agents/services/[feature].py`. |
| **Execution Timeout** | Wrap graph execution in `asyncio.wait_for(..., timeout=T)`. | Seam service (`agents/services/[feature].py`). |
| **Token / Cost Budget** | Running token counter in graph state, checked before model calls. | Node functions or supervisor router. |
| **Handoff Validation** | Validate inter-node payloads against Pydantic models. | Routing edges / node entry points. |
| **Evidence Traceability** | Responses must reference tool outputs and distinguish facts from inferences. | Aggregator and formatting nodes. |

---

## 2. Guardrails Implementation in Practice

### A. Execution Timeouts & Recursion Limits at the Seam
```python
# agents/services/forecast_planning.py
import asyncio
from agents.graphs.forecast_planning import compiled_graph
from agents.services.exceptions import OrchestrationTimeoutError

async def execute_forecast_workflow(user_id: str, payload: dict, timeout_seconds: float = 30.0) -> dict:
    initial_state = {"user_id": user_id, "input_data": payload, "iteration_count": 0}
    config = {
        "configurable": {"thread_id": f"user_{user_id}"},
        "recursion_limit": 10  # Explicit bound preventing runaway cycles
    }
    
    try:
        result = await asyncio.wait_for(
            compiled_graph.ainvoke(initial_state, config=config),
            timeout=timeout_seconds
        )
        return result
    except asyncio.TimeoutError:
        raise OrchestrationTimeoutError(f"Workflow exceeded {timeout_seconds}s limit")
```

### B. Token & Step Budget Enforcement
```python
# agents/graphs/research/nodes/supervisor.py
MAX_BUDGET_TOKENS = 8000

async def supervisor_node(state: ResearchState) -> dict:
    if state.get("consumed_tokens", 0) >= MAX_BUDGET_TOKENS:
        return {
            "next_step": "FINISH",
            "termination_reason": "budget_exceeded",
            "messages": ["Halting orchestration: token budget reached."]
        }
    ...
```

### C. Evidence Traceability & Fact vs. Inference
- **Fact**: Must quote or cite concrete output returned by an executed tool (e.g. `"Tool returned revenue = $1.2M"`).
- **Inference**: Must be explicitly categorized as a model prediction or hypothesis (e.g. `"Based on historical trends, Q4 may see +5% growth"`).

---

## 3. Testing Orchestration Deterministically

Agent orchestration tests must verify topologies, routing decisions, handoff schemas, and guardrails without external network dependencies:

### A. Testing Supervisor Routing Decisions in Isolation
```python
# tests/agent_tests/graphs/triage/test_edges.py
from agents.graphs.triage.edges import route_supervisor

def test_route_supervisor_halts_on_max_iterations():
    state = {"iteration_count": 5, "next_step": "code_agent"}
    destination = route_supervisor(state)
    assert destination == "FINISH"

def test_route_supervisor_delegates_when_under_limit():
    state = {"iteration_count": 2, "next_step": "code_agent"}
    destination = route_supervisor(state)
    assert destination == "code_agent"
```

### B. Testing Recursion Limit Halting Behavior
```python
# tests/agent_tests/services/test_forecast_planning_service.py
import pytest
from langgraph.errors import GraphRecursionError
from agents.graphs.cyclic_test_graph import compiled_cyclic_graph

@pytest.mark.asyncio
async def test_recursion_limit_halts_infinite_loop():
    config = {"recursion_limit": 4}
    with pytest.raises(GraphRecursionError):
        await compiled_cyclic_graph.ainvoke({"counter": 0}, config=config)
```

### C. Testing Parallel Branch Aggregation
```python
# tests/agent_tests/graphs/multi_review/test_aggregator.py
from agents.graphs.multi_review.nodes.aggregator import aggregate_node

def test_aggregator_handles_partial_branch_failure():
    state = {
        "reviews": [
            {"agent": "security", "status": "ok", "findings": ["SEC01"]},
            {"agent": "performance", "status": "error", "error_message": "Timeout in analysis"}
        ]
    }
    result = aggregate_node(state)
    assert "findings" in result
    assert result["partial_failure_detected"] is True
    assert "performance" in result["failed_agents"]
```

