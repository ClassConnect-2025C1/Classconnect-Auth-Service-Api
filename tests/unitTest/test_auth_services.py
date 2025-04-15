from unittest.mock import MagicMock
from unittest.mock import patch
from schemas.auth_schemas import UserLogin
from fastapi import HTTPException
import pytest
from models.credential_models import Credential, VerificationPin
from datetime import datetime, timezone, timedelta
from services.auth_services import login_user, verify_pin, PIN_EXPIRATION_MINUTES

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
    user_id =  "1234567890"
    pin = "123456"

    with patch("services.auth_services.get_verification_pin", return_value=None):
        # Simulate the behavior of get_verification_pin to return None

        with pytest.raises(HTTPException) as exc:
            verify_pin(mock_db, user_id, pin)

        assert exc.value.status_code == 404
        assert exc.value.detail == "Verification pin not found"

def test_try_verify_invalid_pin_raise_401_code():
    mock_db = MagicMock()
    user_id =  "1234567890"
    correct_pin = "0123456789"
    invalid_pin = "9876543210"

    verificacion_pin = VerificationPin(user_id=user_id, pin=correct_pin, created_at=datetime.now(timezone.utc))

    with patch("services.auth_services.get_verification_pin", return_value=verificacion_pin):
        # Simulate the behavior of get_verification_pin to return None
        with pytest.raises(HTTPException) as exc:
            verify_pin(mock_db, user_id, invalid_pin)

        assert exc.value.status_code == 401
        assert exc.value.detail == "Invalid verification pin"

def test_try_expired_pin_raise_410_code():
    mock_db = MagicMock()
    user_id =  "1234567890"
    correct_pin = "0123456789"
    expired_time = datetime.now(timezone.utc) - timedelta(minutes=15)

    expired_pin = VerificationPin(user_id=user_id, pin=correct_pin, created_at=expired_time)

    with patch("services.auth_services.get_verification_pin", return_value=expired_pin):
        # Simulate the behavior of get_verification_pin to return None
        with pytest.raises(HTTPException) as exc:
            verify_pin(mock_db, user_id, correct_pin)

        assert exc.value.status_code == 410
        assert exc.value.detail == "Verification pin expired"
