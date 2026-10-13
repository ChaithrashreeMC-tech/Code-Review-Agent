from pydantic import BaseModel, ConfigDict

class UnstrictPayloadViolation(BaseModel):
    # Violation: Missing model_config extra='forbid' allowing unknown payload attributes
    title: str
    amount: float

class StrictPayloadSafe(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str
    amount: float

