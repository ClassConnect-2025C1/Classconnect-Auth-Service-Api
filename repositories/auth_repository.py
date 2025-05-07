from sqlalchemy.orm import Session
from utils.security import hash_password
from models.credential_models import Credential, VerificationPin, RecoveryLink
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


def delete_verification_pin(db: Session, verification_pin: VerificationPin):
    db.delete(verification_pin)
    db.commit()

def set_new_pin(db: Session, user_email: str, new_pin: str):
    pin_entry = db.query(VerificationPin).filter(VerificationPin.email == user_email).first()
    if not pin_entry:
        raise
    
    pin_entry.pin = new_pin
    pin_entry.created_at = datetime.now(timezone.utc)
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

def set_recovery_link(db: Session, user_id: str, recovery_uuid: str):
    user = db.query(Credential).filter(Credential.id == user_id).first()
    if not user:
        recovery_link = RecoveryLink(user_id=user_id, recovery_link=recovery_uuid, created_at=datetime.now(timezone.utc))
        db.add(recovery_link)
        db.commit()
        db.refresh(recovery_link)
        return recovery_link
    
    recovery_link = db.query(RecoveryLink).filter(RecoveryLink.user_id == user_id).first()
    recovery_link.recovery_link = recovery_uuid
    recovery_link.created_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(recovery_link)
    return recovery_link

def get_recovery_link(db: Session, uuid: str):
    return db.query(RecoveryLink).filter(RecoveryLink.recovery_link == uuid).first()

def delete_recovery_link(db: Session, recovery_link: RecoveryLink):
    db.delete(recovery_link)
    db.commit()

def update_user_password(db: Session, user_id: str, new_password: str):
    user = db.query(Credential).filter(Credential.id == user_id).first()
    if not user:
        raise
    
    user.hashed_password = new_password
    db.commit()
    db.refresh(user)
