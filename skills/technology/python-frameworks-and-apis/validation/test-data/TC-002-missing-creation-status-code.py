from fastapi import FastAPI, status
from pydantic import BaseModel

app = FastAPI()

class ItemCreate(BaseModel):
    name: str

@app.post("/items/violation")
async def create_item_default_status(item: ItemCreate) -> dict:
    # Violation: POST creation endpoint defaults to 200 OK instead of 201 Created
    return {"id": 101, "name": item.name}

@app.post("/items/safe", status_code=status.HTTP_201_CREATED)
async def create_item_explicit_201(item: ItemCreate) -> dict:
    # Safe: Explicitly specifies status_code=201 Created
    return {"id": 101, "name": item.name}

