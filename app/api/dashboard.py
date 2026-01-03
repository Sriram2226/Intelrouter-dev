import time
from fastapi import APIRouter, Depends, HTTPException
from app.api.schemas import UserInfo, UsageToday, OverrideStatus, FeedbackRequest, FeedbackResponse
from app.auth.jwt import verify_jwt
from app.db.operations import get_user, get_user_usage_today, get_user_queries, save_ml_data
from app.utils.redis_client import get_daily_token_usage, get_override_count
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger("intelrouter.api.dashboard")
router = APIRouter(prefix="/api", tags=["dashboard"])


@router.get("/me", response_model=UserInfo)
async def get_me(user_info: dict = Depends(verify_jwt)):
    """Get current user info."""
    start_time = time.time()
    user_id = user_info["user_id"]
    
    logger.info(f"👤 GET_USER_INFO | User: {user_id[:8]}...")
    
    try:
        user = get_user(user_id)
        if not user:
            logger.warning(f"   ⚠️  User not found: {user_id[:8]}...")
            raise HTTPException(status_code=404, detail="User not found")
        
        duration = time.time() - start_time
        logger.info(f"   ✅ User info retrieved | Email: {user.email} | Role: {user.role} | Duration: {duration:.3f}s")
        
        return UserInfo(
            id=user.id,
            email=user.email,
            role=user.role
        )
    except HTTPException:
        raise
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"   ❌ Error getting user info: {type(e).__name__}: {str(e)} | Duration: {duration:.3f}s", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error retrieving user info: {str(e)}")


@router.get("/usage/today", response_model=UsageToday)
async def get_usage_today(user_info: dict = Depends(verify_jwt)):
    """Get today's usage statistics."""
    start_time = time.time()
    user_id = user_info["user_id"]
    
    logger.info(f"📊 GET_USAGE_TODAY | User: {user_id[:8]}...")
    
    try:
        logger.debug(f"   📈 Fetching usage from database...")
        usage = get_user_usage_today(user_id)
        logger.debug(f"   💰 Fetching current usage from Redis...")
        current_usage = get_daily_token_usage(user_id)
        remaining = max(0, settings.daily_token_limit - current_usage)
        
        duration = time.time() - start_time
        logger.info(
            f"   ✅ Usage retrieved | Tokens: {usage['total_tokens']:,} | "
            f"Cost: ${usage['total_cost']:.4f} | Requests: {usage['request_count']} | "
            f"Remaining: {remaining:,} | Duration: {duration:.3f}s"
        )
        
        return UsageToday(
            total_tokens=usage["total_tokens"],
            total_cost=usage["total_cost"],
            request_count=usage["request_count"],
            remaining_tokens=remaining
        )
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"   ❌ Error getting usage: {type(e).__name__}: {str(e)} | Duration: {duration:.3f}s", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error retrieving usage: {str(e)}")


@router.get("/queries/history")
async def get_query_history(user_info: dict = Depends(verify_jwt)):
    """Get user's query history."""
    start_time = time.time()
    user_id = user_info["user_id"]
    
    logger.info(f"📜 GET_QUERY_HISTORY | User: {user_id[:8]}...")
    
    try:
        logger.debug(f"   🔍 Fetching query history from database...")
        queries = get_user_queries(user_id)
        
        duration = time.time() - start_time
        logger.info(f"   ✅ Retrieved {len(queries)} queries | Duration: {duration:.3f}s")
        
        return [
            {
                "id": q.id,
                "query_text": q.query_text,
                "final_label": q.final_label,
                "routing_source": q.routing_source,
                "model_name": q.model_name,
                "created_at": q.created_at.isoformat() if q.created_at else None
            }
            for q in queries
        ]
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"   ❌ Error getting query history: {type(e).__name__}: {str(e)} | Duration: {duration:.3f}s", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error retrieving query history: {str(e)}")


@router.get("/overrides/remaining", response_model=OverrideStatus)
async def get_override_status(user_info: dict = Depends(verify_jwt)):
    """Get remaining override count."""
    start_time = time.time()
    user_id = user_info["user_id"]
    
    logger.info(f"🔒 GET_OVERRIDE_STATUS | User: {user_id[:8]}...")
    
    try:
        logger.debug(f"   📊 Fetching override count from Redis...")
        used = get_override_count(user_id)
        remaining = max(0, 3 - used)
        
        duration = time.time() - start_time
        logger.info(f"   ✅ Override status | Used: {used}/3 | Remaining: {remaining} | Duration: {duration:.3f}s")
        
        return OverrideStatus(
            remaining=remaining,
            used=used,
            limit=3
        )
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"   ❌ Error getting override status: {type(e).__name__}: {str(e)} | Duration: {duration:.3f}s", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error retrieving override status: {str(e)}")


@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(
    feedback: FeedbackRequest,
    user_info: dict = Depends(verify_jwt)
):
    """Submit routing feedback for ML training."""
    start_time = time.time()
    user_id = user_info["user_id"]
    
    logger.info(f"📝 SUBMIT_FEEDBACK | User: {user_id[:8]}... | Correct: {feedback.is_correct}")
    
    try:
        if feedback.is_correct:
            # User says routing is correct - use the current difficulty
            difficulty = feedback.difficulty.upper()
            logger.info(f"   ✅ Routing confirmed correct | Difficulty: {difficulty}")
        else:
            # User says routing is wrong - use the corrected difficulty
            if not feedback.correct_difficulty:
                raise HTTPException(
                    status_code=400,
                    detail="correct_difficulty is required when is_correct is false"
                )
            difficulty = feedback.correct_difficulty.upper()
            logger.info(
                f"   ⚠️  Routing corrected | Original: {feedback.difficulty} | "
                f"Correct: {difficulty}"
            )
        
        # Validate difficulty
        if difficulty not in ["EASY", "MEDIUM", "HARD"]:
            raise HTTPException(
                status_code=400,
                detail="Difficulty must be EASY, MEDIUM, or HARD"
            )
        
        # Save to ML data table
        save_ml_data(feedback.query, difficulty)
        
        duration = time.time() - start_time
        logger.info(f"   ✅ Feedback saved | Duration: {duration:.3f}s")
        
        return FeedbackResponse(
            success=True,
            message="Feedback saved successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        duration = time.time() - start_time
        logger.error(
            f"   ❌ Error submitting feedback: {type(e).__name__}: {str(e)} | "
            f"Duration: {duration:.3f}s",
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail=f"Error submitting feedback: {str(e)}"
        )

