# Python Frameworks & APIs Validation Workflow Reference

## 1. API Testing & Endpoint Verification

- **FastAPI / Starlette**: Use `httpx.AsyncClient` or `starlette.testclient.TestClient`.
- **ConnectRPC**: Test service handlers with mocked context orConnectRPC client stubs.
- **Flask / Django**: Use `app.test_client()` or `django.test.Client`.

```python
import pytest
from httpx import AsyncClient, ASGITransport
from main import app

@pytest.mark.asyncio
async def test_create_user_endpoint() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/users", json={"username": "alice", "email": "alice@example.com", "age": 25})
    assert response.status_code == 201
    assert response.json()["username"] == "alice"
```

## 2. Code Review Checklist for APIs

1. **Request Body Safety**: Are incoming request bodies validated using Pydantic models or Protobuf messages?
2. **Explicit Response Models**: Do endpoints specify response models instead of returning raw unvalidated dicts?
3. **HTTP Status Codes**: Are appropriate HTTP status codes used (`201` for creation, `404` for missing resources)?
4. **Dependency Injection**: Are DB sessions and external services injected cleanly (`Depends()`)?
5. **Error Masking**: Are internal stack traces excluded from public API responses?

