from typing import Optional
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger("intelrouter.auth.jwt")
security = HTTPBearer()
supabase_auth = create_client(settings.supabase_url, settings.supabase_key)


async def verify_jwt(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    """Verify JWT token and extract user info."""
    token = credentials.credentials
    token_preview = f"{token[:10]}...{token[-10:]}" if len(token) > 20 else "***"
    
    logger.debug(f"🔐 Verifying JWT token: {token_preview}")
    
    try:
        # Verify token with Supabase
        user = supabase_auth.auth.get_user(token)
        
        if not user:
            logger.warning(f"   ❌ Invalid token: User not found")
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user_id = user.user.id
        email = user.user.email
        role = user.user.user_metadata.get("role", "user")
        
        logger.info(f"   ✅ Token verified | User: {user_id[:8]}... | Email: {email} | Role: {role}")
        
        return {
            "user_id": user_id,
            "email": email,
            "role": role
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"   ❌ Token verification failed: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=401, detail=f"Token verification failed: {str(e)}")


async def verify_admin(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    """Verify JWT and check admin role."""
    logger.debug(f"👑 Verifying admin access...")
    user_info = await verify_jwt(credentials)
    
    if user_info["role"] != "admin":
        logger.warning(f"   ⛔ Admin access denied | User: {user_info['user_id'][:8]}... | Role: {user_info['role']}")
        raise HTTPException(status_code=403, detail="Admin access required")
    
    logger.info(f"   ✅ Admin access granted | User: {user_info['user_id'][:8]}...")
    return user_info


def verify_admin_secret(admin_secret: str) -> bool:
    """Verify admin secret key."""
    return admin_secret == settings.admin_secret_key

