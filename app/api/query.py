from fastapi import APIRouter, HTTPException, Depends
from app.api.schemas import QueryRequest, QueryResponse
from app.auth.jwt import verify_jwt
from app.router.hybrid_router import route_query
from app.llm.huggingface_client import call_huggingface_api
from app.llm.token_tracker import estimate_token_usage
from app.metrics.cost_calculator import calculate_cost
from app.utils.redis_client import (
    get_daily_token_usage,
    increment_daily_tokens,
    get_override_count,
    increment_override
)
from app.config import settings
from app.db.operations import (
    save_query,
    save_usage_log,
    create_user,
    get_user
)
from app.db.models import Query, UsageLog


router = APIRouter(prefix="/api/query", tags=["query"])


@router.post("", response_model=QueryResponse)
async def process_query(
    request: QueryRequest,
    user_info: dict = Depends(verify_jwt)
):
    """Process user query and route to appropriate LLM."""
    user_id = user_info["user_id"]
    email = user_info["email"]
    
    # Ensure user exists in database
    user = get_user(user_id)
    if not user:
        create_user(user_id, email, user_info["role"])
    
    # Check override limit if override requested
    if request.difficulty_override:
        override_count = get_override_count(user_id)
        if override_count >= 3:
            raise HTTPException(
                status_code=429,
                detail="Daily override limit (3) exceeded"
            )
    
    # Route query
    difficulty, model_name, routing_source = route_query(
        request.query,
        request.difficulty_override
    )
    
    # Increment override count if used
    if routing_source == "user_override":
        increment_override(user_id)
    
    # Check daily token limit
    current_usage = get_daily_token_usage(user_id)
    if current_usage >= settings.daily_token_limit:
        raise HTTPException(
            status_code=429,
            detail=f"Daily token limit ({settings.daily_token_limit}) exceeded"
        )
    
    # Call LLM
    try:
        response_text = await call_huggingface_api(model_name, request.query)
        if not response_text:
            raise HTTPException(status_code=500, detail="Empty response from LLM API")
    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e) if str(e) else f"{type(e).__name__}: {repr(e)}"
        raise HTTPException(status_code=500, detail=f"LLM API error: {error_msg}")
    
    # Estimate token usage
    token_usage = estimate_token_usage(request.query, response_text, model_name)
    
    # Check if this would exceed limit
    new_total = current_usage + token_usage["total_tokens"]
    if new_total > settings.daily_token_limit:
        raise HTTPException(
            status_code=429,
            detail="Request would exceed daily token limit"
        )
    
    # Calculate cost
    cost = calculate_cost(difficulty, token_usage["total_tokens"])
    
    # Increment token usage
    increment_daily_tokens(user_id, token_usage["total_tokens"])
    
    # Get algorithmic and ML labels for logging
    from app.router.algorithmic_scorer import score_difficulty
    from app.ml.classifier import classifier
    
    algorithmic_label = score_difficulty(request.query)
    ml_label = None
    if algorithmic_label == "UNSURE":
        ml_label, _ = classifier.predict(request.query)
    
    # Save query (without query_text for privacy/storage optimization)
    query_record = Query(
        user_id=user_id,
        algorithmic_label=algorithmic_label,
        ml_label=ml_label,
        final_label=difficulty,
        routing_source=routing_source,
        model_name=model_name
    )
    saved_query = save_query(query_record)
    
    # Save usage log
    usage_log = UsageLog(
        user_id=user_id,
        query_id=saved_query.id,
        model_name=model_name,
        difficulty=difficulty,
        tokens_in=token_usage["tokens_in"],
        tokens_out=token_usage["tokens_out"],
        total_tokens=token_usage["total_tokens"],
        cost=cost
    )
    save_usage_log(usage_log)
    
    return QueryResponse(
        answer=response_text,
        model_name=model_name,
        difficulty=difficulty,
        routing_source=routing_source,
        usage=token_usage
    )

