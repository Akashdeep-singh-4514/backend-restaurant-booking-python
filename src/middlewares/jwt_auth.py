from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.utils.jwt_service import verify_jwt_token

class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(
            auto_error=auto_error,
            scheme_name="BearerAuth",  # Must match the security scheme name
            description="JWT Bearer Token Authentication"
        )

    async def __call__(self, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid authorization code"
            )
        
        token = credentials.credentials
        payload = await verify_jwt_token(token)
        return payload
    
jwt_bearer = JWTBearer()