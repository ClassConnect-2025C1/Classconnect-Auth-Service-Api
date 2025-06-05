from sqlalchemy.orm import Session
from utils.security import hash_password
from models.credential_models import Credential, VerificationPin
from datetime import datetime, timezone, timedelta

def get_user_by_email(db: Session, email: str):
    return db.query(Credential).filter(Credential.email == email).first()

def get_user_by_id(db: Session, user_id: str):
    return db.query(Credential).filter(Credential.id == user_id).first()

def create_user(db: Session, email: str, password: str):
    user = Credential(email=email, hashed_password=hash_password(password), is_verified=False)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def create_verification_pin(db: Session, user_email: str, pin: str, for_password_recovery: bool):
    verification_pin = VerificationPin(email=user_email, pin=pin, created_at=datetime.now(timezone.utc), is_valid=True,
                                       can_change=False, for_password_recovery=for_password_recovery)
    db.add(verification_pin)
    db.commit()
    db.refresh(verification_pin)
    return verification_pin

def get_verification_pin(db: Session, user_email: str):
    return db.query(VerificationPin).filter(VerificationPin.email == user_email).first()


def delete_verification_pin(db: Session, verification_pin: VerificationPin):
    db.delete(verification_pin)
    db.commit()

def set_new_pin(db: Session, user_email: str, new_pin: str, for_password_recovery: bool):
    pin_entry = db.query(VerificationPin).filter(VerificationPin.email == user_email).first()
    if not pin_entry:
        raise
    
    pin_entry.pin = new_pin
    pin_entry.created_at = datetime.now(timezone.utc)
    pin_entry.is_valid = True
    pin_entry.can_change = False
    pin_entry.for_password_recovery = for_password_recovery
    db.commit()
    db.refresh(pin_entry)
    return pin_entry

def set_pin_invalid(db: Session, user_email: str):
    pin_entry = db.query(VerificationPin).filter(VerificationPin.email == user_email).first()
    if not pin_entry:
        raise
    
    pin_entry.is_valid = False
    db.commit()
    db.refresh(pin_entry)

def verify_user(db: Session, user_email: str):
    user = get_user_by_email(db, user_email)
    if not user:
        raise
    
    user.is_verified = True
    db.commit()
    db.refresh(user)

def update_user_password(db: Session, user_email: str, new_password: str):
    user = db.query(Credential).filter(Credential.email == user_email).first()
    if not user:
        raise
    
    user.hashed_password = new_password
    db.commit()
    db.refresh(user)

def pin_can_change(db: Session, verification_pin: VerificationPin):
    verification_pin.can_change = True
    db.commit()
    db.refresh(verification_pin)
    return verification_pin

def increase_incorrect_attempts(db: Session, user_email: str):
    pin_entry = db.query(VerificationPin).filter(VerificationPin.email == user_email).first()
    if not pin_entry:
        raise
    
    pin_entry.incorrect_attempts += 1
    db.commit()
    db.refresh(pin_entry)
    return pin_entry

def block_user(db: Session, user: Credential):
    user.is_locked = True
    user.lock_until = datetime.now(timezone.utc) + timedelta(weeks=260)  # 5 years
    db.commit()
    db.refresh(user)
    return user

def unblock_user(db: Session, user: Credential):
    user.is_locked = False
    user.lock_until = None
    user.failed_attempts = 0
    db.commit()
    db.refresh(user)
    return user

def get_all_users(db: Session):
    return db.query(Credential).all()