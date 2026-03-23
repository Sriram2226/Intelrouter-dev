"""
Streaming query endpoint: POST /api/query/stream
Returns Server-Sent Events (SSE) as tokens arrive from the LLM.
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from app.api.schemas import QueryRequest
from app.auth.jwt import verify_jwt
from app.router.hybrid_router import route_query
from app.utils.redis_client import get_daily_token_usage, get_override_count, increment_override
from app.config import settings
from app.db.operations import get_user, create_user, save_ml_data
from app.llm.streaming_client import stream_huggingface_api
from app.utils.logger import get_logger

logger = get_logger("intelrouter.api.stream")
router = APIRouter(prefix="/api/query", tags=["query-stream"])


@router.post("/stream")
async def stream_query(
    request: QueryRequest,
    user_info: dict = Depends(verify_jwt),
):
    """Stream LLM response tokens in real-time via Server-Sent Events."""
    user_id = user_info["user_id"]
    email = user_info["email"]

    logger.info(f"🌊 STREAM QUERY | User: {user_id[:8]}... | Query length: {len(request.query)}")

    # Ensure user exists
    user = get_user(user_id)
    if not user:
        create_user(user_id, email, user_info["role"])

    # Check override limit
    if request.difficulty_override:
        override_count = get_override_count(user_id)
        if override_count >= 3:
            raise HTTPException(status_code=429, detail="Daily override limit (3) exceeded")

    # Check daily token limit
    current_usage = get_daily_token_usage(user_id)
    if current_usage >= settings.daily_token_limit:
        raise HTTPException(
            status_code=429,
            detail=f"Daily token limit ({settings.daily_token_limit}) exceeded"
        )

    # Route the query
    difficulty, model_name, routing_source = route_query(
        request.query, request.difficulty_override
    )
    logger.info(f"   🧭 Streaming via: {model_name} | Difficulty: {difficulty}")

    if routing_source == "user_override":
        increment_override(user_id)
        try:
            save_ml_data(request.query, difficulty)
        except Exception:
            pass

    async def event_generator():
        # Send routing info as first SSE event
        yield f"data: [ROUTING]{difficulty}:{model_name}\n\n"
        async for chunk in stream_huggingface_api(model_name, request.query):
            yield chunk
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        }
    )
