from pydantic import BaseModel, Field
from uuid import UUID

class Register(BaseModel):
    email: str =Emails
    password: str = Field(..., max_length=50)
    created_at: str = Field(default=None)

   