from fastapi import APIRouter, Depends
from app.api.schemas import UserInfo, UsageToday, OverrideStatus
from app.auth.jwt import verify_jwt
from app.db.operations import get_user, get_user_usage_today, get_user_queries
from app.utils.redis_client import get_daily_token_usage, get_override_count
from app.config import settings


router = APIRouter(prefix="/api", tags=["dashboard"])


@router.get("/me", response_model=UserInfo)
async def get_me(user_info: dict = Depends(verify_jwt)):
    """Get current user info."""
    user = get_user(user_info["user_id"])
    if not user:
        raise Exception("User not found")
    
    return UserInfo(
        id=user.id,
        email=user.email,
        role=user.role
    )


@router.get("/usage/today", response_model=UsageToday)
async def get_usage_today(user_info: dict = Depends(verify_jwt)):
    """Get today's usage statistics."""
    user_id = user_info["user_id"]
    
    usage = get_user_usage_today(user_id)
    current_usage = get_daily_token_usage(user_id)
    remaining = max(0, settings.daily_token_limit - current_usage)
    
    return UsageToday(
        total_tokens=usage["total_tokens"],
        total_cost=usage["total_cost"],
        request_count=usage["request_count"],
        remaining_tokens=remaining
    )


@router.get("/queries/history")
async def get_query_history(user_info: dict = Depends(verify_jwt)):
    """Get user's query history."""
    user_id = user_info["user_id"]
    queries = get_user_queries(user_id)
    
    return [
        {
            "id": q.id,
            "final_label": q.final_label,
            "routing_source": q.routing_source,
            "model_name": q.model_name,
            "created_at": q.created_at.isoformat() if q.created_at else None
        }
        for q in queries
    ]


@router.get("/overrides/remaining", response_model=OverrideStatus)
async def get_override_status(user_info: dict = Depends(verify_jwt)):
    """Get remaining override count."""
    user_id = user_info["user_id"]
    used = get_override_count(user_id)
    remaining = max(0, 3 - used)
    
    return OverrideStatus(
        remaining=remaining,
        used=used,
        limit=3
    )

