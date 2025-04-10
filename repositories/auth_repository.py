from sqlalchemy.orm import Session
from controller.service_controller import Credential  # tu modelo SQLAlchemy
from utils.security import hash_password

def get_user_by_email(db: Session, email: str):
    return db.query(Credential).filter(Credential.email == email).first()

def create_user(db: Session, email: str, password: str):
    user = Credential(email=email, hashed_password=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
