# tests/unitTest/test_auth_repository.py

from unittest.mock import MagicMock
from repositories.auth_repository import create_user, get_user_by_email, get_user_by_id
from repositories.auth_repository import create_verification_pin, get_verification_pin, delete_verification_pin, set_pin_invalid
from models.credential_models import Credential, VerificationPin
from datetime import datetime, timezone

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

def test_get_user_by_id():
    mock_db = MagicMock()
    id = "123456789"
    # Simulamos que .query().filter().first() retorna un usuario
    mock_user = Credential(id=id ,email="found@example.com", hashed_password="hashed")
    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.first.return_value = mock_user

    result = get_user_by_id(mock_db, "found@example.com")

    mock_db.query.assert_called_once()
    mock_query.filter.assert_called_once()
    assert result.id == id

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

def test_create_verification_pin_returns_model():
    mock_db = MagicMock()
    mock_add = mock_db.add
    mock_commit = mock_db.commit
    mock_refresh = mock_db.refresh

    user_id = "user@example.com"
    pin = "123456"

    result = create_verification_pin(mock_db, user_id, pin)

    assert isinstance(result, VerificationPin)
    assert result.user_id == user_id
    assert result.pin == pin
    assert isinstance(result.created_at, datetime)
    assert result.created_at.tzinfo is not None

def test_create_verification_pin_sets_recent_timestamp():
    mock_db = MagicMock()
    user_id = "13456"
    pin = "123456"

    before = datetime.now(timezone.utc)

    result = create_verification_pin(mock_db, user_id, pin)

    after = datetime.now(timezone.utc)

    # Asegura que el tiempo de creación esté entre `before` y `after`
    assert before <= result.created_at <= after

def test_get_not_exist_pin_return_none():
    mock_db = MagicMock()
    user_id = "1234567890"

    # Simula que no encuentra ningún usuario
    mock_db.query.return_value.filter.return_value.first.return_value = None

    result = get_verification_pin(mock_db, user_id)

    assert result is None

def test_get_veritication_pin_success():
    mock_db = MagicMock()
    user_id = "1234567890"
    pin = "123456"

    # Simula que encuentra el pin
    mock_pin = VerificationPin(user_id=user_id, pin=pin, created_at=datetime.now(timezone.utc))
    mock_db.query.return_value.filter.return_value.first.return_value = mock_pin

    result = get_verification_pin(mock_db, user_id)

    assert result is not None
    assert result.user_id == user_id
    assert result.pin == pin

def test_delete_verification_pin():
    mock_db = MagicMock()
    verification_pin = VerificationPin(user_id="1234567890", pin="123456", created_at=datetime.now(timezone.utc))

    # Simula el comportamiento de eliminar el pin
    delete_verification_pin(mock_db, verification_pin)

    # Verifica que se haya llamado a commit
    mock_db.commit.assert_called_once()

def test_created_pin_is_valid():
    mock_db = MagicMock()
    user_id = "13456"
    pin = "123456"

    result = create_verification_pin(mock_db, user_id, pin)

    # Asegura que el tiempo de creación esté entre `before` y `after`
    assert result.is_valid is True

def test_change_is_valid_to_false():
    mock_db = MagicMock()
    user_id = "123456790"
    pin = "123456"
    
    pin_entry = VerificationPin(user_id=user_id, pin=pin, is_valid=True)
    
    # Configuramos el mock para que devuelva esta entrada al hacer la query
    mock_db.query.return_value.filter_by.return_value.first.return_value = pin_entry

    # Ejecutamos la función
    set_pin_invalid(mock_db, user_id)

    # Aserciones
    assert pin_entry.is_valid is False
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(pin_entry)