import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from schemas.auth_schemas import UserRegister, UserLogin, TokenResponse
from dbConfig.session import get_db
from models.credential_models import Credential
from utils.security import decode_token
from utils.security import hash_password, verify_password, create_access_token, get_current_user
from fastapi.security import OAuth2PasswordBearer
import httpx


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=TokenResponse)
def register(data: UserRegister, db: Session = Depends(get_db)):
    if db.query(Credential).filter(Credential.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # for the momment i create user id here
    user_id = uuid.uuid4()

    user = Credential(id=user_id ,email=data.email, hashed_password=hash_password(data.password))
    db.add(user)
    db.commit()
    db.refresh(user)

    # Sent to user service
    profile_data = {
        "id": str(user_id),
        "email": data.email,
        "name": data.name,
        "last_name": data.last_name,
        "role": data.role,
    }

    try:
        response = httpx.post("http://localhost:8001/users/profile", json=profile_data)
        response.raise_for_status()

    except httpx.HTTPError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating profile: {e}")
    

    token = create_access_token({"sub": str(user.id),"email": user.email})
    return {"access_token": token}

@router.post("/login", response_model=TokenResponse)
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(Credential).filter(Credential.email == data.email).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": str(user.id), "email": user.email})
    return {"access_token": token}

@router.get("/protected")
def protected_route(current_user=Depends(get_current_user)):
    return {"message": f"Hola {current_user['email']}, estás autenticado"}

