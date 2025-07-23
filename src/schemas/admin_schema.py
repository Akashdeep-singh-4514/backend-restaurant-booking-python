from datetime import datetime
from pydantic import BaseModel
from src.constants import AdminRole

class AdminCreate(BaseModel):
    username: str
    email: str
    password: str
    role: AdminRole
    is_active: bool = True

class Admin(BaseModel):
    id: int
    username: str
    email: str
    role: AdminRole
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

class AdminUpdate(BaseModel):
    username: str
    email: str
    role: AdminRole
    is_active: bool = True

class AdminLogin(BaseModel):
    username: str
    password: str

class AdminResponse(BaseModel):
    id: int
    username: str
    email: str
    role: AdminRole
    is_active: bool = True
    created_at: datetime
    updated_at: datetime