# LangGraph Agent Orchestration Review Checklist

This checklist defines concrete review rules (`ORCH01`–`ORCH10`), detection patterns, good/bad code examples, and remediation guidance for single-agent and multi-agent systems built with LangGraph.

---

## Rule Index

| ID | Rule Name | Objective |
|---|---|---|
| `ORCH01` | Canonical Package Layout | Ensure graph packages follow clean separation of concerns and layered folder conventions. |
| `ORCH02` | Seam Service Isolation | Ensure entry points (APIs/workers) invoke graphs through dedicated seam services, not raw graph instances. |
| `ORCH03` | Dependency Boundary Rules | Enforce strict inward dependency directions; forbid domain/application layers from importing `agents/`. |
| `ORCH04` | Tool-to-Application Bridging | Ensure tools act as thin adapters delegating to Application-layer handlers; forbid direct DB/infra access. |
| `ORCH05` | Model Provider Abstraction | Abstract LLM clients behind provider factories or `BaseChatModel` interfaces with safe secret handling. |
| `ORCH06` | Orchestration Guardrails | Enforce runtime guardrails: `recursion_limit`, timeout envelopes, token counters, and concurrency limits. |
| `ORCH07` | Topology Proportionality | Use explicit edges for deterministic flows; reserve LLM supervisor routers only for dynamic routing needs. |
| `ORCH08` | Handoff Contract Validation | Validate cross-agent state transfers and inter-agent handoff payloads with explicit schemas. |
| `ORCH09` | Partial Failure Aggregation | Handle branch errors gracefully in fan-out/fan-in topologies without losing failure traceability. |
| `ORCH10` | Deterministic Orchestration Testing | Test agent graph orchestration deterministically using test doubles (`FakeListChatModel`) without live LLM calls. |

---

## Detailed Rule Checklist

### ORCH01: Canonical Package Layout
- [ ] Graph code is collocated under `agents/graphs/[feature]/` with dedicated submodules: `state.py`, `nodes.py`, `edges.py`, `graph.py`.
- [ ] Shared agent utilities live in `agents/common/` or `agents/services/`.
- ❌ **Anti-pattern:** Placing entire multi-node graph assembly, schemas, LLM prompts, and tool implementations inside a single monolithic file.
- ✅ **Remediation:** Split graph components into `state.py`, `nodes.py`, `edges.py`, and compiled `graph.py`.

### ORCH02: Seam Service Isolation
- [ ] External controllers (FastAPI routers, CLI scripts, message consumers) interact with graphs through an Application/Service seam (`AgentService`).
- ❌ **Anti-pattern:** FastAPI endpoint directly calling `compiled_graph.invoke()` with raw dictionary states.
- ✅ **Remediation:** Introduce a typed service class that wraps graph execution, handles config (`thread_id`), and maps outputs to domain DTOs.

### ORCH03: Dependency Boundary Rules
- [ ] Domain models and application handlers never import from `agents/` or `langgraph`.
- [ ] Graph nodes import down to `application/` and `domain/`, maintaining Clean Architecture dependency inversion.
- ❌ **Anti-pattern:** `domain/entities/order.py` importing `agents.graphs.review.state.ReviewState`.
- ✅ **Remediation:** Move shared data definitions into the domain layer; agent state schemas inherit or compose domain types.

### ORCH04: Tool-to-Application Bridging
- [ ] Agent tools are thin adapters that delegate to injected Application-layer use cases or command handlers.
- [ ] Tools never instantiate direct database sessions or execute raw SQL.
- ❌ **Anti-pattern:** `@tool def process_refund(order_id: str): db_session.execute(...)`.
- ✅ **Remediation:** `@tool def process_refund(order_id: str, handler: RefundHandler): return handler.execute(order_id)`.

### ORCH05: Model Provider Abstraction
- [ ] LLM instances are instantiated via provider factories (`agents/llm/factory.py`) returning `BaseChatModel`.
- [ ] API keys are retrieved from environment/settings models, never hardcoded in graph node files.
- ❌ **Anti-pattern:** `ChatOpenAI(api_key="sk-live-...")` directly instantiated inside a node function.
- ✅ **Remediation:** Use `get_chat_model(provider="openai", model_name="gpt-4o")` reading from centralized settings.

### ORCH06: Orchestration Guardrails
- [ ] All graph invocations set `recursion_limit` (e.g. `config={"recursion_limit": 25}`).
- [ ] Async invocations wrap executions in timeout envelopes (`asyncio.wait_for(...)` or deadline propagation).
- [ ] Token usage or loop iteration budgets are tracked in graph state.
- ❌ **Anti-pattern:** Unbounded while-loop or conditional cyclic graph without `recursion_limit` or escape edge.
- ✅ **Remediation:** Configure `recursion_limit` in execution config and implement cycle counter nodes.

### ORCH07: Topology Proportionality
- [ ] Deterministic sequential tasks use direct graph edges (`add_edge("step_a", "step_b")`), not LLM supervisor routers.
- [ ] Parallel fan-out/fan-in is used when sub-tasks are independent.
- ❌ **Anti-pattern:** Using an expensive GPT-4 LLM call to decide whether to proceed from Step 1 to Step 2 in a fixed linear flow.
- ✅ **Remediation:** Replace LLM routing node with a static edge or deterministic Python conditional edge.

### ORCH08: Handoff Contract Validation
- [ ] Inter-agent handoffs validate required fields using Pydantic schemas or TypedDict before state updates.
- ❌ **Anti-pattern:** Blindly passing untyped freeform dictionaries across multi-agent supervisor boundaries.
- ✅ **Remediation:** Define explicit `HandoffPayload` schema and validate before routing to child agents.

### ORCH09: Partial Failure Aggregation
- [ ] In fan-out parallel executions, one failing branch returns an error record without silently dropping data or crashing sibling branches.
- [ ] Final synthesis node checks for branch error flags and reports partial success when applicable.
- ❌ **Anti-pattern:** Parallel fan-in node assuming all branch outputs are present, triggering `KeyError`.
- ✅ **Remediation:** Use reducers that append branch outcomes (e.g. `results: Annotated[list, add]`) and handle `Exception` payloads gracefully.

### ORCH10: Deterministic Orchestration Testing
- [ ] Orchestration test suites test graph routing and state transitions using `FakeListChatModel` or deterministic mocks.
- [ ] Tests never require live external API calls or network access during automated test runs.
- ❌ **Anti-pattern:** Unit tests calling live OpenAI APIs with real credit card charges.
- ✅ **Remediation:** Inject mock chat models and handler test doubles into graph compile fixtures.

