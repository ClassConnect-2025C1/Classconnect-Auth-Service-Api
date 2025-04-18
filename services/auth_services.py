from fastapi import HTTPException
from sqlalchemy.orm import Session
from schemas.auth_schemas import UserRegister, UserLogin, TokenResponse
from repositories.auth_repository import get_user_by_email, create_user, verify_user, get_user_by_id
from repositories.auth_repository import get_verification_pin, delete_verification_pin, set_pin_invalid, create_verification_pin
from utils.security import hash_password, verify_password, create_access_token
from datetime import datetime, timedelta, timezone
import random
from externals.notify_service import send_notification

PIN_EXPIRATION_MINUTES = 0.2

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

    
def verify_pin(db: Session, user_id: str, pin: str):
    assert_user_already_verified(db, user_id)

    verification_pin = get_verification_pin(db, user_id)

    assert_pin_is_not_correct(db, user_id, pin, verification_pin)
    assert_pin_not_expired(db, user_id, verification_pin)
    
    delete_verification_pin(db, verification_pin)
    make_user_verified(db, user_id)
    return True

def notify_user(db: Session, user_id: str, to: str, channel: str):
    pin = create_pin()
    result = send_notification(to, pin, channel)
    if result:
        create_verification_pin(db, user_id, pin)
    return result


########### UTILS ###########

def assert_user_not_verified(user):
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="User not verified")

def assert_user_already_verified(db, user_id):
    user = get_user_by_id(db, user_id)
    if user and user.is_verified:
        raise HTTPException(status_code=404, detail="User already verified")

def make_invalid_pin(db: Session ,user_id: str):
    set_pin_invalid(db, user_id)

def make_user_verified(db: Session, user_id: str):
    verify_user(db, user_id)

def assert_pin_is_not_correct(db, user_id, pin, verification_pin):
    if verification_pin.pin != pin:
        make_invalid_pin(db, user_id)
        raise HTTPException(status_code=401, detail="Invalid verification pin")

def assert_pin_not_expired(db, user_id, verification_pin):
    date_now = datetime.now(timezone.utc)
    if verification_pin.created_at + timedelta(minutes=PIN_EXPIRATION_MINUTES) < date_now:
        make_invalid_pin(db, user_id)
        raise HTTPException(status_code=410, detail="Verification pin expired")
    
def create_pin():
    # This function should create a new pin and return it
    # For now, we will just return a dummy pin
    return ''.join(random.choices('0123456789', k=6))