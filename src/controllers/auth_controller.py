from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from src.config._database_config import DatabaseConfig
from src.config._logger import logger
from src.schemas.user_schema import UserCreate, UserLogin, UserResponse, UserUpdate
from src.services import AuthService


class AuthController:
    def __init__(self):
        self.logger = logger
        self.router = APIRouter()
        self.router.add_api_route(
            "auth/signup",
            self.signup,
            methods=["POST"],
            tags=["auth"],
            response_model=None,
        )
        self.router.add_api_route(
            "auth/signin",
            self.signin,
            methods=["POST"],
            tags=["auth"],
            response_model=None,
        )

    async def signup(
        self, user_data: UserCreate, db=Depends(DatabaseConfig.get_db_session)
    ):
        """Create a new user."""
        try:
            auth_service = AuthService(db)
            user = await auth_service.signup(user_data)
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
            # Handle unexpected errors
            self.logger.error(f"Unexpected error creating user: {e}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "message": "An unexpected error occurred while creating the user.",
                    "status": False,
                },
            )

    async def signin(
        self, user_data: UserLogin, db=Depends(DatabaseConfig.get_db_session)
    ):
        """User login."""
        try:
            auth_service = AuthService(db)
            user = await auth_service.signin(user_data)
            return {
                "data": user,
                "message": "User signed in successfully.",
                "status": True,
            }
        except ValueError as ve:
            # Handle login errors (like invalid credentials)
            error_message = str(ve)

            if "invalid credentials" in error_message.lower():
                status_code = status.HTTP_401_UNAUTHORIZED
            elif "user not found" in error_message.lower():
                status_code = status.HTTP_404_NOT_FOUND
            elif (
                "email or username is required" in error_message.lower()
                or "password is required" in error_message.lower()
            ):
                status_code = status.HTTP_400_BAD_REQUEST
            elif (
                "validation failed" in error_message.lower()
                or "invalid" in error_message.lower()
            ):
                status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
            else:
                # Generic validation/business logic error
                status_code = status.HTTP_400_BAD_REQUEST

            return JSONResponse(
                status_code=status_code,
                content={"message": error_message, "status": False},
            )
        except Exception as e:
            # Handle unexpected errors
            self.logger.error(f"Unexpected error during sign-in: {e}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "message": "An unexpected error occurred during sign-in.",
                    "status": False,
                },
            )
