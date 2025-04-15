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
    

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer" #This is the standar token type for OAuth2 and JWT

class VerificationPin(BaseModel):
    user_id: str
    pin: str
    created_at: datetime