from datetime import datetime, timedelta
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
import httpx


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
    argentina_tz = pytz.timezone('America/Argentina/Buenos_Aires')

    user = db.query(Credential).filter(Credential.email == data.email).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid Email"
        )

    if user.lock_until and user.lock_until.tzinfo is None:
        user.lock_until = argentina_tz.localize(user.lock_until)

    now = datetime.now(argentina_tz)

    if user.is_locked and user.lock_until > now:
        raise HTTPException(
            status_code=403,
            detail={
                "type": "account_locked",
                "message": f"The account is locked until {user.lock_until.strftime('%Y-%m-%d %H:%M:%S')}",
                "lock_until": user.lock_until.isoformat()
            }
        )

    if not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail={
                "type": "invalid_password",
                "message": "Invalid password"
            }
        )

    # Reset lock status if login is successful
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
    picture = user_info.get("picture", "")  # URL de la foto de perfil

    if not email:
        raise HTTPException(status_code=400, detail="No se pudo obtener el correo electrónico del usuario de Google.")

    # Buscar al usuario en la base de datos
    user = db.query(Credential).filter(Credential.email == email).first()

    if not user:
        user_id = uuid.uuid4()
        user = Credential(id=user_id, email=email, hashed_password="")  # Contraseña vacía
        db.add(user)
        db.commit()
        db.refresh(user)

        # Crear perfil en el microservicio de user
        profile_data = {
            "id": str(user_id),
            "email": email,
            "name": name,
            "last_name": last_name,
            "role": "student",
            "picture": picture,  # Nuevo: incluir foto de perfil
        }

        try:
            response = httpx.post("http://localhost:8001/users/profile", json=profile_data)
            response.raise_for_status()
        except httpx.HTTPError as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error creando el perfil: {e}")

    token = create_access_token({"sub": str(user.id), "email": user.email})
    return {"access_token": token}




@router.get("/protected")
def protected_route(current_user=Depends(get_current_user)):
    return {"message": f"Hola {current_user['email']}, estás autenticado"}


@router.post("/verify")
def verify_user(request: PinRequest, db: Session = Depends(get_db)):
    verify_pin(db, request.user_id, request.pin)
    return {"message": "User verified successfully"}

@router.post("/notify")
def notify_user(request: NotificationRequest, db: Session = Depends(get_db), ):
    notify_user(db, request.user_id, request.to, request.channel)
    return {"message": "Notification sent successfully"}