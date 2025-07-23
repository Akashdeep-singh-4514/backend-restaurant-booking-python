from fastapi import APIRouter

from src.controllers.auth_controller import AuthController
from src.controllers.users_controller import UsersController
from src.controllers.admin_controller import AdminController

api_router = APIRouter()
api_router.include_router(AuthController().router, prefix="/v1", tags=["auth"])
api_router.include_router(UsersController().router, prefix="/v1", tags=["users"])
api_router.include_router(AdminController().router, prefix="/v1", tags=["admin"])

__all__ = ["api_router"]
__version__ = "0.1.0"
__author__ = "Akashdeep Singh"
