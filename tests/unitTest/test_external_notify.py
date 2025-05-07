import os
import pytest
import requests
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from externals.notify_service import send_notification

@pytest.fixture
def mock_env():
    os.environ['URL_NOTIFICATION'] = "http://mock-notification-service"

@patch("externals.notify_service.requests.post")
def test_send_notification_success(mock_post, mock_env):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_post.return_value = mock_response

    result = send_notification("test@example.com", "1234", "email")
    assert result is True
    mock_post.assert_called_once_with(
        "http://mock-notification-service/notifications",
        json={"to": "test@example.com", "body": "1234", "channel": "email"}
    )

@patch("externals.notify_service.requests.post")
def test_send_notification_404(mock_post, mock_env):
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_post.return_value = mock_response

    with pytest.raises(HTTPException) as exc_info:
        send_notification("test@example.com", "1234", "email")
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Notification rejected by provider"

@patch("externals.notify_service.requests.post")
def test_send_notification_400(mock_post, mock_env):
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_post.return_value = mock_response

    with pytest.raises(HTTPException) as exc_info:
        send_notification("test@example.com", "1234", "email")
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "One or more fields are missing or invalid"

@patch("externals.notify_service.requests.post")
def test_send_notification_service_unavailable(mock_post, mock_env):
    mock_post.side_effect = requests.RequestException("Service unavailable")

    with pytest.raises(HTTPException) as exc_info:
        send_notification("test@example.com", "1234", "email")
    assert exc_info.value.status_code == 503
    assert "Notification service unavailable" in exc_info.value.detail