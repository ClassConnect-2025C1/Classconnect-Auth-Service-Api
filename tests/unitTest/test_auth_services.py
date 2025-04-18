from unittest.mock import MagicMock
from unittest.mock import patch
from schemas.auth_schemas import UserLogin
from fastapi import HTTPException
import pytest
from models.credential_models import Credential, VerificationPin
from datetime import datetime, timezone, timedelta
from services.auth_services import login_user, verify_pin, PIN_EXPIRATION_MINUTES, assert_user_already_verified
from services.auth_services import create_pin, notify_user

def test_login_user_unverified_should_raise_exception():
    # Arrange
    fake_db = MagicMock()
    user_data = UserLogin(email="test@example.com", password="securepass")

    fake_user = Credential(
        email="test@example.com",
        hashed_password="$2b$12$hashedfakepassword",
        is_verified=False
    )

    with patch("services.auth_services.get_user_by_email", return_value=fake_user), \
         patch("services.auth_services.verify_password", return_value=True):

        #chequeo que el usuario no esta verificado
        with pytest.raises(HTTPException) as exc_info:
            login_user(user_data, fake_db)

        exception = exc_info.value
        assert exception.status_code == 403
        assert exception.detail == "User not verified"


def test_try_verify_alreadyverified_user_raise_404_code():
    mock_db = MagicMock()
    user_email = "testEmail@test.com"
    
    # Creamos un usuario simulado marcado como verificado
    mock_user = Credential()
    mock_user.id = user_email
    mock_user.is_verified = True

    with patch("services.auth_services.get_user_by_email", return_value=mock_user):
        with pytest.raises(HTTPException) as exc:
            assert_user_already_verified(mock_db, user_email)

        assert exc.value.status_code == 404
        assert exc.value.detail == "User already verified"

def test_try_verify_invalid_pin_raise_401_code():
    mock_db = MagicMock()
    user_email =  "testEmail@test.com"
    correct_pin = "0123456789"
    invalid_pin = "9876543210"

    verificacion_pin = VerificationPin(email=user_email, pin=correct_pin, created_at=datetime.now(timezone.utc))

    with patch("services.auth_services.assert_user_already_verified", return_value=None), \
        patch("services.auth_services.get_verification_pin", return_value=verificacion_pin):
        # Simulate the behavior of get_verification_pin to return None
        with pytest.raises(HTTPException) as exc:
            verify_pin(mock_db, user_email, invalid_pin)

        assert exc.value.status_code == 401
        assert exc.value.detail == "Invalid verification pin"

def test_try_expired_pin_raise_410_code():
    mock_db = MagicMock()
    user_email =  "testEmail@test.com"
    correct_pin = "0123456789"
    expired_time = datetime.now(timezone.utc) - timedelta(minutes=15)

    expired_pin = VerificationPin(email=user_email, pin=correct_pin, created_at=expired_time)

    with patch("services.auth_services.assert_user_already_verified", return_value=None), \
        patch("services.auth_services.get_verification_pin", return_value=expired_pin):
        # Simulate the behavior of get_verification_pin to return None
        with pytest.raises(HTTPException) as exc:
            verify_pin(mock_db, user_email, correct_pin)

        assert exc.value.status_code == 410
        assert exc.value.detail == "Verification pin expired"

def test_succes_verification_return_true():
    mock_db = MagicMock()
    user_email =  "testEmail@test.com"
    correct_pin = "0123456789"
    created_time = datetime.now(timezone.utc)

    valid_pin = VerificationPin(email=user_email, pin=correct_pin, created_at=created_time)

    with patch("services.auth_services.assert_user_already_verified", return_value=None), \
        patch("services.auth_services.get_verification_pin", return_value=valid_pin):
        # Simulate the behavior of get_verification_pin to return None
        result = verify_pin(mock_db, user_email, correct_pin)

        assert result is True  # No exception means success

def test_success_verification_delete_pin_from_db():
    mock_db = MagicMock()
    user_email =  "testEmail@test.com"
    correct_pin = "0123456789"
    created_time = datetime.now(timezone.utc)

    valid_pin = VerificationPin(email=user_email, pin=correct_pin, created_at=created_time)

    with patch("services.auth_services.assert_user_already_verified", return_value=None), \
        patch("services.auth_services.get_verification_pin", return_value=valid_pin), \
        patch("services.auth_services.delete_verification_pin") as mock_delete:
        
        verify_pin(mock_db, user_email, correct_pin)

        mock_delete.assert_called_once_with(mock_db, valid_pin)

def test_enter_invalid_pin_make_invalid_the_real():
    mock_db = MagicMock()
    user_email =  "testEmail@test.com"
    correct_pin = "0123456789"
    invalid_pin = "9876543210"

    verificacion_pin = VerificationPin(email=user_email, pin=correct_pin, created_at=datetime.now(timezone.utc))

    with patch("services.auth_services.assert_user_already_verified", return_value=None), \
        patch("services.auth_services.get_verification_pin", return_value=verificacion_pin), \
        patch("services.auth_services.make_invalid_pin") as mock_invalid_pin:
        # Simulate the behavior of get_verification_pin to return None
        with pytest.raises(HTTPException) as exc:
            verify_pin(mock_db, user_email, invalid_pin)

        mock_invalid_pin.assert_called_once_with(mock_db, user_email)

def test_enter_expired_pin_make_invalid_the_real():
    mock_db = MagicMock()
    user_email =  "testEmail@test.com"
    correct_pin = "0123456789"
    expired_time = datetime.now(timezone.utc) - timedelta(minutes=15)

    expired_pin = VerificationPin(email=user_email, pin=correct_pin, created_at=expired_time)

    with patch("services.auth_services.assert_user_already_verified", return_value=None), \
        patch("services.auth_services.get_verification_pin", return_value=expired_pin), \
        patch("services.auth_services.make_invalid_pin") as mock_invalid_pin:
        # Simulate the behavior of get_verification_pin to return None
        with pytest.raises(HTTPException) as exc:
            verify_pin(mock_db, user_email, correct_pin)

        mock_invalid_pin.assert_called_once_with(mock_db, user_email)

def test_success_verification_delete_pin_from_db():
    mock_db = MagicMock()
    user_email =  "testEmail@test.com"
    correct_pin = "0123456789"
    created_time = datetime.now(timezone.utc)

    valid_pin = VerificationPin(email=user_email, pin=correct_pin, created_at=created_time)

    with patch("services.auth_services.assert_user_already_verified", return_value=None), \
        patch("services.auth_services.get_verification_pin", return_value=valid_pin), \
        patch("services.auth_services.delete_verification_pin"), \
        patch("services.auth_services.make_user_verified") as mock_verify_user:
        
        verify_pin(mock_db, user_email, correct_pin)

        mock_verify_user.assert_called_once_with(mock_db, user_email)

def test_create_random_pin_long_6():
    first_pin = create_pin()
    second_pin = create_pin()
    thrid_pin = create_pin()
    assert first_pin != second_pin
    assert second_pin != thrid_pin
    assert first_pin != thrid_pin
    assert len(first_pin) == 6
    assert len(second_pin) == 6
    assert len(thrid_pin) == 6

def test_success_to_send_notification_return_true():
    user_email = "testEmail@test.com"
    toTest = "1234567890"
    channel = "sms"
    pin = "123456"
    mock_db = MagicMock()

    with patch("services.auth_services.create_pin", return_value=pin) as mock_create_pin, \
        patch("services.auth_services.send_notification", return_value=True) as mock_send:
        result = notify_user(mock_db, user_email, toTest, channel)
        mock_create_pin.assert_called_once()
        mock_send.assert_called_once_with(toTest, pin, channel)
        assert result is True

def test_success_to_send_notification_create_db_entry():
    user_email = "testEmail@test.com"
    toTest = "1234567890"
    channel = "sms"
    pin = "123456"
    mock_db = MagicMock()

    with patch("services.auth_services.create_pin", return_value=pin), \
        patch("services.auth_services.send_notification", return_value=True), \
        patch("services.auth_services.create_verification_pin") as mock_create_entry:

        result = notify_user(mock_db, user_email, toTest, channel)

        mock_create_entry.assert_called_once_with(mock_db, user_email, pin)
        assert result is True

