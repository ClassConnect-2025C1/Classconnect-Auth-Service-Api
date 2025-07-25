import pytest
from pydantic import ValidationError
from schemas import auth_schemas
from datetime import datetime, timezone

def test_user_login_valid_data():
    user = auth_schemas.UserLogin(email="test@example.com", password="securepassword123")
    assert user.email == "test@example.com"
    assert user.password == "securepassword123"

def test_user_login_invalid_email():
    with pytest.raises(ValidationError):
        auth_schemas.UserLogin(email="invalid-email", password="pass")

def test_user_login_empty_password():
    user = auth_schemas.UserLogin(email="test@example.com", password="")
    assert user.password == ""



def test_user_register_valid_data():
    

    user = auth_schemas.UserRegister(email="user@example.com", password="password123", name="John", last_name="Doe",role ="student", phone = "123456789") 

    assert user.email == "user@example.com"
    assert user.password == "password123"

def test_user_register_invalid_email():
    with pytest.raises(ValidationError):
        auth_schemas.UserRegister(email="not-an-email", password="password123")

def test_user_register_missing_password():
    with pytest.raises(ValidationError):
        auth_schemas.UserRegister(email="user@example.com")


def test_token_response_default_type():
    token = auth_schemas.TokenResponse(access_token="some.jwt.token")
    assert token.access_token == "some.jwt.token"
    assert token.token_type == "bearer"

def test_token_response_custom_type():
    token = auth_schemas.TokenResponse(access_token="some.jwt.token", token_type="custom")
    assert token.token_type == "custom"


def test_verification_pin_valid_data():
    # Simula una fecha con timezone (UTC en este caso)
    aware_dt = datetime.now(timezone.utc)

    user_email = "tesEmail@test.com"
    pin = "123456"
    schema = auth_schemas.VerificationPin(email=user_email, pin=pin, created_at=aware_dt)

    assert schema.email == user_email
    assert schema.pin == pin
    assert isinstance(schema.created_at, datetime)
    assert schema.created_at.tzinfo is not None
    assert schema.created_at.utcoffset() is not None