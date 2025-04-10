from pydantic import BaseModel, EmailStr

class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: str
    last_name: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer" #This is the standar token type for OAuth2 and JWT