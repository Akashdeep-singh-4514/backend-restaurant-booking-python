import datetime
from datetime import timezone
import jwt
from src.config._logger import logger
from src.config._jwt_config import jwt_config

def generate_jwt_token(user_id: int, username: str, email: str) -> str:
    """Generate a JWT token for a user."""
    try:
        payload = {
            "id": user_id,
            "username": username,
            "email": email,
            "exp": datetime.datetime.now(timezone.utc) + datetime.timedelta(minutes=jwt_config["JWT_EXPIRATION_MINUTES"]),
        }
        return jwt.encode(payload, jwt_config["SECRET_KEY"], algorithm=jwt_config["JWT_ALGORITHM"])
    except Exception as e:
        logger.error(f"Error generating JWT token: {e}")
        raise