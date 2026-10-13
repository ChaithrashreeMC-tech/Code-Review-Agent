# TC-002: Structural Pattern Matching Fixture

def process_event_payload(payload: dict[str, object]) -> str:
    match payload:
        case {"type": "user", "id": int(user_id)}:
            return f"User:{user_id}"
        case {"type": "system", "status": str(status)}:
            return f"System:{status}"
        case _:
            return "Unknown"

