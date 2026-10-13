# Python API Contracts & Validation Reference

## 1. Pydantic v2 Request/Response Validation

- Use Pydantic v2 `BaseModel` for body validation, query parameters, and settings.
- Use `Field(..., description="...", ge=1)` for validation constraints and OpenAPI docs.
- Use `model_config = ConfigDict(extra="forbid")` to reject unknown request payload fields.

```python
from pydantic import BaseModel, Field, EmailStr, ConfigDict

class CreateUserRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    age: int = Field(..., ge=18, le=120)
```

## 2. Standard HTTP/RPC Status Codes & Error Responses

- **200 OK / 201 Created**: Successful retrieval / resource creation.
- **400 Bad Request**: Invalid body parameters or validation failure.
- **401 Unauthorized / 403 Forbidden**: Missing or insufficient credentials.
- **404 Not Found**: Resource does not exist.
- **422 Unprocessable Entity**: Automatic Pydantic validation error in FastAPI.
- **500 Internal Server Error**: Unhandled exception. Catch domain exceptions and map to clean HTTP status codes.

```python
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

@app.exception_handler(DomainError)
async def domain_exception_handler(request: Request, exc: DomainError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error_code": exc.code, "message": exc.message}
    )
```

## 3. OpenAPI & Contract Consistency

- Ensure path parameter names in endpoint URL match function argument names (`/users/{id}` -> `def get_user(id: int)`).
- Provide explicit `status_code` on post operations (`status_code=status.HTTP_201_CREATED`).
- Omit internal system stack traces from client error payloads.

