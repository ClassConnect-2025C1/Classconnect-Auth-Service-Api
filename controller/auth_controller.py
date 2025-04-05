from pydantic import BaseModel, EmailStr, Field

class Login(BaseModel):
    username:str
    password:str

class Register(BaseModel):
    email:EmailStr
    password:str
 
