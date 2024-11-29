
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from app.core.config import settings
import time

security = HTTPBearer()

def verify_jwt(token: str) -> dict:
    try:
        decoded_token = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        if decoded_token["exp"] < time.time():
            raise HTTPException(status_code=401, detail="Token has expired")
        return decoded_token
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def auth_middleware(request: Request, call_next):
    try:
        token = await security(request)
        verify_jwt(token.credentials)
        response = await call_next(request)
        return response
    except HTTPException as e:
        raise e