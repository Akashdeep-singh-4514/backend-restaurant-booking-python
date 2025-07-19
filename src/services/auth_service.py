from typing import List

from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.config import DatabaseConfig, logger
from src.models import User
from src.schemas.user_schema import UserCreate, UserLogin, UserResponse, UserUpdate
from src.validators import (
    CommonValidator,
    EmailValidator,
    PasswordValidator,
    SecurityValidator,
)


class AuthService:
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

    async def signup(self, user_data: UserCreate) -> UserResponse:
        self.logger.info("AuthService: Creating a new user.")
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

    async def signin(self, user_data: UserLogin) -> UserResponse:
        """Authenticate user by username/email and password."""
        print("AuthService: Authenticating user.", user_data)
        user_dict = user_data.model_dump(exclude_unset=True)
        email = user_dict.get("email")
        password = user_dict.get("password")
        username = user_dict.get("username")
        print(email, password, username)

        if not email and not username:
            raise ValueError("Email or username is required for login.")
        if not password:
            raise ValueError("Password is required for login.")

        async with self.db as session:
            if email:
                result = await session.execute(select(User).where(User.email == email))
            else:
                result = await session.execute(
                    select(User).where(User.username == username)
                )

            user = result.scalars().first()
            if not user:
                raise ValueError("User not found.")

            if not self.verify_password(password, user.hashed_password):
                raise ValueError("Invalid credentials.")

            return UserResponse.model_validate(user)
