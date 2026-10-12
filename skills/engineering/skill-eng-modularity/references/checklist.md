# Modularity Rules & Architectural Boundary Checklist

Use during code review to identify structural and layering defects across any tech stack—agent orchestration, backend APIs, or component-based frontends.

---

## Boundary Violations — Anti-Pattern Table

| Anti-Pattern | Rule ID | Description | Remediation |
| :--- | :---: | :--- | :--- |
| **Single Responsibility Violation** | MOD01 | Module or class has more than one distinct reason to change. | Split into focused, single-purpose classes or modules (SRP). |
| **Layer Isolation Violation** | MOD02 | High-level module directly imports low-level I/O detail across a layer boundary. | Introduce interface abstraction / dependency inversion at boundary. |
| **Cross-Domain Private Import** | MOD03 | Module in Domain A imports private internal module from Domain B. | Communicate through Domain B's public interface or event stream. |
| **Hardcoded Global Client** | MOD04 | Global SDK / DB / HTTP client instantiated at module import scope. | Use constructor injection, provider factory, or framework DI. |
| **God Class / God Step** | MOD05 | Class or service with > 5 direct dependencies or multi-lifecycle duties. | Split into cohesive sub-services or pipeline steps. |
| **Mixed Wiring & Execution in Graph File** | MOD06 | Graph file (`graph.py`, `edges.py`) contains inline execution or LLM calls. | Extract execution logic into dedicated step files; keep graph declarative. |
| **Raw External Call in Agent Step** | MOD07 | Agent step directly invokes raw SDK endpoint inline. | Route external calls through a shared client abstraction in tools/ shared module. |
| **Fat Handler / Controller** | MOD08 | Business logic, domain decisions, or calculations inside route/RPC handler. | Move logic into dedicated Service; handler only maps transport <-> service. |
| **Bypassed DAL / Raw Query in Service** | MOD09 | Service builds raw SQL strings or directly uses raw DB session handles. | Encapsulate queries in Repository/DAL; service calls repo methods. |
| **Direct Data-Fetching in UI Component** | MOD10 | `fetch()`, `axios()`, or Connect client calls inside JSX component body. | Wrap calls in custom hooks, store actions, or composables. |
| **Feature Code Scattered Globally** | MOD11 | Feature-specific code placed in global utility/component folders. | Collocate inside `features/[FeatureName]/`; expose public API via barrel index. |
| **Circular Dependency** | MOD12 | Circular import detected between two modules (A -> B -> A). | Introduce shared lower-level interface or extract common module. |

---

## Per-Rule Detailed Criteria

### MOD01: Single Responsibility & Cohesion
- **Objective & Scope**: Ensure modules, classes, and functions have a single, well-defined reason to change.
- **Detection Criteria**: Inspect class/module responsibilities. Flag modules handling unrelated domains (e.g. business math + email formatting + DB persistence).
- **Evidence Requirements**: Cite specific line numbers demonstrating multiple unrelated lifecycle or domain responsibilities.
- **False-Positive Guidance**: Cohesive helper modules that group closely related utility methods for a single domain are compliant.
- **Severity Guidance**: High (-8 deduction) per instance.
- **Remediation Guidance**: Decompose into single-purpose components following SRP.

### MOD02: Layer Separation & Dependency Inversion
- **Objective & Scope**: Prevent high-level domain modules from directly importing low-level I/O details across layer boundaries.
- **Detection Criteria**: Flag core domain/business logic importing concrete DB drivers, HTTP libraries, or filesystem SDKs directly.
- **Evidence Requirements**: Show direct import of low-level I/O library inside high-level policy code.
- **False-Positive Guidance**: Low-level integration modules or application composition roots naturally import concrete I/O drivers.
- **Severity Guidance**: High (-10 deduction) per occurrence.
- **Remediation Guidance**: Define an abstract interface in the high-level layer and implement it in the low-level layer.

### MOD03: Cross-Domain Private Imports
- **Objective & Scope**: Protect domain boundary encapsulation across feature or bounded context boundaries.
- **Detection Criteria**: Flag imports reaching into another domain's internal/private paths (e.g. `import domainB.internal.helper`).
- **Evidence Requirements**: Identify source file, target private import path, and target domain context.
- **False-Positive Guidance**: Importing from a domain's explicitly declared public facade (`index.ts` / `public_api.py`) is compliant.
- **Severity Guidance**: Medium (-8 deduction) per import.
- **Remediation Guidance**: Expose required capability through the target domain's public facade API or publish domain events.

### MOD04: Hardcoded Global Clients
- **Objective & Scope**: Ensure SDK, database, and HTTP clients are injectable and mockable.
- **Detection Criteria**: Flag global client instantiation at module import scope (e.g. `client = StripeClient()`).
- **Evidence Requirements**: Point to module-level instantiation lines creating concrete network or DB clients.
- **False-Positive Guidance**: Pure stateless constants or configuration schemas created at module load are acceptable.
- **Severity Guidance**: Medium (-8 deduction) per instance.
- **Remediation Guidance**: Inject client instances via constructor arguments or framework dependency injection.

### MOD05: Module Granularity & God Classes
- **Objective & Scope**: Prevent overly complex, tightly coupled God classes or God pipeline steps.
- **Detection Criteria**: Flag classes or services with > 5 direct dependencies or managing multiple business lifecycles.
- **Evidence Requirements**: Count constructor parameters / imports and list distinct lifecycle responsibilities.
- **False-Positive Guidance**: Orchestration facades or application assembly entry points that purely delegate are acceptable.
- **Severity Guidance**: High (-10 deduction) per class.
- **Remediation Guidance**: Extract sub-responsibilities into cohesive sub-services; apply facade or pipeline patterns.

### MOD06: Declarative Graph Wiring
- **Objective & Scope**: Keep agent orchestration graph definition files purely structural and declarative.
- **Detection Criteria**: Flag inline LLM calls, data transformations, or business logic inside graph assembly files (`graph.py`, `edges.py`).
- **Evidence Requirements**: Reference inline execution blocks inside graph node/edge definitions.
- **False-Positive Guidance**: Pure routing predicate functions that evaluate pre-computed state keys are compliant.
- **Severity Guidance**: High (-10 deduction) per occurrence.
- **Remediation Guidance**: Move node execution and decision logic into dedicated node handler modules.

### MOD07: Agent Step Abstractions
- **Objective & Scope**: Decouple agent node handlers from direct third-party SDK calls.
- **Detection Criteria**: Flag agent node functions directly calling raw external SDK APIs (e.g. cloud storage, vector DBs) inline.
- **Evidence Requirements**: Show direct SDK method invocation inside agent node step functions.
- **False-Positive Guidance**: Invoking project-standard tool wrappers or abstract client interfaces from nodes is compliant.
- **Severity Guidance**: High (-10 deduction) per node.
- **Remediation Guidance**: Wrap external SDK calls in reusable tool modules or client abstractions before invoking from agent nodes.

### MOD08: Handler Layer Isolation
- **Objective & Scope**: Keep transport layer handlers thin and focused solely on request/response mapping.
- **Detection Criteria**: Flag business logic, domain calculations, or direct persistence calls inside HTTP/RPC route handlers.
- **Evidence Requirements**: Highlight domain calculations or direct persistence invocations within controller handler methods.
- **False-Positive Guidance**: Basic request validation, parameter parsing, and HTTP response formatting inside handlers are expected.
- **Severity Guidance**: High (-12 deduction) per handler.
- **Remediation Guidance**: Delegate all processing to domain services; handler only maps input -> service call -> response.

### MOD09: Data Access Isolation
- **Objective & Scope**: Isolate database query construction and raw connection handles inside the Data Access Layer (DAL).
- **Detection Criteria**: Flag raw SQL query strings, raw DB session operations, or inline query building inside Service classes.
- **Evidence Requirements**: Show SQL string literals or raw session execute calls inside domain Service methods.
- **False-Positive Guidance**: ORM query specification objects or repository calls passed from services are compliant.
- **Severity Guidance**: High (-12 deduction) per occurrence.
- **Remediation Guidance**: Move query logic into Repository or DAL classes and expose domain-oriented methods.

### MOD10: UI Component Modularity
- **Objective & Scope**: Prevent direct network calls and data-fetching logic inside UI rendering components.
- **Detection Criteria**: Flag direct `fetch()`, `axios`, or API client calls inside JSX/component render bodies or inline render hooks.
- **Evidence Requirements**: Reference HTTP client calls inside component definitions.
- **False-Positive Guidance**: Presentational event handlers passing data to injected callbacks or using standard data-fetching hooks (e.g. TanStack Query) are compliant.
- **Severity Guidance**: High (-10 deduction) per component.
- **Remediation Guidance**: Extract data fetching into custom hooks, state stores, or container components.

### MOD11: Feature Collocation
- **Objective & Scope**: Maintain feature encapsulation and modular folder organization.
- **Detection Criteria**: Flag feature-specific components, hooks, stores, or clients placed in global shared folders.
- **Evidence Requirements**: Identify feature-bound files located in generic global directories like `/components` or `/utils`.
- **False-Positive Guidance**: Truly generic, domain-agnostic UI primitives (e.g. `Button`, `Modal`) in global folders are compliant.
- **Severity Guidance**: Low (-5 deduction) per misplaced module.
- **Remediation Guidance**: Move feature-specific files into `features/[feature_name]/` directories.

### MOD12: Cyclic Dependencies
- **Objective & Scope**: Eliminate circular import loops between modules, packages, or architectural layers.
- **Detection Criteria**: Detect module import loops (Module A imports Module B, which directly or indirectly imports Module A).
- **Evidence Requirements**: Trace the complete import cycle path across involved files.
- **False-Positive Guidance**: Type-only imports resolved at compile time (e.g. `import type` in TypeScript) are not cyclic runtime dependencies.
- **Severity Guidance**: High (-15 deduction) per cycle.
- **Remediation Guidance**: Break cycles by introducing shared abstractions, extracting common logic, or applying dependency injection.

---

## Technology Adaptation

Modularity principles apply universally across all technologies and paradigms:
- **Backend & Web APIs (Python/Flask/FastAPI, Java/Spring, C#/.NET, Node/Express/Nest, Go, Rust)**: Enforce layer separation between handlers (MOD08), services (MOD01, MOD05), repositories (MOD09), and external clients (MOD04).
- **Agent Orchestration Frameworks (LangGraph, AutoGen, CrewAI, LlamaIndex)**: Separate graph assembly (MOD06) from node execution (MOD07), isolate tool wrappers (MOD04), and prevent cyclic graph dependencies (MOD12).
- **Frontend Frameworks (React, Vue, Angular, Svelte)**: Keep components presentational (MOD10), encapsulate side-effects in custom hooks/stores, and collocate feature assets (MOD11).
- **Systems & Mobile (C++, Rust, Swift, Kotlin)**: Enforce module visibility boundaries (MOD03), strictly manage object lifecycles and DI (MOD04, MOD05), and avoid circular package dependencies (MOD12).
