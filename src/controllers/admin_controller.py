from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from src.config._database_config import DatabaseConfig
from src.config._logger import logger
from src.schemas.admin_schema import AdminCreate
from src.services import AdminService

class AdminController:
    def __init__(self):
        self.logger = logger
        self.router = APIRouter()
        self.router.add_api_route("/admin", self.create_admin, methods=["POST"], status_code=status.HTTP_201_CREATED)


    async def create_admin(self, admin: AdminCreate, db=Depends(DatabaseConfig.get_db_session)):
        try:
            admin_service = AdminService(db)
            admin = await admin_service.create_admin(admin)
            return JSONResponse(status_code=status.HTTP_201_CREATED, content=admin.model_dump())
        except ValueError as e:
            error_message = str(e)
            self.logger.error(f"Error creating admin: {error_message}")
            if (
                "already exists" in error_message.lower()
            ):
                return JSONResponse(
                    status_code=status.HTTP_409_CONFLICT,
                    content={"message": error_message, "status": False},
                )
            elif (
                "validation failed" in error_message.lower()
                or "invalid" in error_message.lower()
            ):
                # Generic validation/business logic error
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={"message": error_message, "status": False},
                )
        except Exception as e:
            self.logger.error(f"Error creating admin: {e}")
            return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": "Internal server error", "status": False})
        
        