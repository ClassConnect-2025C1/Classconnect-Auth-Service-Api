import os
import pytest
from fastapi import HTTPException
from unittest.mock import patch, MagicMock
import importlib

import externals.user_service as user_service

@pytest.fixture(autouse=True)
def set_env(monkeypatch):
    monkeypatch.setenv('URL_USERS', 'http://fake-url.com')
    # Reload module to update prefix
    importlib.reload(user_service)

def test_get_user_data_success(monkeypatch):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": "123", "name": "Test"}
    monkeypatch.setattr(user_service.requests, "get", lambda url: mock_response)
    result = user_service.get_user_data("123")
    assert result == {"id": "123", "name": "Test"}

def test_get_user_data_404(monkeypatch):
    mock_response = MagicMock()
    mock_response.status_code = 404
    monkeypatch.setattr(user_service.requests, "get", lambda url: mock_response)
    with pytest.raises(HTTPException) as exc:
        user_service.get_user_data("notfound")
    assert exc.value.status_code == 404
    assert exc.value.detail == "User not found"

def test_get_user_data_400(monkeypatch):
    mock_response = MagicMock()
    mock_response.status_code = 400
    monkeypatch.setattr(user_service.requests, "get", lambda url: mock_response)
    with pytest.raises(HTTPException) as exc:
        user_service.get_user_data("bad")
    assert exc.value.status_code == 400
    assert exc.value.detail == "One or more fields are missing or invalid"

def test_get_user_data_request_exception(monkeypatch):
    def raise_exc(url):
        raise user_service.requests.RequestException("Connection error")
    monkeypatch.setattr(user_service.requests, "get", raise_exc)
    with pytest.raises(HTTPException) as exc:
        user_service.get_user_data("123")
    assert exc.value.status_code == 503
    assert "Notification service unavailable" in exc.value.detail

def test_update_user_data_success(monkeypatch):
    mock_response = MagicMock()
    mock_response.status_code = 200
    monkeypatch.setattr(user_service.requests, "patch", lambda url, json: mock_response)
    result = user_service.update_user_data("123", {"name": "New"})
    assert result is True

def test_update_user_data_404(monkeypatch):
    mock_response = MagicMock()
    mock_response.status_code = 404
    monkeypatch.setattr(user_service.requests, "patch", lambda url, json: mock_response)
    with pytest.raises(HTTPException) as exc:
        user_service.update_user_data("notfound", {"name": "New"})
    assert exc.value.status_code == 404
    assert exc.value.detail == "User not found"

def test_update_user_data_400(monkeypatch):
    mock_response = MagicMock()
    mock_response.status_code = 400
    monkeypatch.setattr(user_service.requests, "patch", lambda url, json: mock_response)
    with pytest.raises(HTTPException) as exc:
        user_service.update_user_data("bad", {"name": "New"})
    assert exc.value.status_code == 400
    assert exc.value.detail == "One or more fields are missing or invalid"

def test_update_user_data_422(monkeypatch):
    mock_response = MagicMock()
    mock_response.status_code = 422
    monkeypatch.setattr(user_service.requests, "patch", lambda url, json: mock_response)
    with pytest.raises(HTTPException) as exc:
        user_service.update_user_data("unauth", {"name": "New"})
    assert exc.value.status_code == 403
    assert exc.value.detail == "User not authorized to update this data"

def test_update_user_data_request_exception(monkeypatch):
    def raise_exc(url, json):
        raise user_service.requests.RequestException("Connection error")
    monkeypatch.setattr(user_service.requests, "patch", raise_exc)
    with pytest.raises(HTTPException) as exc:
        user_service.update_user_data("123", {"name": "New"})
    assert exc.value.status_code == 503
    assert "Notification service unavailable" in exc.value.detail