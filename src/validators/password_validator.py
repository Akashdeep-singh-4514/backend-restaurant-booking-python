import re
from typing import Dict, List


class PasswordValidator:
    """Password validation utilities."""

    MIN_LENGTH = 6  # Updated to 6 as per requirement
    MAX_LENGTH = 128

    @staticmethod
    def validate_password(password: str) -> Dict[str, bool]:
        """Comprehensive password validation."""
        return {
            "min_length": len(password) >= PasswordValidator.MIN_LENGTH,
            "max_length": len(password) <= PasswordValidator.MAX_LENGTH,
            "has_letter": bool(re.search(r"[a-zA-Z]", password)),
            "has_digit": bool(re.search(r"\d", password)),
            "has_special": bool(
                re.search(r'[!@#$%^&*(),.?":{}|<>_+\-=\[\]\\;\'\/~`]', password)
            ),
            "no_whitespace": not bool(re.search(r"\s", password)),
        }

    @staticmethod
    def is_strong_password(password: str) -> bool:
        """Check if password meets strength requirements."""
        if not isinstance(password, str):
            return False

        checks = PasswordValidator.validate_password(password)
        # All requirements must be met: 6+ chars, letters, numbers, special chars, no spaces
        required_checks = [
            "min_length",
            "has_letter",
            "has_digit",
            "has_special",
            "no_whitespace",
        ]
        return all(checks[check] for check in required_checks)

    @staticmethod
    def get_password_strength_errors(password: str) -> List[str]:
        """Get list of password validation errors."""
        if not isinstance(password, str):
            return ["Password must be a string"]

        checks = PasswordValidator.validate_password(password)
        errors = []

        if not checks["min_length"]:
            errors.append(
                f"Password must be at least {PasswordValidator.MIN_LENGTH} characters long"
            )
        if not checks["max_length"]:
            errors.append(
                f"Password must be no more than {PasswordValidator.MAX_LENGTH} characters long"
            )
        if not checks["has_letter"]:
            errors.append("Password must contain at least one letter")
        if not checks["has_digit"]:
            errors.append("Password must contain at least one number")
        if not checks["has_special"]:
            errors.append("Password must contain at least one special character")
        if not checks["no_whitespace"]:
            errors.append("Password cannot contain whitespace")

        return errors

    @staticmethod
    def validate_and_get_errors(password: str) -> List[str]:
        """Validate password and return errors if any."""
        if PasswordValidator.is_strong_password(password):
            return []
        return PasswordValidator.get_password_strength_errors(password)
