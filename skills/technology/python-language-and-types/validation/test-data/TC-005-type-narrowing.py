# TC-005: Type Narrowing & TypeGuard Fixture

from typing import TypeGuard

def is_string_tuple(val: tuple[object, ...]) -> TypeGuard[tuple[str, ...]]:
    return all(isinstance(x, str) for x in val)

def format_tuple(val: tuple[object, ...]) -> str:
    if is_string_tuple(val):
        return ":".join(val)
    return ""

