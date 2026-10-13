from typing import TypedDict

class BrokenEvolvedState(TypedDict):
    # Defect: breaking_schema_change causing unhandled_legacy_checkpoint failure
    existing_id: str
    newly_required_non_default_field: int

