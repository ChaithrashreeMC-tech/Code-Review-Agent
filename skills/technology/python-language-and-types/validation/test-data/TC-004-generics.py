# TC-004: Generic Class & TypeVar Fixture

from typing import TypeVar, Generic

T = TypeVar("T")

class MemoryStore(Generic[T]):
    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T | None:
        return self._items.pop() if self._items else None

