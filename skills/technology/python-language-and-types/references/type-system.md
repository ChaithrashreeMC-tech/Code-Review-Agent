# Python Type System Reference

## 1. Native Static Type Annotations

Use built-in generics (PEP 585) and pipe unions (PEP 604) across all function signatures and class fields:

```python
from typing import Callable

def process_items(
    items: list[str],
    handler: Callable[[str], bool] | None = None
) -> dict[str, bool]:
    results: dict[str, bool] = {}
    for item in items:
        results[item] = handler(item) if handler else True
    return results
```

---

## 2. Protocols (Structural Subtyping)

Use `Protocol` to define implicit interfaces without requiring inheritance:

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Serializer(Protocol):
    def serialize(self) -> dict[str, str]: ...

class UserDTO:
    def serialize(self) -> dict[str, str]:
        return {"id": "123", "type": "user"}

def send_payload(obj: Serializer) -> None:
    data = obj.serialize()
```

---

## 3. Generics & Type Variables

Reusable generic classes and functions using `TypeVar` or `Generic[T]`:

```python
from typing import TypeVar, Generic

T = TypeVar("T")

class Repository(Generic[T]):
    def __init__(self) -> None:
        self._storage: list[T] = []

    def add(self, item: T) -> None:
        self._storage.append(item)

    def get_all(self) -> list[T]:
        return self._storage
```

---

## 4. Type Narrowing & `TypeGuard`

Refine loose types safely using `isinstance` or custom `TypeGuard` functions:

```python
from typing import TypeGuard

def is_str_list(val: list[object]) -> TypeGuard[list[str]]:
    return all(isinstance(x, str) for x in val)

def process_unknown(val: list[object]) -> str:
    if is_str_list(val):
        return ", ".join(val)  # Type narrowed to list[str]
    return ""
```

---

## 5. Pydantic v2 Type Integration

Use Pydantic v2 `BaseModel`, `Field`, and `ConfigDict` for runtime validation with static type safety:

```python
from pydantic import BaseModel, Field, ConfigDict

class UserModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    user_id: int = Field(gt=0, description="Positive integer ID")
    email: str
    role: str = "user"
```

