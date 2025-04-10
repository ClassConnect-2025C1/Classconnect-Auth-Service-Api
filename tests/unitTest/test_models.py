import pytest
from pydantic import ValidationError
from schemas import auth_schemas

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
    
    user = auth_schemas.UserRegister(email="user@example.com", password="password123", name="John", last_name="Doe")
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
