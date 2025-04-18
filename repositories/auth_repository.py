from sqlalchemy.orm import Session
from utils.security import hash_password
from models.credential_models import Credential, VerificationPin
from datetime import datetime, timezone

def get_user_by_email(db: Session, email: str):
    return db.query(Credential).filter(Credential.email == email).first()

def create_user(db: Session, email: str, password: str):
    user = Credential(email=email, hashed_password=hash_password(password), is_verified=False)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def create_verification_pin(db: Session, user_email: str, pin: str):
    verification_pin = VerificationPin(email=user_email, pin=pin, created_at=datetime.now(timezone.utc), is_valid=True)
    db.add(verification_pin)
    db.commit()
    db.refresh(verification_pin)
    return verification_pin

def get_verification_pin(db: Session, user_email: str):
    return db.query(VerificationPin).filter(VerificationPin.email == user_email).first()

def get_user_by_id(db: Session, user_id: str):
    return db.query(Credential).filter(Credential.id == user_id).first()

def delete_verification_pin(db: Session, verification_pin: VerificationPin):
    db.delete(verification_pin)
    db.commit()

def set_pin_invalid(db: Session, user_email: str):
    pin_entry = db.query(VerificationPin).filter_by(email=user_email).first()
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