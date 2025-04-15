from fastapi import HTTPException
from sqlalchemy.orm import Session
from schemas.auth_schemas import UserRegister, UserLogin, TokenResponse
from repositories.auth_repository import get_user_by_email, create_user, verify_user
from repositories.auth_repository import get_verification_pin, get_user_by_id, delete_verification_pin, set_pin_invalid
from utils.security import hash_password, verify_password, create_access_token
from datetime import datetime, timedelta, timezone

PIN_EXPIRATION_MINUTES = 10

def register_user(data: UserRegister, db: Session) -> TokenResponse:
    if get_user_by_email(db, data.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    user = create_user(db, data.email, data.password)
    token = create_access_token({"sub": user.email})
    return TokenResponse(access_token=token)

def login_user(data: UserLogin, db: Session) -> TokenResponse:
    user = get_user_by_email(db, data.email)
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    assert_user_not_verified(user)

    token = create_access_token({"sub": user.email, "current_user_id": str(user.id)})
    return TokenResponse(access_token=token)


def assert_user_not_verified(user):
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="User not verified")
    
def verify_pin(db: Session, user_id: str, pin: str):
    assert_user_already_verified(db, user_id)

    verification_pin = get_verification_pin(db, user_id)

    if verification_pin.pin != pin:
        make_invalid_pin(db, user_id)
        raise HTTPException(status_code=401, detail="Invalid verification pin")
    
    date_now = datetime.now(timezone.utc)
    if verification_pin.created_at + timedelta(minutes=PIN_EXPIRATION_MINUTES) < date_now:
        make_invalid_pin(db, user_id)
        raise HTTPException(status_code=410, detail="Verification pin expired")
    
    delete_verification_pin(db, verification_pin)
    make_user_verified(db, user_id)
    return True

def assert_user_already_verified(db, user_id):
    user = get_user_by_id(db, user_id)
    if user and user.is_verified:
        raise HTTPException(status_code=404, detail="User already verified")

def make_invalid_pin(db: Session ,user_id: str):
    set_pin_invalid(db, user_id)

def make_user_verified(db: Session, user_id: str):
    verify_user(db, user_id)