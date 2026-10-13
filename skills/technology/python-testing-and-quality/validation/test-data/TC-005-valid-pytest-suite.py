import pytest

@pytest.fixture
def sample_user_data() -> dict:
    return {"username": "test_user", "email": "user@example.com"}

def test_valid_user_creation(sample_user_data: dict) -> None:
    # Safe: Well-structured pytest test case using fixture and assertions
    assert sample_user_data["username"] == "test_user"
    assert "@" in sample_user_data["email"]

