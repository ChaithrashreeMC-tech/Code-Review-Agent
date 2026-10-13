from fastapi import FastAPI, Depends, status
from pydantic import BaseModel, ConfigDict

app = FastAPI()

class ProductCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str
    price: float

class ProductResponse(BaseModel):
    id: int
    name: str
    price: float

def get_product_repo():
    return "repo_stub"

@app.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductCreate, repo=Depends(get_product_repo)) -> ProductResponse:
    # Safe: Valid, type-safe FastAPI endpoint with response model, 201 status code, and dependency injection
    return ProductResponse(id=1, name=product.name, price=product.price)

