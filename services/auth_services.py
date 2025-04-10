from fastapi import HTTPException
from sqlalchemy.orm import Session
from schemas.auth_schemas import UserRegister, UserLogin, TokenResponse
from repositories.auth_repository import get_user_by_email, create_user
from utils.security import hash_password, verify_password, create_access_token

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

    token = create_access_token({"sub": user.email, "current_user_id": str(user.id)})
    return TokenResponse(access_token=token)
