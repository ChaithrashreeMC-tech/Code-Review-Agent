import pytest
import requests

def test_process_payment_unmocked() -> None:
    # Violation: Makes a real external HTTP call during unit test run without mocking
    response = requests.post("https://api.stripe.com/v1/charges", data={"amount": 1000})
    assert response.status_code == 200

def test_process_payment_mocked(mocker) -> None:
    # Safe: Mocks the external requests.post call cleanly
    mock_post = mocker.patch("requests.post")
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"status": "succeeded"}
    
    response = requests.post("https://api.stripe.com/v1/charges", data={"amount": 1000})
    assert response.status_code == 200
    mock_post.assert_called_once()

