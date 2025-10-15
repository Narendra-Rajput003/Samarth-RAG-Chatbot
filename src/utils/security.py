# src/utils/security.py
"""Security: JWT auth and input sanitization (OWASP-compliant)."""
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from pydantic import BaseModel
import re
from src.config.settings import settings

security = HTTPBearer()
ALPHANUMERIC_REGEX = re.compile(r'^[a-zA-Z0-9\s\.,?!\-_]+$' )

class User(BaseModel):
    username: str

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    try:
        payload = jwt.decode(credentials.credentials, settings.jwt_secret, algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return User(username=username)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def sanitize_input(text: str) -> str:
    if not ALPHANUMERIC_REGEX.match(text):
        raise ValueError("Input contains invalid characters")
    return text[:500]