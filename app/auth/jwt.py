from typing import Optional
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client
from app.config import settings


security = HTTPBearer()
supabase_auth = create_client(settings.supabase_url, settings.supabase_key)


async def verify_jwt(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    """Verify JWT token and extract user info."""
    token = credentials.credentials
    
    try:
        # Verify token with Supabase
        user = supabase_auth.auth.get_user(token)
        
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        return {
            "user_id": user.user.id,
            "email": user.user.email,
            "role": user.user.user_metadata.get("role", "user")
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token verification failed: {str(e)}")


async def verify_admin(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    """Verify JWT and check admin role."""
    user_info = await verify_jwt(credentials)
    
    if user_info["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return user_info


def verify_admin_secret(admin_secret: str) -> bool:
    """Verify admin secret key."""
    return admin_secret == settings.admin_secret_key

