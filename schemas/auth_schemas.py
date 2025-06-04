from pydantic import BaseModel, EmailStr
from enum import Enum
from datetime import datetime



class UserRole(str, Enum):
    student = "student"
    teacher = "teacher"


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: str
    last_name: str
    role: UserRole 
    phone: str
    

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer" #This is the standar token type for OAuth2 and JWT


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer" #This is the standar token type for OAuth2 and JWT

class PinRequest(BaseModel):
    userId: str
    pin: str

class VerificationPin(BaseModel):
    email: str
    pin: str
    created_at: datetime

class NotificationRequest(BaseModel):
    email: str
    to: str
    channel: str

class ResendRequest(BaseModel):
    userId: str
    phone: str

class RecoveryRequest(BaseModel):
    userEmail: str

class ChangePasswordRequest(BaseModel):
    userEmail: str
    new_password: str

class PinPasswordRequest(BaseModel):
    userEmail: str
    pin: str

class BlockUserRequest(BaseModel):
    block: bool

class ChangeRoleRequest(BaseModel):
    role: UserRole