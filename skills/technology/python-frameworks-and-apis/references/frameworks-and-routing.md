# Python Frameworks & Routing Reference

## 1. FastAPI Idioms & Routing

- **Path Operations**: Use explicit HTTP decorators (`@app.get`, `@app.post`, `@app.put`, `@app.delete`).
- **Dependency Injection**: Inject services, DB sessions, and auth using `Depends()`.
- **Response Models**: Always specify `response_model` or explicit return type annotations to enforce schema serialization.

```python
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel

app = FastAPI()

class UserResponse(BaseModel):
    id: int
    name: str

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, service: UserService = Depends(get_user_service)) -> UserResponse:
    user = await service.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user
```

## 2. ConnectRPC & Protobuf Services

- **Schema First**: Define RPC contracts in `.proto` files (`proto/[project_name]/v1/service.proto`).
- **Code Generation**: Never hand-edit code under `api/gen/`. Implement services in `api/services/`.
- **Handler Implementation**: Extend generated base service class and return Protobuf message instances.

```python
from api.gen.user.v1.user_pb2 import GetUserRequest, GetUserResponse
from api.gen.user.v1.user_pb2_connect import UserServiceServicer

class UserServiceImpl(UserServiceServicer):
    async def get_user(self, req: GetUserRequest, context) -> GetUserResponse:
        user = await self.user_repo.find(req.user_id)
        return GetUserResponse(id=user.id, name=user.name)
```

## 3. Flask & Django Patterns

- **Flask**: Use Blueprints for modular routing. Use Marshmallow or Pydantic for request parsing.
- **Django / DRF**: Use Class-Based Views (CBVs) or ViewSets with Serializers for structured API responses.

## 4. Framework Anti-Patterns

- **Raw Dict Returns**: Returning unvalidated dictionaries without Pydantic models or Protobuf responses.
- **Global DB State**: Accessing un-injected global DB connections directly inside route handlers.
- **Hand-Editing Generated Code**: Modifying generated Protobuf (`*_pb2.py`) or ConnectRPC stubs directly.

