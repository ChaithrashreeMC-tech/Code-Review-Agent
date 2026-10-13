# Python Language Features Reference

## 1. Modern Syntax Idioms (Python 3.10+)

| Feature | Legacy Pattern (Avoid) | Modern Idiom (Prefer) | Benefits |
|---|---|---|---|
| **Union Types** | `Union[int, str]` | `int | str` | Cleaner, PEP 604 native syntax |
| **Optional Types** | `Optional[str]` | `str | None` | Explicit nullability without `typing` import |
| **Built-in Collections** | `List[int]`, `Dict[str, Any]` | `list[int]`, `dict[str, Any]` | PEP 585 native generic collections |
| **Pattern Matching** | `if/elif` chains on dicts/types | `match/case` | Structural extraction and type matching |

### Pattern Matching Example
```python
match payload:
    case {"type": "user", "id": int(user_id)}:
        process_user(user_id)
    case {"type": "event", "name": str(name)}:
        process_event(name)
    case _:
        raise ValueError("Invalid payload structure")
```

---

## 2. Error Handling & Context Management

### Explicit Exception Chaining
Always preserve cause tracebacks when translating exceptions:
```python
# GOOD: Preserves original cause via 'from'
try:
    data = json.loads(raw_input)
except json.JSONDecodeError as err:
    raise InvalidPayloadError("Failed to parse JSON") from err
```

### Context Managers for Resource Safety
Enforce deterministic resource cleanup using `with` or `async with`:
```python
# GOOD: Auto-closes file/connection
with open("data.json", "r", encoding="utf-8") as f:
    config = json.load(f)
```

---

## 3. Efficient Iteration & Memory Performance

1. **Strict Zip**: Use `zip(..., strict=True)` to prevent silent truncation when combining iterables of unequal length.
2. **Generators for Large Data**: Prefer generator expressions `(x for x in data)` over list comprehensions `[x for x in data]` when processing streaming data to conserve RAM.

