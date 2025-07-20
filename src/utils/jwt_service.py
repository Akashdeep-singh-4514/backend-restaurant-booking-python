import datetime
from datetime import timezone
from fastapi import HTTPException, status
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
    
async def verify_jwt_token(token: str) -> dict:
    """Verify a JWT token."""
    try:
        payload = jwt.decode(token, jwt_config["SECRET_KEY"], algorithms=[jwt_config["JWT_ALGORITHM"]])
        return payload
    except jwt.DecodeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Token could not be decoded",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Error verifying JWT token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Token verification failed",
            headers={"WWW-Authenticate": "Bearer"},
        )
