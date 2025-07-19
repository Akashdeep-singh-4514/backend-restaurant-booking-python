from typing import Any, List


class CommonValidator:
    """Common validation utilities."""

    @staticmethod
    def is_not_empty(value: Any) -> bool:
        """Check if value is not empty."""
        if value is None:
            return False
        if isinstance(value, str):
            return bool(value.strip())
        if isinstance(value, (list, dict, tuple)):
            return len(value) > 0
        return True

    @staticmethod
    def validate_required_fields(data: dict, required_fields: List[str]) -> List[str]:
        """Validate that required fields are present and not empty."""
        missing_fields = []
        for field in required_fields:
            if field not in data or not CommonValidator.is_not_empty(data[field]):
                missing_fields.append(field)
        return missing_fields

    @staticmethod
    def trim_whitespace(value: str) -> str:
        """Trim whitespace from string."""
        return value.strip() if isinstance(value, str) else value

    @staticmethod
    def validate_length(
        value: str, min_length: int = 0, max_length: int = None
    ) -> bool:
        """Validate string length."""
        if not isinstance(value, str):
            return False
        length = len(value)
        if length < min_length:
            return False
        if max_length and length > max_length:
            return False
        return True

    @staticmethod
    def prevent_empty_string(value: str, field_name: str = "Field") -> str:
        """Prevent empty strings and return trimmed value."""
        if not isinstance(value, str):
            raise ValueError(f"{field_name} must be a string")

        trimmed = value.strip()
        if not trimmed:
            raise ValueError(f"{field_name} cannot be empty or contain only whitespace")

        return trimmed
