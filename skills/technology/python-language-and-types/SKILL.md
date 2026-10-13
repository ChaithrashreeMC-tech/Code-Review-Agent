---
name: python-language-and-types
description: >-
  Activate when writing or reviewing Python code syntax, modern Python 3.10+ features,
  static type annotations, mypy/pyright type checking, generics, protocols, Pydantic v2 type
  safety, async typing, or model definitions.
---

# Python Language & Types Technology Skill

## 1. Purpose & Activation

Provides Python language syntax, modern feature usage, static type system rules, and static analysis guidance for Code Review Agent workflows.

**Activate when** inspecting or writing Python code involving type hints, mypy/pyright diagnostics, generic classes, structural protocols, Pydantic models, pattern matching, async function signatures, or modern syntax upgrades (Python 3.10+).

## 2. Supported Use Cases

1. **Code Review**: Pass Python syntax and type annotation evidence to core engineering skills (`skill-eng-maintainability`, `skill-eng-modularity`, `skill-eng-security`).
2. **Type Hardening**: Upgrade untyped or `Any`-heavy Python code to strict PEP 484/585/604 static type hints.
3. **Modernization**: Refactor legacy syntax (`Union[X, Y]`, `Optional[X]`, `Dict`) to modern 3.10+ idioms (`X | Y`, `X | None`, `dict`).
4. **API & Interface Design**: Define rigid duck-typed interfaces via `Protocol` and generic models with `TypeVar` / Pydantic v2.

## 3. Reference Selection

| Topic | Focus | Reference Document |
|---|---|---|
| **Language Idioms & Syntax** | 3.10+ syntax, pattern matching, exception chaining, generators | [`references/language-features.md`](references/language-features.md) |
| **Type System & Annotations** | PEP 484/585/604, `Protocol`, `Generic`, Pydantic v2, type narrowing | [`references/type-system.md`](references/type-system.md) |
| **Type Checker Validation** | `mypy`, `pyright`, strict type checking, `# type: ignore` guardrails | [`references/validation-workflow.md`](references/validation-workflow.md) |

## 4. Execution Workflow

1. **Inspect Code**: Identify target Python version, type hint coverage, and static analyzer settings (`pyproject.toml` `[tool.mypy]`).
2. **Select Guidance**: Load relevant references (`language-features.md` for idioms, `type-system.md` for hints/protocols).
3. **Apply & Verify**:
   - *Review Mode*: Flag unsafe `Any`, missing return types, or improper type ignores; supply technical context to engineering skills.
   - *Implementation Mode*: Add precise type annotations (`X | None`, `Protocol`), replace legacy types, run `mypy --strict`.
4. **Report Result**: Summarize type coverage, analyzer checks, and remaining type ambiguities.

## 5. Technology Guidance vs. Engineering Scoring

- **Technology Skill Responsibility**: Provide accurate Python type system mechanics, modern syntax standards, and type checker commands.
- **Engineering Skill Responsibility**: Evaluate overall maintainability, readability, or modularity and assign numeric scores (0–10 scale).
- This technology skill does **not** generate a separate numeric score.

## 6. Supporting References

- **Language Features**: [`references/language-features.md`](references/language-features.md)
- **Type System**: [`references/type-system.md`](references/type-system.md)
- **Validation Workflow**: [`references/validation-workflow.md`](references/validation-workflow.md)
- **Validation Suite**: [`validation/test-suite.json`](validation/test-suite.json)

