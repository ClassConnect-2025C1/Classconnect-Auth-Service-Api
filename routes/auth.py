from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

from app.db.session import get_db
from app.models.credential import Credential
from app.schemas.auth import RegisterInput, LoginInput, TokenResponse
from app.core.security import hash_password, verify_password, create_access_token, decode_token

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

@router.post("/register", status_code=201)
def register_user(data: RegisterInput, db: Session = Depends(get_db)):
    if db.query(Credential).filter_by(email=data.email).first():
        raise HTTPException(status_code=400, detail="Email ya registrado")
    credential = Credential(
        user_id=data.user_id,
        email=data.email,
        password_hash=hash_password(data.password)
    )
    db.add(credential)
    db.commit()
    return {"message": "Usuario registrado correctamente"}

@router.post("/login", response_model=TokenResponse)
def login(data: LoginInput, db: Session = Depends(get_db)):
    user = db.query(Credential).filter_by(email=data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    
    token = create_access_token({"sub": str(user.user_id), "email": user.email})
    return TokenResponse(access_token=token)

@router.get("/me")
def get_me(token: str = Depends(oauth2_scheme)):
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido")
    return {"user_id": payload.get("sub"), "email": payload.get("email")}
