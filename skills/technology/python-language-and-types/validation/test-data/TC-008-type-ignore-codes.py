# TC-008: Specific Type Ignore Codes Fixture

# Violation: Bare type ignore without specific error code or justification
def legacy_call_violation(val: str) -> None:
    untyped_external_fn(val)  # type: ignore

# Safe: Specific error code with rationale
def legacy_call_safe(val: str) -> None:
    untyped_external_fn(val)  # type: ignore[name-defined] # External C-extension wrapper

