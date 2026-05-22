from fastapi import HTTPException, Header
from jose import JWTError, jwt
from datetime import datetime, timedelta
from backend.config import settings

def verify_jwt(token: str) -> dict:
    """Verify JWT token and return user data"""
    
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        # Check expiration
        exp = payload.get('exp')
        if exp and datetime.fromtimestamp(exp) < datetime.utcnow():
            raise HTTPException(status_code=401, detail="Token expired")
        
        return {
            'id': payload.get('user_id'),
            'email': payload.get('email'),
            'role': payload.get('role', 'student')
        }
        
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def require_jwt(authorization: str = Header(...)):
    """FastAPI dependency for JWT authentication"""
    
    if not authorization.startswith('Bearer '):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = authorization.replace('Bearer ', '')
    return verify_jwt(token)
