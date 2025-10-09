from pydantic import BaseModel, EmailStr
from datetime import datetime

# Shared base for all admin schemas
class AdminBase(BaseModel):
    name: str
    email: EmailStr

# Schema used for creating a new admin (e.g. signup)
class AdminCreate(AdminBase):
    password: str

# Schema used for login
class AdminLogin(BaseModel):
    email: EmailStr
    password: str

# Schema returned in responses
class AdminOut(AdminBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"