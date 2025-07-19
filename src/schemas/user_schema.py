# src/schemas/user_schema.py
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from src.validators import (
    CommonValidator,
    EmailValidator,
    PasswordValidator,
    SecurityValidator,
)


class UserBase(BaseModel):
    """Base schema for User - contains common fields."""

    username: Optional[str] = Field(
        None, min_length=3, max_length=30, example="john_doe"
    )
    email: EmailStr = Field(..., example="john.doe@example.com")
    is_active: bool = Field(default=True, description="Indicates if the user is active")


class UserCreate(UserBase):
    """Schema for creating a new user (includes password)."""

    password: str = Field(..., min_length=6, max_length=128, example="SecureP@ss123")

    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        if v is None:
            return v

        # Trim whitespace
        v = CommonValidator.trim_whitespace(v)

        # Security validation - only letters, numbers, dots, and underscores
        if not SecurityValidator.is_safe_username(v):
            errors = SecurityValidator.get_username_validation_errors(v)
            raise ValueError(f"Username validation failed: {', '.join(errors)}")

        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        # Check password strength - 6+ chars, letters, numbers, special chars
        if not PasswordValidator.is_strong_password(v):
            errors = PasswordValidator.get_password_strength_errors(v)
            raise ValueError(f"Password requirements not met: {', '.join(errors)}")

        return v


class UserLogin(BaseModel):
    """Schema for user login credentials."""

    email: Optional[EmailStr] = Field(None, example="john.doe@example.com")
    username: Optional[str] = Field(
        None, min_length=3, max_length=30, example="john_doe"
    )
    password: str = Field(..., min_length=6, max_length=128, example="SecureP@ss123")

    def model_post_init(self, __context):
        """Validate that at least one of email or username is provided."""
        if not self.email and not self.username:
            raise ValueError("Either email or username must be provided for login")
        return self


class UserUpdate(BaseModel):
    """Schema for updating an existing user (all fields optional for partial update)."""

    username: Optional[str] = Field(
        None, min_length=3, max_length=30, example="john_doe_new"
    )
    email: Optional[EmailStr] = Field(None, example="john.doe.new@example.com")
    is_active: Optional[bool] = Field(
        None, description="Indicates if the user is active"
    )

    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        if v is None:
            return v

        v = CommonValidator.trim_whitespace(v)

        if not SecurityValidator.is_safe_username(v):
            errors = SecurityValidator.get_username_validation_errors(v)
            raise ValueError(f"Username validation failed: {', '.join(errors)}")

        return v

    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        if v is None:
            return v

        if not EmailValidator.is_valid_email(v):
            raise ValueError("Invalid email format")

        return v

    @field_validator("is_active")
    @classmethod
    def validate_is_active(cls, v):
        if v is None:
            return v

        return v == True


class UserInDBBase(UserBase):
    """Schema for user data as stored in DB (includes ID and timestamps)."""

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Enables ORM model to Pydantic mapping


class UserResponse(UserInDBBase):
    """Schema for user data sent as response (excludes hashed password)."""

    pass


__all__ = [
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserInDBBase",
    "UserResponse",
    "UserLogin",
]
