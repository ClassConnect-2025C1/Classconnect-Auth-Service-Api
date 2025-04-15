from unittest.mock import MagicMock
from unittest.mock import patch
from schemas.auth_schemas import UserLogin
from fastapi import HTTPException
import pytest
from models.credential_models import Credential
from services.auth_services import login_user

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