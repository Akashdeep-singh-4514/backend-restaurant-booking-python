from pydantic import BaseModel
from src.schemas.user_schema import UserResponse

class AuthResponse(BaseModel):
    token: str
    user: UserResponse