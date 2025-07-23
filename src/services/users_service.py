from typing import List

from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.config import logger
from src.config._database_config import DatabaseConfig
from src.models import User
from src.schemas.user_schema import UserCreate, UserResponse, UserUpdate
from src.validators import (
    CommonValidator,
    EmailValidator,
    PasswordValidator,
    SecurityValidator,
)


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.logger = logger
        # Password encryption context
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt."""
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash."""
        return self.pwd_context.verify(plain_password, hashed_password)

    """Service for user-related operations."""

    async def get_users(self) -> List[UserResponse]:
        async with self.db as session:
            result = await session.execute(select(User))
            users = result.scalars().all()
            # Convert to UserResponse objects for proper serialization
            return [UserResponse.model_validate(user) for user in users]

    async def get_user_by_id(self, user_id: int) -> UserResponse:
        """Fetch a user by ID."""
        async with self.db as session:
            result = await session.execute(select(User).where(User.id == user_id))
            user = result.scalars().first()
            if not user:
                raise ValueError("User not found.")
            return UserResponse.model_validate(user)

    async def create_user(self, user_data: UserCreate) -> UserResponse:
        async with self.db as session:
            # Convert Pydantic model to dict
            user_dict = user_data.model_dump(exclude_unset=True)

            # Validate email
            if not user_dict.get("email"):
                raise ValueError("Email is required.")

            # Validate email format
            if not EmailValidator.is_valid_email(user_dict["email"]):
                raise ValueError("Invalid email format.")

            # Validate username if provided
            if user_dict.get("username"):
                # Sanitize username
                user_dict["username"] = CommonValidator.trim_whitespace(
                    user_dict["username"]
                )

                # Validate username format and security
                if not SecurityValidator.is_safe_username(user_dict["username"]):
                    username_errors = SecurityValidator.get_username_validation_errors(
                        user_dict["username"]
                    )
                    raise ValueError(
                        f"Username validation failed: {', '.join(username_errors)}"
                    )

                # Check for existing username
                existing_user_result = await session.execute(
                    select(User).where(User.username == user_dict["username"])
                )
                existing_user = existing_user_result.scalars().first()
                if existing_user:
                    raise ValueError("Username already taken.")

            # Check for existing email
            existing_email_result = await session.execute(
                select(User).where(User.email == user_dict["email"])
            )
            existing_email_user = existing_email_result.scalars().first()
            if existing_email_user:
                raise ValueError("Email already registered.")

            # Validate password strength
            if not PasswordValidator.is_strong_password(user_dict["password"]):
                password_errors = PasswordValidator.get_password_strength_errors(
                    user_dict["password"]
                )
                raise ValueError(
                    f"Password validation failed: {', '.join(password_errors)}"
                )

            # Hash password before storing
            hashed_password = self.hash_password(user_dict["password"])

            # Create new user with hashed password
            new_user = User(
                username=user_dict.get("username"),
                email=user_dict["email"],
                hashed_password=hashed_password,
                is_active=user_dict.get("is_active", True),
            )
            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)

            # Convert to UserResponse for proper serialization
            return UserResponse.model_validate(new_user)

    async def update_user(self, user_id: int, user_data: UserUpdate) -> UserResponse:
        """Update user details."""
        async with self.db as session:
            result = await session.execute(select(User).where(User.id == user_id))
            user = result.scalars().first()
            if not user:
                raise ValueError("User not found.")

            user_dict = user_data.model_dump(exclude_unset=True)
            if "username" in user_dict:
                # Sanitize username
                user_dict["username"] = CommonValidator.trim_whitespace(
                    user_dict["username"]
                )
                user.username = user_dict["username"]
            if "email" in user_dict:
                # Validate email format
                if not EmailValidator.is_valid_email(user_dict["email"]):
                    raise ValueError("Invalid email format.")
                user.email = user_dict["email"]
            if "is_active" in user_dict:
                user.is_active = user_dict["is_active"]

            session.add(user)
            await session.commit()
            await session.refresh(user)

            return UserResponse.model_validate(user)

    async def delete_user(self, user_id: int) -> None:
        """Delete a user by ID."""
        async with self.db as session:
            result = await session.execute(select(User).where(User.id == user_id))
            user = result.scalars().first()
            if not user:
                raise ValueError("User not found.")

            await session.delete(user)
            await session.commit()
