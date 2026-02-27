from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    job_title: Optional[str] = None
    department: Optional[str] = None
    role: Optional[str] = "employee" # Platform Admin, Tenant Admin, Manager, Employee
    organization_id: int

class UserCreate(UserBase):
    password: str
    manager_id: Optional[int] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    manager_id: Optional[int] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[int] = None
    organization_id: Optional[int] = None
    role: Optional[str] = None
