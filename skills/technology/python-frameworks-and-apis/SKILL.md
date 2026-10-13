---
name: python-frameworks-and-apis
description: >-
  Activate when writing, inspecting, or reviewing Python web and API frameworks (FastAPI, ConnectRPC, Flask, Django),
  request/response validation models (Pydantic v2, Protobuf), API routing, middleware, status codes, or OpenAPI specs.
---

# Python Frameworks & APIs Technology Skill

## 1. Purpose & Activation

Provides technology guidance for Python web frameworks, API routing, schema-first contracts, and request/response validation in Code Review Agent workflows.

**Activate when** inspecting or writing Python API endpoints (FastAPI path operations, ConnectRPC Protobuf handlers, Flask blueprints, Django views), Pydantic request/response schemas, API middleware, error handling, status codes, or API integration logic.

## 2. Supported Use Cases

1. **Code Review**: Extract API routing patterns, request validation safety, status codes, and contract alignment to supply evidence to engineering skills (`skill-eng-maintainability`, `skill-eng-security`, `skill-eng-business-logic`).
2. **API Endpoint Scaffolding**: Build robust, type-safe API endpoints using FastAPI dependency injection or ConnectRPC handlers.
3. **Contract Validation**: Enforce strict request/response validation using Pydantic v2 models or Protobuf schema generation (`gen/`).
4. **Error Handling & Middleware**: Standardize HTTP/RPC error responses, CORS configurations, and exception handlers.

## 3. Reference Selection

| Topic | Focus | Reference Document |
|---|---|---|
| **Frameworks & Routing** | FastAPI, ConnectRPC, Flask, Django, routing, dependency injection | [`references/frameworks-and-routing.md`](references/frameworks-and-routing.md) |
| **API Contracts & Validation** | Pydantic v2, Protobuf schemas, error handling, status codes | [`references/api-contracts-and-validation.md`](references/api-contracts-and-validation.md) |
| **Validation Workflow** | Execution commands, API testing, anti-patterns, contract checks | [`references/validation-workflow.md`](references/validation-workflow.md) |

## 4. Execution Workflow

1. **Inspect API Setup**: Identify framework (FastAPI, ConnectRPC, Flask, Django), routing structure, and contract definitions (Pydantic models, `.proto` files).
2. **Select Reference**: Load relevant guide (`frameworks-and-routing.md` for endpoint design; `api-contracts-and-validation.md` for schemas/errors).
3. **Execute & Evaluate**:
   - *Review Mode*: Flag untyped request payloads, unhandled exceptions, raw dictionary returns, or missing status codes. Pass context to engineering skills.
   - *Implementation Mode*: Define typed request/response models, wire dependency injection, implement exception handlers.
4. **Report Results**: State verified endpoints, schema validations, and framework compliance status.

## 5. Technology Guidance vs. Engineering Scoring

- **Technology Skill Responsibility**: Provide accurate framework idioms, routing mechanics, Pydantic/Protobuf schema patterns, and API testing setups.
- **Engineering Skill Responsibility**: Evaluate overall security, maintainability, or business logic correctness and assign numeric scores (0–10 scale).
- This technology skill does **not** generate a separate numeric score.

## 6. Supporting References

- **Frameworks & Routing**: [`references/frameworks-and-routing.md`](references/frameworks-and-routing.md)
- **API Contracts & Validation**: [`references/api-contracts-and-validation.md`](references/api-contracts-and-validation.md)
- **Validation Workflow**: [`references/validation-workflow.md`](references/validation-workflow.md)
- **Validation Suite**: [`validation/test-suite.json`](validation/test-suite.json)

