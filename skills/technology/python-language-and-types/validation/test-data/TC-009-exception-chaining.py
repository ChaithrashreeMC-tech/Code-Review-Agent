# TC-009: Explicit Exception Chaining Fixture

import json

# Violation: Masking original cause without chaining
def parse_payload_violation(raw: str) -> dict[str, object]:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        raise ValueError("Invalid payload JSON")

# Safe: Preserving cause via 'from'
def parse_payload_safe(raw: str) -> dict[str, object]:
    try:
        return json.loads(raw)
    except json.JSONDecodeError as err:
        raise ValueError("Invalid payload JSON") from err

