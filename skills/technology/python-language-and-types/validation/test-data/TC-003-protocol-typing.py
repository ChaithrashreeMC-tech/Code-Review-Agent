# TC-003: Structural Subtyping with Protocol Fixture

from typing import Protocol, runtime_checkable

@runtime_checkable
class Exportable(Protocol):
    def export_data(self) -> dict[str, str]: ...

class UserRecord:
    def export_data(self) -> dict[str, str]:
        return {"id": "101", "name": "Alice"}

