# Graph Package Architecture & Layer Boundaries

This reference documents the canonical Clean Architecture graph package structure, directional dependency rules, naming conventions, and structural invariants for LangGraph agent orchestration.

---

## 1. Canonical Layering & Folder Structure

In Clean Architecture Python backends, agent orchestration acts as a **driving adapter** within the `agents/` layer:

```text
agents/
├── __init__.py                    # Global registry: graph_id -> compiled graph
├── graphs/
│   ├── __init__.py
│   ├── shared/
│   │   ├── state.py                # State schemas & fragments shared across graphs
│   │   └── nodes/                  # Node helpers reused across graphs
│   └── [feature]/                  # One package per agent feature
│       ├── __init__.py             # Exports compiled graph object (public seam contract)
│       ├── state.py                # Feature-specific state schema and reducers
│       ├── nodes/                  # Node modules (e.g. classify_intent.py, supervisor.py)
│       ├── edges.py                # Pure routing / conditional-edge decision functions
│       ├── graph.py                # Graph assembly and compilation (builder.compile())
│       └── prompts/                # Prompt templates and system instructions
├── tools/                          # LangGraph tools bridging to Application layer
├── llm/                            # LLM provider abstractions & model factories
├── persistence/                    # Checkpointer & thread storage wiring
└── services/
    └── [feature].py                # Feature seam service: maps API requests <-> graph state,
                                     # manages thread/run IDs, streaming events, and timeouts

api/
└── routers/[feature].py            # Depends ONLY on agents/services/[feature].py (Seam Rule)

application/
└── features/[feature]/             # Application command/query handlers called by tools
```

---

## 2. Naming Conventions & Structural Invariants

| Component | Naming Rule | Example |
|---|---|---|
| Graph Package | Snake_case workflow noun | `agents/graphs/forecast_planning/`, `agents/graphs/risk_analysis/` |
| Node Module | Snake_case verb phrase | `classify_intent.py`, `evaluate_risk.py`, `supervisor.py` |
| Seam Module | Matches graph package name | `agents/services/forecast_planning.py` |
| Routing Module | Standard module name | `edges.py` (pure routing functions without side-effects) |
| Assembly Module | Standard module name | `graph.py` (single assembly point for `StateGraph`) |

### Structural Invariants
- **Multi-Graph Shape Everywhere**: Every agent feature uses the complete graph package structure (`state.py`, `nodes/`, `edges.py`, `graph.py`), even single-agent topologies. This allows a single-agent graph to evolve into a multi-agent pipeline by adding nodes without architectural refactoring.
- **No Loose Modules in `agents/graphs/`**: Only `__init__.py`, `shared/`, and `[feature]/` packages are permitted.
- **One Seam Service per Feature**: Exactly one `agents/services/[feature].py` module encapsulates invocation of `agents/graphs/[feature]/`.
- **Test Tree Symmetry**: `tests/agent_tests/` directly mirrors `agents/` (`tests/agent_tests/graphs/[feature]/`, `tests/agent_tests/services/`).

---

## 3. Mandatory Directional Dependency Rules

Dependencies must strictly flow inward and downstream:

```text
api/  -->  agents/services/  -->  agents/graphs/[feature]/  -->  agents/tools/ | agents/llm/ | agents/persistence/
                     \                      \
                      --------------------->  config / observability / utils
```

| Rule Name | Rule Statement & Rationale | Violation Example |
|---|---|---|
| **Graph Isolation** | `agents/graphs/**` never imports from `api/**` or `agents/services/**`. Graphs are transport-agnostic. | `from agents.services.risk import RiskService` inside a node. |
| **API Seam Access** | `api/**` never imports from `agents/graphs/**` directly. It must invoke `agents/services/**`. | `from agents.graphs.risk.graph import compiled_graph` inside an API router. |
| **Public Seam Contract** | `agents/services/**` imports a compiled graph ONLY from `agents/graphs/[feature]/__init__.py`, never from `nodes/`, `edges.py`, or `graph.py` directly. | `from agents.graphs.risk.graph import build_risk_graph` in seam service. |
| **Sibling Graph Isolation** | A graph package never imports a sibling graph package directly. Shared items go in `agents/graphs/shared/`. | `from agents.graphs.sales.nodes import planner` inside `agents/graphs/finance/`. |
| **Core Layer Independence** | `config/`, `observability/`, and `utils/` import from no other project layer. | `from agents.graphs.risk.state import RiskState` inside `config/`. |
| **Inward Tool Dependency** | `agents/tools/`, `agents/llm/`, and `agents/persistence/` never import from `agents/graphs/`. (Nodes import tools, not vice versa). | `from agents.graphs.risk.state import RiskState` inside a tool module. |
| **Sibling State Contract** | Nodes import state schema from sibling `state.py` (or `shared/state.py`) and never redefine it inline. | Defining a duplicate `class WorkflowState(TypedDict)` inside `nodes/evaluator.py`. |
| **Acyclic Node Design** | `nodes/` modules never import `graph.py` (prevents circular dependency cycles). | `from agents.graphs.risk.graph import graph_builder` inside a node. |
| **Transport Model Isolation** | Nodes and edges never import API request/response schemas from `api/schemas/`. Seam services translate them. | `from api.schemas.risk import RiskRequestPayload` inside `edges.py`. |
| **Service Composition** | Graph-to-graph composition occurs in `agents/services/`, never inside a node. | Invoking a secondary LangGraph instance directly inside a node function. |
| **Tool Handler Delegation** | `agents/tools/` may import from `application/` ONLY. Tools never import `infrastructure/` or `domain/` directly and never open raw DB sessions. | `from infrastructure.db import get_session` or running `session.query(...)` in a tool. |

---

## 4. Distinguishing Project Conventions from External Repositories

- **Clean Architecture Repositories**: Directional dependency rules are strictly enforced as architectural boundaries. Violations represent structural modularity defects.
- **External / Minimalist Repositories**: If an external codebase legitimately employs a single-file or non-Clean Architecture pattern, evaluate technical cohesion and safety rather than forcing rigid Clean Architecture directory structures.
