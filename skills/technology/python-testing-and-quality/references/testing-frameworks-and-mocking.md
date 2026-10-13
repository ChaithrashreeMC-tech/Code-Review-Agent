# Python Testing Frameworks & Mocking Reference

## 1. Pytest Best Practices

- **Test Discovery**: Name test files `test_*.py` or `*_test.py`; name test functions `test_*`.
- **Assertions**: Use plain `assert expr, "message"` statements instead of `self.assertEqual()`.
- **Exceptions**: Test raised exceptions with `with pytest.raises(ExpectedException, match="regex"):`.
- **Parametrization**: Use `@pytest.mark.parametrize("input_val, expected", [(a, b), (c, d)])` for multiple inputs.

```python
import pytest

@pytest.mark.parametrize("val, expected", [(2, 4), (3, 9)])
def test_square(val: int, expected: int) -> None:
    assert val ** 2 == expected
```

## 2. Fixture Management & Scope

- Place reusable fixtures in `conftest.py`.
- **Scopes**: Use `function` (default), `class`, `module`, or `session`. Default to `function` for test isolation.
- **Yield Fixtures**: Use `yield` for setup/teardown resources (DB transactions, temp files).

```python
import pytest
from typing import Generator

@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    session = create_test_session()
    yield session
    session.rollback()
    session.close()
```

## 3. Mocking & Isolation

- **Side-Effect Protection**: Never make real network HTTP or production DB calls in unit tests.
- **unittest.mock**: Use `unittest.mock.patch` or `pytest-mock` (`mocker` fixture).
- **Async Mocking**: Use `unittest.mock.AsyncMock` for coroutines in Python 3.8+.
- **Patch Location**: Patch where the object is *imported*, not where it is defined.

```python
# Patching external HTTP call safely
def test_fetch_user(mocker: MockerFixture) -> None:
    mock_get = mocker.patch("app.services.user_service.requests.get")
    mock_get.return_value.json.return_value = {"id": 1, "name": "Alice"}
    
    user = fetch_user(1)
    assert user.name == "Alice"
    mock_get.assert_called_once_with("https://api.example.com/users/1")
```

## 4. Async Testing

- Annotate async test functions with `@pytest.mark.asyncio`.
- Configure `asyncio_mode = "auto"` in `pyproject.toml` or `pytest.ini` when using `pytest-asyncio`.

```python
import pytest

@pytest.mark.asyncio
async def test_async_fetch() -> None:
    result = await async_fetch_data()
    assert result["status"] == "ok"
```

## 5. Anti-Patterns to Avoid

- **Assertion-free tests**: Running code without checking outputs or state.
- **Shared mutable state**: Reusing mutable objects across tests without reset.
- **Over-mocking**: Mocking internal domain logic instead of external dependencies.
- **Unmocked I/O**: Allowing network or file system mutations in unit test runs.

