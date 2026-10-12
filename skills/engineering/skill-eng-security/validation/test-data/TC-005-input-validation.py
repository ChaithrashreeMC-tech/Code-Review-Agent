def process_user_payload_violation(request):
    # SEC05 Violation: Processing raw untyped payload without schema validation or size limits
    data = request.json
    db.save_user_settings(data['user_id'], data['settings'])

from pydantic import BaseModel, Field

class UserSettingsSchema(BaseModel):
    user_id: int
    settings: dict = Field(..., max_length=1000)

def process_user_payload_safe(request):
    # SEC05 Safe: Enforces schema validation and payload size boundaries
    payload = UserSettingsSchema(**request.json)
    db.save_user_settings(payload.user_id, payload.settings)

