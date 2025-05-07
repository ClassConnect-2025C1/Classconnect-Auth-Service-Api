from fastapi import HTTPException
from sqlalchemy.orm import Session
from schemas.auth_schemas import UserRegister, UserLogin, TokenResponse
from repositories.auth_repository import get_user_by_email, create_user, verify_user, update_user_password
from repositories.auth_repository import get_verification_pin, delete_verification_pin, set_pin_invalid, create_verification_pin, set_new_pin
from repositories.auth_repository import set_recovery_link, get_recovery_link, delete_recovery_link
from utils.security import hash_password, verify_password, create_access_token
from datetime import datetime, timedelta, timezone
import random
from externals.notify_service import send_notification, send_email_recovery
import uuid

PIN_EXPIRATION_SECONDS = 20

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

    
def verify_pin(db: Session, user_email: str, pin: str):
    assert_user_already_verified(db, user_email)

    verification_pin = get_verification_pin(db, user_email)

    assert_pin_is_not_correct(db, user_email, pin, verification_pin)
    assert_pin_not_expired(db, user_email, verification_pin)
    
    delete_verification_pin(db, verification_pin)
    make_user_verified(db, user_email)
    return True

def notify_user(db: Session, user_email: str, to: str, channel: str):
    user = get_user_by_email(db, user_email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    pin = create_pin()
    result = send_notification(to, pin, channel)
    if result:
        if get_verification_pin(db, user_email):
            set_new_pin(db, user_email, pin)
        else:
            create_verification_pin(db, user_email, pin)
    return result

def send_recovery_link(db: Session, user_email: str):
    user = get_user_by_email(db, user_email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    recovery_uuid = str(uuid.uuid4())
    result = send_email_recovery(user_email, recovery_uuid)
    set_recovery_link(db, user.id, recovery_uuid)
    return result

def change_password(db: Session, uuid: str, new_password: str):
    recovery_link = get_recovery_link(db, uuid)
    if not recovery_link:
        raise HTTPException(status_code=404, detail="Recovery link not found")
    if recovery_link.created_at + timedelta(seconds=PIN_EXPIRATION_SECONDS) < datetime.now(timezone.utc):
        delete_recovery_link(db, recovery_link)
        raise HTTPException(status_code=410, detail="Recovery link expired")
    user_id = recovery_link.user_id
    hashed_password = hash_password(new_password)
    update_user_password(db, user_id, hashed_password)
    delete_verification_pin(db, recovery_link)
    return True


########### UTILS ###########

def assert_user_not_verified(user):
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="User not verified")

def assert_user_already_verified(db, user_email):
    user = get_user_by_email(db, user_email)
    if user and user.is_verified:
        raise HTTPException(status_code=404, detail="User already verified")

def make_invalid_pin(db: Session ,user_email: str):
    set_pin_invalid(db, user_email)

def make_user_verified(db: Session, user_email: str):
    verify_user(db, user_email)

def assert_pin_is_not_correct(db, user_email, pin, verification_pin):
    if verification_pin.pin != pin:
        make_invalid_pin(db, user_email)
        raise HTTPException(status_code=401, detail="Invalid verification pin")

def assert_pin_not_expired(db, user_email, verification_pin):
    date_now = datetime.now(timezone.utc)
    if verification_pin.created_at + timedelta(seconds=PIN_EXPIRATION_SECONDS) < date_now:
        make_invalid_pin(db, user_email)
        raise HTTPException(status_code=410, detail="Verification pin expired")
    
def create_pin():
    # This function should create a new pin and return it
    # For now, we will just return a dummy pin
    return ''.join(random.choices('0123456789', k=6))