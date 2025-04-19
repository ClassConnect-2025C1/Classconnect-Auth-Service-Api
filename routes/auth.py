from fastapi.responses import JSONResponse
from fastapi import HTTPException, status
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
import firebase_admin
from firebase_admin import credentials, auth
MAX_FAILED_ATTEMPTS = 3
LOCK_TIME = timedelta(minutes=0.3)

cred = credentials.Certificate("firebaseKeys.json")
firebase_admin.initialize_app(cred)
router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse)
def register(data: UserRegister, db: Session = Depends(get_db)):
    if db.query(Credential).filter(Credential.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    try:
        user_id = uuid.uuid4()
        user = Credential(id=user_id, email=data.email,
                          hashed_password=hash_password(data.password))
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

        response = httpx.post(
            "http://localhost:8001/users/profile", json=profile_data)
        response.raise_for_status()

    except httpx.HTTPStatusError as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error creating profile: {str(e)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Unexpected error: {str(e)}")

    token = create_access_token({"sub": str(user.id), "email": user.email})
    return {"access_token": token}


def verify_google_token(google_token: str) -> dict:
    try:
        # Verifica el ID Token de Firebase
        decoded_token = auth.verify_id_token(google_token)
        # Imprime el token para ver qué datos trae
        print("Token decodificado:", decoded_token)
        return decoded_token
    except auth.InvalidIdTokenError:
        raise HTTPException(status_code=401, detail="Invalid Google token")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al verificar el token: {str(e)}")


@router.post("/google", response_model=TokenResponse)
def login_with_google(data: dict, db: Session = Depends(get_db)):
    google_token = data.get("google_token")
    if not google_token:
        raise HTTPException(status_code=400, detail="Google token is required")

    google_info = verify_google_token(google_token)

    
    email = google_info.get("email")
    name = google_info.get("name")
    picture = google_info.get("picture")

    if not all([email, name]):
        raise HTTPException(status_code=400, detail="Incomplete Google data")

    name_parts = name.split(" ")
    first_name = name_parts[0]
    last_name = " ".join(name_parts[1:])

    role = data.get("role", "student")
    phone = data.get("phone")

    user = db.query(Credential).filter(Credential.email == email).first()

    if not user:
        try:
            # Si el usuario no existe, lo creamos
            user_id = uuid.uuid4()
            user = Credential(id=user_id, email=email, hashed_password=None)
            db.add(user)
            db.commit()
            db.refresh(user)

            # Datos para crear el perfil
            profile_data = {
                "id": str(user_id),
                "email": email,
                "name": first_name,          
                "last_name": last_name,
                "role": role,
                "phone": phone,
                "photo_url": picture            
            }

            response = httpx.post(
                "http://localhost:8001/users/google_profile", json=profile_data)
            response.raise_for_status()

        except httpx.HTTPStatusError as e:
            db.rollback()  
            raise HTTPException(
                status_code=500, detail=f"Error creating profile: {str(e)}")
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=500, detail=f"Unexpected error: {str(e)}")

    # Paso 5: Generamos el token JWT y lo devolvemos
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
