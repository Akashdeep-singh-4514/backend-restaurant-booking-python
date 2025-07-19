import html
import re
from typing import Dict, List


class SecurityValidator:
    """Security validation utilities for preventing injections."""

    # Common SQL injection patterns
    SQL_INJECTION_PATTERNS = [
        r"(\b(ALTER|CREATE|DELETE|DROP|EXEC(UTE)?|INSERT|SELECT|UNION|UPDATE)\b)",
        r"(\b(AND|OR)\b.*(=|<|>))",
        r"(--|#|/\*|\*/)",
        r"(\b(SCRIPT|JAVASCRIPT|VBSCRIPT|ONLOAD|ONERROR|ONCLICK)\b)",
        r"(CHAR\(|ASCII\(|SUBSTRING\()",
        r"(\b(XP_|SP_)\w+)",
    ]

    # HTML/XSS patterns
    HTML_INJECTION_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"<iframe[^>]*>.*?</iframe>",
        r"<object[^>]*>.*?</object>",
        r"<embed[^>]*>.*?</embed>",
        r"<form[^>]*>.*?</form>",
        r"javascript:",
        r"vbscript:",
        r"onload=",
        r"onerror=",
        r"onclick=",
        r"onmouseover=",
    ]

    @staticmethod
    def sanitize_string(value: str) -> str:
        """Sanitize string by escaping HTML characters."""
        if not isinstance(value, str):
            return value
        return html.escape(value.strip())

    @staticmethod
    def detect_sql_injection(value: str) -> bool:
        """Detect potential SQL injection attempts."""
        if not isinstance(value, str):
            return False

        value_lower = value.lower()
        for pattern in SecurityValidator.SQL_INJECTION_PATTERNS:
            if re.search(pattern, value_lower, re.IGNORECASE):
                return True
        return False

    @staticmethod
    def detect_html_injection(value: str) -> bool:
        """Detect potential HTML/XSS injection attempts."""
        if not isinstance(value, str):
            return False

        value_lower = value.lower()
        for pattern in SecurityValidator.HTML_INJECTION_PATTERNS:
            if re.search(pattern, value_lower, re.IGNORECASE):
                return True
        return False

    @staticmethod
    def validate_username(username: str) -> Dict[str, bool]:
        """Validate username for security and format - only letters, numbers, dots, and underscores."""
        if not isinstance(username, str):
            return {"valid_input": False}

        return {
            "min_length": len(username) >= 3,
            "max_length": len(username) <= 30,
            "valid_chars": bool(
                re.match(r"^[a-zA-Z0-9._]+$", username)
            ),  # Only letters, numbers, dots, underscores
            "no_whitespace": not bool(re.search(r"\s", username)),
            "not_empty": bool(username.strip()),
            "not_only_dots": not re.match(
                r"^\.+$", username
            ),  # Prevent usernames that are only dots
            "not_only_underscores": not re.match(
                r"^_+$", username
            ),  # Prevent usernames that are only underscores
            "no_sql_injection": not SecurityValidator.detect_sql_injection(username),
            "no_html_injection": not SecurityValidator.detect_html_injection(username),
        }

    @staticmethod
    def is_safe_username(username: str) -> bool:
        """Check if username meets all security requirements."""
        if not isinstance(username, str):
            return False
        validation_result = SecurityValidator.validate_username(username)
        return all(validation_result.values())

    @staticmethod
    def get_username_validation_errors(username: str) -> List[str]:
        """Get list of username validation errors."""
        if not isinstance(username, str):
            return ["Username must be a string"]

        validation_result = SecurityValidator.validate_username(username)
        errors = []

        if not validation_result["min_length"]:
            errors.append("Username must be at least 3 characters long")
        if not validation_result["max_length"]:
            errors.append("Username must be no more than 30 characters long")
        if not validation_result["valid_chars"]:
            errors.append(
                "Username can only contain letters, numbers, dots, and underscores"
            )
        if not validation_result["no_whitespace"]:
            errors.append("Username cannot contain spaces")
        if not validation_result["not_empty"]:
            errors.append("Username cannot be empty")
        if not validation_result["not_only_dots"]:
            errors.append("Username cannot consist only of dots")
        if not validation_result["not_only_underscores"]:
            errors.append("Username cannot consist only of underscores")
        if not validation_result["no_sql_injection"]:
            errors.append("Username contains potentially dangerous content")
        if not validation_result["no_html_injection"]:
            errors.append("Username contains potentially dangerous content")

        return errors

    @staticmethod
    def is_safe_string(value: str) -> bool:
        """Check if string is safe from common injection attacks."""
        if not isinstance(value, str):
            return False
        return (
            not SecurityValidator.detect_sql_injection(value)
            and not SecurityValidator.detect_html_injection(value)
            and bool(value.strip())
        )
