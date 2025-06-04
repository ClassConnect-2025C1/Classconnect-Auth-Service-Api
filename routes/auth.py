import os
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
from fastapi import HTTPException, status
from datetime import datetime, timedelta, timezone
import pytz
import uuid
from fastapi import APIRouter, Depends, HTTPException, requests, status, Query
from sqlalchemy.orm import Session
from schemas.auth_schemas import UserRegister, UserLogin, TokenResponse, BlockUserRequest, ChangeRoleRequest
from schemas.auth_schemas import PinRequest, NotificationRequest, ResendRequest, RecoveryRequest, ChangePasswordRequest, PinPasswordRequest
from dbConfig.session import get_db
from models.credential_models import Credential
from utils.security import decode_token
from utils.security import hash_password, verify_password, create_access_token, get_current_user
from fastapi.security import OAuth2PasswordBearer
from services.auth_services import verify_pin, notify_user, send_recovery_link, change_password, verify_recovery_user_pin, block_user_service, change_user_role_service
from dbConfig.session import get_db
import httpx
import firebase_admin
from firebase_admin import credentials, auth
from dotenv import load_dotenv
import os

load_dotenv()
USERS_SERVICE_URL = os.getenv("URL_USERS", "http://localhost:8001")

MAX_FAILED_ATTEMPTS = 3
LOCK_TIME = timedelta(minutes=0.3)
CHANNEL = "sms"

cred = credentials.Certificate("firebaseKeys.json")
firebase_admin.initialize_app(cred)
router = APIRouter(prefix="/auth", tags=["auth"])


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

        if not notify_user(db, data.email, data.phone, CHANNEL):
            raise HTTPException(status_code=500, detail="Error sending notification")

        response = httpx.post(f"{USERS_SERVICE_URL}/users/profile", json=profile_data)
        response.raise_for_status()

    except httpx.HTTPStatusError as e:
        print(f"Error creating profile: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating profile: {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

    token = create_access_token({"user_id": str(user.id), "email": user.email})
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

    if not user.is_verified:
        raise HTTPException(
            status_code=401,
            detail="User not verified"
        )


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

    token = create_access_token({"user_id": str(user.id), "email": user.email})
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

 
            response = httpx.post(f"{USERS_SERVICE_URL}/users/google_profile", json=profile_data)

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
    token = create_access_token({"user_id": str(user.id), "email": user.email})
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
    user = db.query(Credential).filter(Credential.id == request.userId).first()
    verify_pin(db, user.email, request.pin)
    return {"message": "User verified successfully"}

@router.post("/notification")
def notification_user(request: NotificationRequest, db: Session = Depends(get_db), ):
    notify_user(db, request.email, request.to, request.channel)
    return {"message": "Notification sent successfully"}

@router.post("/verification/resend")
def resend_pin(request: ResendRequest, db: Session = Depends(get_db)):
    user = db.query(Credential).filter(Credential.id == request.userId).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.is_verified:
        raise HTTPException(status_code=400, detail="User already verified")
    print(request.phone)
    notify_user(db, user.email, request.phone, CHANNEL)
    return {"message": "Verification code resent successfully"}

@router.post("/recovery-password")
def recovery_password(request: RecoveryRequest, db: Session = Depends(get_db)):
    send_recovery_link(db, request.userEmail)
    return {"message": "Password recovery link sent successfully"}

@router.post("/recovery-password/verify-pin")
def verify_recovery_pin(request: PinPasswordRequest, db: Session = Depends(get_db)):
    verify_recovery_user_pin(db, request.userEmail, request.pin)
    return {"message": "Pin verified successfully"}

@router.patch("/recovery-password/change-password")
def change_user_password(request: ChangePasswordRequest, db: Session = Depends(get_db)):
    change_password(db, request.userEmail, request.new_password)
    return {"message": "Password changed successfully"}

@router.patch("/block/{user_id}")
def block_user(user_id: str, request: BlockUserRequest,db: Session = Depends(get_db)):
    block_user_service(db, user_id, request.block)
    return {"message": f"User {user_id} {'blocked' if request.block else 'unblocked'} successfully"}

@router.patch("/rol/{user_id}")
def change_user_role(user_id: str, request: ChangeRoleRequest, db: Session = Depends(get_db)):
    change_user_role_service(db, user_id, request.role)
    return {"message": f"User {user_id} role changed to {request.role} successfully"}