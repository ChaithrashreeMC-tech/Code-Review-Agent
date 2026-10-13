from fastapi import FastAPI

app = FastAPI()

@app.get("/users/{user_id}")
async def get_user_unvalidated_dict(user_id: int) -> dict:
    # Violation: Returns raw unvalidated dictionary without Pydantic response model
    return {"id": user_id, "internal_secret": "secret_data", "name": "Alice"}

@app.get("/users/{user_id}/safe")
async def get_user_validated_model(user_id: int):
    # Safe: Returns validated dictionary or Pydantic model
    return {"id": user_id, "name": "Alice"}

