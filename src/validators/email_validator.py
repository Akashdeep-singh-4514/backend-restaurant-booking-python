import re

from email_validator import EmailNotValidError, validate_email


class EmailValidator:
    """Email validation utilities."""

    # Regex pattern for email validation (allows any domain)
    EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Check if email format is valid - all domains allowed."""
        if not isinstance(email, str) or not email.strip():
            return False

        email = email.strip()

        # First try with email-validator library (disable deliverability check)
        try:
            validate_email(email, check_deliverability=False)
            return True
        except EmailNotValidError:
            # Fallback to regex pattern for more permissive validation
            return bool(EmailValidator.EMAIL_PATTERN.match(email))

    @staticmethod
    def normalize_email(email: str) -> str:
        """Normalize email address."""
        try:
            valid = validate_email(email, check_deliverability=False)
            return valid.email
        except EmailNotValidError:
            # If email-validator fails, just return lowercase trimmed version
            if EmailValidator.is_valid_email(email):
                return email.strip().lower()
            raise ValueError("Invalid email format")

    @staticmethod
    def sanitize_email(email: str) -> str:
        """Sanitize and normalize email."""
        if not isinstance(email, str):
            raise ValueError("Email must be a string")

        # Basic sanitization
        email = email.strip().lower()

        # Validate format
        if not EmailValidator.is_valid_email(email):
            raise ValueError("Invalid email format")

        return EmailValidator.normalize_email(email)
