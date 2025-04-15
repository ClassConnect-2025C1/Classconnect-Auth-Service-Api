# tests/unitTest/test_auth_repository.py

from unittest.mock import MagicMock
from repositories.auth_repository import create_user, get_user_by_email
from models.credential_models import Credential
from routes import auth
from controller import service_controller
from services import auth_services

def test_create_user_with_mock():
    mock_db = MagicMock()
    mock_add = mock_db.add
    mock_commit = mock_db.commit
    mock_refresh = mock_db.refresh

    email = "mock@example.com"
    password = "mockpassword"

    # Ejecutar función
    result = create_user(mock_db, email, password)

    # Verificaciones
    mock_add.assert_called_once()
    mock_commit.assert_called_once()
    mock_refresh.assert_called_once()

    assert isinstance(result, Credential)
    assert result.email == email
    assert result.hashed_password != password  # debería estar hasheado

def test_get_user_by_email_with_mock():
    mock_db = MagicMock()

    # Simulamos que .query().filter().first() retorna un usuario
    mock_user = Credential(email="found@example.com", hashed_password="hashed")
    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.first.return_value = mock_user

    result = get_user_by_email(mock_db, "found@example.com")

    mock_db.query.assert_called_once()
    mock_query.filter.assert_called_once()
    assert result.email == "found@example.com"

def test_get_user_by_email_not_found_with_mock():
    mock_db = MagicMock()

    # Simula que no encuentra ningún usuario
    mock_db.query.return_value.filter.return_value.first.return_value = None

    result = get_user_by_email(mock_db, "notfound@example.com")

    assert result is None

def test_user_is_not_verified_when_created():
    mock_db = MagicMock()
    mock_add = mock_db.add
    mock_commit = mock_db.commit
    mock_refresh = mock_db.refresh

    email = "mock@example.com"
    password = "mockpassword"

    user = create_user(mock_db, email, password)

    mock_add.assert_called_once()
    mock_commit.assert_called_once()
    mock_refresh.assert_called_once()

    assert isinstance(user, Credential)
    assert user.is_verified is False