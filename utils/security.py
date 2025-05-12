from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
import os
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose.exceptions import ExpiredSignatureError
from sqlalchemy.orm import Session
from dbConfig.session import get_db

from models.credential_models import Credential


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

SECRET_KEY = os.getenv("SECRET_KEY", "supersecret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 200
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="La sesión ha expirado. Por favor, inicia sesión de nuevo."
        )
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Token inválido."
        )


def get_token_expiry():
    return timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(token)
        user_id: str = payload.get("user_id")
        if user_id is None:
            raise credentials_exception

        # Verificar si la cuenta está bloqueada
        user = db.query(Credential).filter(Credential.id == user_id).first()
        if user.is_locked and user.lock_until > datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Cuenta bloqueada. Intenta nuevamente más tarde.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return {"id": user_id, "email": payload.get("email"), "is_locked": user.is_locked, "lock_until": user.lock_until}

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado",  
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError:
        raise credentials_exception