USERS_ID_ROUTE = "/users/{id}"
USERS_ROUTE = "/users"

from fastapi import APIRouter, Depends, status, Security
from fastapi.responses import JSONResponse

from src.config._database_config import DatabaseConfig
from src.config._logger import logger
from src.schemas.user_schema import UserCreate, UserUpdate
from src.services import UserService
from src.middlewares.jwt_auth import jwt_bearer


class UsersController:
    def __init__(self):
        self.logger = logger
        self.router = APIRouter()
        self.router.add_api_route(
            USERS_ROUTE,
            self.get_users,
            methods=["GET"],
            tags=["users"],
            response_model=None,
        )
        self.router.add_api_route(
            USERS_ID_ROUTE,
            self.get_user_by_id,
            methods=["GET"],
            tags=["users"],
            response_model=None,
        )
        self.router.add_api_route(
            USERS_ROUTE,
            self.create_user,
            methods=["POST"],
            tags=["users"],
            response_model=None,
        )
        self.router.add_api_route(
            USERS_ID_ROUTE,
            self.update_user,
            methods=["PUT"],
            tags=["users"],
            response_model=None,
        )
        self.router.add_api_route(
            USERS_ID_ROUTE,
            self.delete_user,
            methods=["DELETE"],
            tags=["users"],
            response_model=None,
        )
        # Fixed: Added dependencies parameter with JWT authentication
        self.router.add_api_route(
            "/me",
            self.get_current_user_profile,
            methods=["GET"],
            tags=["users"],
            response_model=None,
            dependencies=[Security(jwt_bearer)],  # This makes it show in Swagger
        )

    async def get_users(self, db=Depends(DatabaseConfig.get_db_session)):
        """Fetch all users."""
        try:
            user_service = UserService(db)
            data = await user_service.get_users()
            return {
                "data": data,
                "message": "Users fetched successfully.",
                "status": True,
            }
        except Exception as e:
            self.logger.error(f"Unexpected error fetching users: {e}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "message": "An unexpected error occurred while fetching users.",
                    "status": False,
                    "data": None,
                },
            )

    async def get_user_by_id(self, id: int, db=Depends(DatabaseConfig.get_db_session)):
        """Fetch a user by ID."""
        try:
            user_service = UserService(db)
            user = await user_service.get_user_by_id(id)
            return {
                "data": user,
                "message": "User fetched successfully.",
                "status": True,
            }
        except ValueError as e:
            self.logger.error(f"Error fetching user by ID {id}: {e}")
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={
                    "message": str(e),
                    "status": False,
                    "data": None,
                },
            )
        except Exception as e:
            self.logger.error(f"Unexpected error fetching user by ID {id}: {e}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "message": "An unexpected error occurred while fetching the user.",
                    "status": False,
                    "data": None,
                },
            )

    async def create_user(
        self, user_data: UserCreate, db=Depends(DatabaseConfig.get_db_session)
    ):
        """Create a new user."""
        try:
            user_service = UserService(db)
            user = await user_service.create_user(user_data)
            return {
                "data": user,
                "message": "User created successfully.",
                "status": True,
            }
        except ValueError as ve:
            # Handle business logic errors (like username already taken)
            error_message = str(ve)

            # Map business logic errors to appropriate HTTP status codes
            if (
                "already taken" in error_message.lower()
                or "already registered" in error_message.lower()
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
            self.logger.error(f"Unexpected error creating user: {e}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "message": "An unexpected error occurred while creating the user.",
                    "status": False,
                    "data": None,
                },
            )

    async def update_user(
        self, id: int, user_data: UserUpdate, db=Depends(DatabaseConfig.get_db_session)
    ):
        """Update user details."""
        try:
            user_service = UserService(db)
            user = await user_service.update_user(id, user_data)
            return {
                "data": user,
                "message": "User updated successfully.",
                "status": True,
            }
        except ValueError as e:
            self.logger.error(f"Error updating user with ID {id}: {e}")
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "message": str(e),
                    "status": False,
                    "data": None,
                },
            )
        except Exception as e:
            self.logger.error(f"Unexpected error updating user with ID {id}: {e}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "message": "An unexpected error occurred while updating the user.",
                    "status": False,
                    "data": None,
                },
            )

    async def delete_user(self, id: int, db=Depends(DatabaseConfig.get_db_session)):
        """Delete a user by ID."""
        try:
            user_service = UserService(db)
            await user_service.delete_user(id)
            from starlette.responses import Response

            return Response(status_code=status.HTTP_204_NO_CONTENT)
        except ValueError as e:
            self.logger.error(f"Error deleting user with ID {id}: {e}")
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={
                    "message": str(e),
                    "status": False,
                    "data": None,
                },
            )
        except Exception as e:
            self.logger.error(f"Unexpected error deleting user with ID {id}: {e}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "message": "An unexpected error occurred while deleting the user.",
                    "status": False,
                    "data": None,
                },
            )
    async def get_current_user_profile(
        self, 
        current_user: dict = Security(jwt_bearer),  # Use Security instead of decorator
        db=Depends(DatabaseConfig.get_db_session)
    ):
        """Get current user profile using JWT authentication."""
        try:
            user_service = UserService(db)
            user = await user_service.get_user_by_id(current_user["id"])
            return {
                "data": user,
                "message": "Current user profile fetched successfully.",
                "status": True,
            }
        except Exception as e:
            self.logger.error(f"Error fetching current user profile: {e}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "message": "An unexpected error occurred while fetching the user profile.",
                    "status": False,
                    "data": None,
                },
            )
        