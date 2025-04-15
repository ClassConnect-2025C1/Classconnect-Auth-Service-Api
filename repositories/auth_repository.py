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

def create_verification_pin(db: Session, user_id: str, pin: str):
    verification_pin = VerificationPin(user_id=user_id, pin=pin, created_at=datetime.now(timezone.utc) )
    db.add(verification_pin)
    db.commit()
    db.refresh(verification_pin)
    return verification_pin

def get_verification_pin(db: Session, user_id: str):
    return db.query(VerificationPin).filter(VerificationPin.user_id == user_id).first()