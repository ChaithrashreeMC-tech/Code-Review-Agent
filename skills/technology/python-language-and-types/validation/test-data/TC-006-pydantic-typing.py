# TC-006: Pydantic v2 Type Safety Fixture

from pydantic import BaseModel, Field, ConfigDict

class AccountPayload(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    account_id: int = Field(gt=0)
    name: str
    is_active: bool = True

