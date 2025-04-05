from pydantic import BaseModel, EmailStr
from uuid import UUID

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"