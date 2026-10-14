# LangGraph Agent Orchestration: Architecture & Patterns

This reference document details canonical graph architectures, agent topologies, tool-bridging patterns, model abstraction, and guardrail enforcement for Python LangGraph applications.

---

## 1. Canonical Graph Package Architecture

Follow the Clean Architecture layout for agent modules:

```
src/agents/
├── common/                     # Shared agent utilities and prompts
├── llm/                        # Model provider factory and client wrappers
│   ├── factory.py              # Centralized get_chat_model()
│   └── config.py               # Provider settings and schemas
├── services/                   # Seam services exposing graphs to API layer
│   └── review_agent_service.py # AgentService wrapping compiled graph execution
└── graphs/
    └── code_review/            # Feature-specific graph package
        ├── __init__.py
        ├── state.py            # TypedDict / Pydantic state definition
        ├── nodes.py            # Pure / handler-delegating node functions
        ├── edges.py            # Conditional routing functions
        ├── tools.py            # Thin tool adapters delegating to Application layer
        └── graph.py            # Declarative StateGraph assembly & compilation
```

### Dependency Direction Rules
1. `agents/graphs/` may import from `application/` and `domain/`.
2. `domain/` and `application/` **must never** import from `agents/` or `langgraph`.
3. Web APIs (`presentation/` or `controllers/`) interact with `agents/` **only** through `agents/services/`.

---

## 2. Agent Topologies

### A. Sequential Pipeline
Use direct deterministic edges when steps must execute in an unvarying order:
```python
from langgraph.graph import StateGraph, START, END

builder = StateGraph(ReviewState)
builder.add_node("parse_diff", parse_diff_node)
builder.add_node("analyze_security", analyze_security_node)
builder.add_node("format_report", format_report_node)

builder.add_edge(START, "parse_diff")
builder.add_edge("parse_diff", "analyze_security")
builder.add_edge("analyze_security", "format_report")
builder.add_edge("format_report", END)
```

### B. Parallel Fan-Out / Fan-In
Execute independent analysis nodes concurrently and aggregate results via reducers:
```python
from typing import Annotated
from operator import add
from typing_extensions import TypedDict

class MultiAgentState(TypedDict):
    findings: Annotated[list[dict], add]

builder = StateGraph(MultiAgentState)
builder.add_node("security_analyst", security_analyst_node)
builder.add_node("performance_analyst", performance_analyst_node)
builder.add_node("aggregator", aggregate_findings_node)

builder.add_edge(START, "security_analyst")
builder.add_edge(START, "performance_analyst")
builder.add_edge("security_analyst", "aggregator")
builder.add_edge("performance_analyst", "aggregator")
builder.add_edge("aggregator", END)
```

### C. Supervisor / Dynamic Router
Use an LLM supervisor node only when subsequent steps depend dynamically on runtime context or query complexity:
```python
def supervisor_router(state: ReviewState) -> str:
    decision = state.get("next_worker")
    if decision in ["security_agent", "database_agent"]:
        return decision
    return "finish"

builder.add_conditional_edges("supervisor", supervisor_router, {
    "security_agent": "security_agent",
    "database_agent": "database_agent",
    "finish": END
})
```

---

## 3. Tool-to-Application Bridging

Tools must remain thin adapters that delegate to application use cases:

```python
from langchain_core.tools import tool
from src.application.features.review.commands import RunSecurityScanHandler

@tool
def trigger_security_scan(repo_url: str, branch: str) -> dict:
    """Trigger static security analysis on the given repository branch."""
    # Delegate directly to application command handler
    handler = RunSecurityScanHandler()
    result = handler.execute(repo_url=repo_url, branch=branch)
    return {"status": "SUCCESS", "report_id": result.report_id}
```

---

## 4. Orchestration Guardrails & Test Doubles

Always enforce recursion limits and test with deterministic mock models:

```python
# Guardrail Configuration
config = {
    "recursion_limit": 30,
    "configurable": {"thread_id": "review-thread-101"}
}

# Invocation
result = compiled_graph.invoke({"diff": "sample diff"}, config=config)
```

