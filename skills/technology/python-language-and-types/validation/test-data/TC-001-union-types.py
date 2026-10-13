# TC-001: Modern Union Type Syntax Fixture
# Pipe union syntax (PEP 604)

def parse_user_id(raw_id: str | int) -> int:
    if isinstance(raw_id, int):
        return raw_id
    return int(raw_id)

