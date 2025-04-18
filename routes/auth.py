from datetime import datetime, timedelta, timezone
import pytz
import uuid
from fastapi import APIRouter, Depends, HTTPException, requests, status
from sqlalchemy.orm import Session
from schemas.auth_schemas import UserRegister, UserLogin, TokenResponse, PinRequest, NotificationRequest
from dbConfig.session import get_db
from models.credential_models import Credential
from utils.security import decode_token
from utils.security import hash_password, verify_password, create_access_token, get_current_user
from fastapi.security import OAuth2PasswordBearer
from services.auth_services import verify_pin, notify_user
from dbConfig.session import get_db
import httpx
from dotenv import load_dotenv
import os
load_dotenv()
USERS_SERVICE_URL = os.getenv("USERS_SERVICE_URL", "http://localhost:8001")

MAX_FAILED_ATTEMPTS = 3
LOCK_TIME = timedelta(minutes=0.3)

router = APIRouter(prefix="/auth", tags=["auth"])

from fastapi import HTTPException, status
from fastapi.responses import JSONResponse

@router.post("/register", response_model=TokenResponse)
def register(data: UserRegister, db: Session = Depends(get_db)):
    if db.query(Credential).filter(Credential.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    try:
        user_id = uuid.uuid4()
        user = Credential(id=user_id, email=data.email, hashed_password=hash_password(data.password))
        db.add(user)
        db.commit()
        db.refresh(user)

   
        profile_data = {
            "id": str(user_id),
            "email": data.email,
            "name": data.name,
            "last_name": data.last_name,
            "role": data.role,
            "phone": data.phone,
        }

        response = httpx.post(f"{USERS_SERVICE_URL}/users/profile", json=profile_data)
        response.raise_for_status()

    except httpx.HTTPStatusError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating profile: {str(e)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

    token = create_access_token({"sub": str(user.id), "email": user.email})
    return {"access_token": token}


@router.post("/login", response_model=TokenResponse)
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(Credential).filter(Credential.email == data.email).first()
    buenos_aires_tz = pytz.timezone('America/Argentina/Buenos_Aires')
    now = datetime.now(buenos_aires_tz)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid Email"
        )
    """ 
    if not user.is_verified:
        raise HTTPException(
            status_code=401,
            detail="User not verified"
        )
    """


    if user.lock_until and user.lock_until.tzinfo is None:
        user.lock_until = buenos_aires_tz.localize(user.lock_until)

   
    if user.is_locked and user.lock_until and now > user.lock_until:
        user.is_locked = False
        user.failed_attempts = 0
        user.lock_until = None
        db.commit()


    if user.failed_attempts >= MAX_FAILED_ATTEMPTS:
        user.is_locked = True
        user.lock_until = now + LOCK_TIME
        db.commit()
        db.refresh(user)

        lock_until_arg = user.lock_until.strftime('%Y-%m-%d %H:%M:%S')

        raise HTTPException(
            status_code=401,
            detail=f"Too many failed attempts. Your account has been locked until {lock_until_arg} (Argentina Time)."
        )


    if not verify_password(data.password, user.hashed_password):
        user.failed_attempts += 1
        user.last_failed_login = now

        if user.failed_attempts >= MAX_FAILED_ATTEMPTS:
            user.is_locked = True
            user.lock_until = now + LOCK_TIME

        db.commit()
        db.refresh(user)
        raise HTTPException(
            status_code=401,
            detail="Invalid password"
        )

   
    user.failed_attempts = 0
    user.last_failed_login = None
    user.is_locked = False
    user.lock_until = None
    db.commit()

    token = create_access_token({"sub": str(user.id), "email": user.email})
    return {"access_token": token}


@router.post("/google", response_model=TokenResponse)
def login_with_google(data: dict, db: Session = Depends(get_db)):
    access_token = data.get("access_token")
    if not access_token:
        raise HTTPException(status_code=400, detail="Token de Google no proporcionado.")

    try:
        google_response = requests.get(
            f"https://www.googleapis.com/oauth2/v1/userinfo?alt=json&access_token={access_token}",
            timeout=5
        )
    except requests.RequestException:
        raise HTTPException(status_code=503, detail="No se pudo conectar con Google. Intentalo de nuevo más tarde.")

    if google_response.status_code == 401:
        raise HTTPException(status_code=401, detail="Token de Google inválido o expirado.")
    elif google_response.status_code != 200:
        raise HTTPException(status_code=500, detail="Error inesperado al validar el token de Google.")

    user_info = google_response.json()
    email = user_info.get("email")
    name = user_info.get("given_name", "")
    last_name = user_info.get("family_name", "")
    picture = user_info.get("picture", "")  

    if not email:
        raise HTTPException(status_code=400, detail="No se pudo obtener el correo electrónico del usuario de Google.")

    # Buscar al usuario en la base de datos
    user = db.query(Credential).filter(Credential.email == email).first()

    if not user:
        user_id = uuid.uuid4()
        user = Credential(id=user_id, email=email, hashed_password="")  
        db.add(user)
        db.commit()
        db.refresh(user)

    
        profile_data = {
            "id": str(user_id),
            "email": email,
            "name": name,
            "last_name": last_name,
            "role": "student",
            "picture": picture,  # Nuevo: incluir foto de perfi
        }

        try:
            response = httpx.post(f"{USERS_SERVICE_URL}/users/profile", json=profile_data)
            response.raise_for_status()
        except httpx.HTTPError as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error creando el perfil: {e}")

    token = create_access_token({"sub": str(user.id), "email": user.email})
    return {"access_token": token}




@router.get("/protected")
def protected_route(current_user=Depends(get_current_user)):
    if current_user["is_locked"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Cuenta bloqueada. Intenta nuevamente más tarde.",
        )
    return {"message": f"Hola {current_user['email']}, estás autenticado."}


@router.post("/verification")
def verify_user(request: PinRequest, db: Session = Depends(get_db)):
    verify_pin(db, request.email, request.pin)
    return {"message": "User verified successfully"}

@router.post("/notification")
def notification_user(request: NotificationRequest, db: Session = Depends(get_db), ):
    notify_user(db, request.email, request.to, request.channel)
    return {"message": "Notification sent successfully"}