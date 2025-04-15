from sqlalchemy.orm import Session
from utils.security import hash_password
from models.credential_models import Credential

def get_user_by_email(db: Session, email: str):
    return db.query(Credential).filter(Credential.email == email).first()

def create_user(db: Session, email: str, password: str):
    user = Credential(email=email, hashed_password=hash_password(password), is_verified=False)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
