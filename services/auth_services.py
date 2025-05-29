from fastapi import HTTPException
from sqlalchemy.orm import Session
from schemas.auth_schemas import UserRegister, UserLogin, TokenResponse
from repositories.auth_repository import get_user_by_email, create_user, verify_user, update_user_password, increase_incorrect_attempts
from repositories.auth_repository import get_verification_pin, delete_verification_pin, set_pin_invalid, create_verification_pin, set_new_pin, pin_can_change
from utils.security import hash_password, verify_password, create_access_token
from datetime import datetime, timedelta, timezone
import random
from externals.notify_service import send_notification, send_email_recovery
import uuid

PIN_EXPIRATION_SECONDS = 60
MAX_INCORRECT_ATTEMPTS = 3

def register_user(data: UserRegister, db: Session) -> TokenResponse:
    if get_user_by_email(db, data.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    user = create_user(db, data.email, data.password)
    token = create_access_token({"user_email": user.email, "user_id": str(user.id)})
    return TokenResponse(access_token=token)

def login_user(data: UserLogin, db: Session) -> TokenResponse:
    user = get_user_by_email(db, data.email)
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    assert_user_not_verified(user)

    token = create_access_token({"user_email": user.email, "user_id": str(user.id)})
    return TokenResponse(access_token=token)

    
def verify_pin(db: Session, user_email: str, pin: str):
    assert_user_already_verified(db, user_email)

    verification_pin = get_verification_pin(db, user_email)

    assert_pin_is_correct(db, user_email, pin, verification_pin)
    assert_pin_not_expired(db, user_email, verification_pin)
    assert_pin_is_valid(verification_pin)
    assert_pin_not_for_recovery(db, user_email, verification_pin)
    
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
            set_new_pin(db, user_email, pin, False)
        else:
            create_verification_pin(db, user_email, pin, False)
    return result

def send_recovery_link(db: Session, user_email: str):
    user = get_user_by_email(db, user_email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    pin = create_pin()
    result = send_email_recovery(user_email, pin)
    if result:
        if get_verification_pin(db, user_email):
            set_new_pin(db, user_email, pin, True)
        else:
            create_verification_pin(db, user_email, pin, True)
    return user.id, user.email


def change_password(db: Session, user_email: str, new_password: str):
    recovery_link = get_verification_pin(db, user_email)
    if not recovery_link:
        raise HTTPException(status_code=404, detail="Verification pin not found")
    
    assert_pin_for_recovery(db, user_email, recovery_link)
    assert_pin_is_valid(recovery_link)
    assert_pin_can_change(recovery_link)

    hashed_password = hash_password(new_password)
    update_user_password(db, user_email, hashed_password)
    delete_verification_pin(db, recovery_link)
    return True

def verify_recovery_user_pin(db: Session, user_email: str, pin: str):
    verification_pin = get_verification_pin(db, user_email)
    if not verification_pin:
        raise HTTPException(status_code=404, detail="Verification pin not found")
    
    assert_recovery_pin_is_correct(db, user_email, pin, verification_pin)
    assert_pin_not_expired(db, user_email, verification_pin)
    assert_pin_is_valid(verification_pin)
    assert_pin_for_recovery(db, user_email, verification_pin)

    pin_can_change(db, verification_pin)
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

def assert_pin_is_correct(db, user_email, pin, verification_pin):
    if verification_pin.pin != pin:
        make_invalid_pin(db, user_email)
        raise HTTPException(status_code=401, detail="Invalid verification pin")

def assert_pin_not_expired(db, user_email, verification_pin):
    date_now = datetime.now(timezone.utc)
    if verification_pin.created_at + timedelta(seconds=PIN_EXPIRATION_SECONDS) < date_now:
        make_invalid_pin(db, user_email)
        raise HTTPException(status_code=410, detail="Verification pin expired")

def assert_recovery_pin_is_correct(db, user_email, pin, verification_pin):
    if verification_pin.pin != pin:
        if verification_pin.incorrect_attempts < MAX_INCORRECT_ATTEMPTS:
            increase_incorrect_attempts(db, user_email)
            raise HTTPException(status_code=401, detail="Verification pin is not correct, try again")
        else:
            make_invalid_pin(db, user_email)
            raise HTTPException(status_code=401, detail="Invalid verification pin")

        
def assert_pin_is_valid(verification_pin):
    if not verification_pin.is_valid:
        raise HTTPException(status_code=410, detail="Invalid verification pin")
    
def assert_pin_for_recovery(db, user_email, verification_pin):
    if not verification_pin.for_password_recovery:
        make_invalid_pin(db, user_email)
        raise HTTPException(status_code=403, detail="Pin is not for password recovery")

    
def assert_pin_not_for_recovery(db, user_email, verification_pin):
    if verification_pin.for_password_recovery:
        make_invalid_pin(db, user_email)
        raise HTTPException(status_code=403, detail="Pin is for password recovery")
    

    
def assert_pin_can_change(recovery_link):
    if recovery_link.can_change == False:
        raise HTTPException(status_code=403, detail="Pin cannot be used to change password")
    
def create_pin():
    # This function should create a new pin and return it
    # For now, we will just return a dummy pin
    return ''.join(random.choices('0123456789', k=6))