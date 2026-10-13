# Type Validation Workflow Reference

## 1. Type Checker Commands & Modes

| Tool | Primary Command | Strict Checking Command |
|---|---|---|
| **mypy** | `uv run mypy src/` | `uv run mypy --strict src/` |
| **pyright** | `uv run pyright` | `uv run pyright --level strict` |

---

## 2. Type Suppression Policy (`# type: ignore`)

1. **Specific Error Codes**: Never use bare `# type: ignore`. Always specify the exact error code (e.g., `# type: ignore[override]`, `# type: ignore[arg-type]`).
2. **Document Justification**: Include a brief inline comment explaining why type suppression is necessary.
```python
# GOOD: Specific error code with comment
result = third_party_untyped_call()  # type: ignore[no-untyped-call] # Legacy C-extension stub
```

---

## 3. Review & Verification Workflow

1. **Verify Signatures**: Ensure all public methods and functions specify parameter and return type annotations.
2. **Eliminate Unbound `Any`**: Replace unconstrained `Any` with concrete types, generics `T`, `object`, or `Protocol`.
3. **Execute Type Check**: Run `mypy` or `pyright`. Report unresolved type diagnostics as type safety findings.

