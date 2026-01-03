import time
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
    get_user,
    save_ml_data
)
from app.db.models import Query, UsageLog
from app.utils.logger import get_logger

logger = get_logger("intelrouter.api.query")
router = APIRouter(prefix="/api/query", tags=["query"])


@router.post("", response_model=QueryResponse)
async def process_query(
    request: QueryRequest,
    user_info: dict = Depends(verify_jwt)
):
    """Process user query and route to appropriate LLM."""
    start_time = time.time()
    user_id = user_info["user_id"]
    email = user_info["email"]
    query_length = len(request.query)
    
    logger.info(f"🔍 QUERY RECEIVED | User: {user_id[:8]}... | Query length: {query_length} chars")
    if request.difficulty_override:
        logger.info(f"   ⚙️  Override requested: {request.difficulty_override}")
    
    try:
        # Ensure user exists in database
        logger.debug(f"   👤 Checking user existence...")
        user = get_user(user_id)
        if not user:
            logger.info(f"   ➕ Creating new user: {email}")
            create_user(user_id, email, user_info["role"])
        else:
            logger.debug(f"   ✅ User exists: {email}")
        
        # Check override limit if override requested
        if request.difficulty_override:
            logger.debug(f"   🔒 Checking override limit...")
            override_count = get_override_count(user_id)
            logger.info(f"   📊 Override count: {override_count}/3")
            if override_count >= 3:
                logger.warning(f"   ⛔ Override limit exceeded for user {user_id[:8]}...")
                raise HTTPException(
                    status_code=429,
                    detail="Daily override limit (3) exceeded"
                )
        
        # Route query
        logger.debug(f"   🧭 Routing query...")
        route_start = time.time()
        difficulty, model_name, routing_source = route_query(
            request.query,
            request.difficulty_override
        )
        route_duration = time.time() - route_start
        logger.info(
            f"   ✅ Routed to: {model_name} | Difficulty: {difficulty} | "
            f"Source: {routing_source} | Routing time: {route_duration:.3f}s"
        )
        
        # Increment override count if used
        if routing_source == "user_override":
            logger.info(f"   🔄 Incrementing override count...")
            increment_override(user_id)
            # Save override to ML training data (user explicitly selected difficulty)
            logger.info(f"   📚 Saving override to ML training data...")
            try:
                save_ml_data(request.query, difficulty)
                logger.info(f"   ✅ Override saved to ML data")
            except Exception as e:
                logger.warning(f"   ⚠️  Failed to save override to ML data: {str(e)}")
                # Don't fail the request if ML data save fails
        
        # Check daily token limit
        logger.debug(f"   💰 Checking daily token usage...")
        current_usage = get_daily_token_usage(user_id)
        logger.info(f"   📈 Current daily usage: {current_usage:,}/{settings.daily_token_limit:,} tokens")
        if current_usage >= settings.daily_token_limit:
            logger.warning(f"   ⛔ Daily token limit exceeded for user {user_id[:8]}...")
            raise HTTPException(
                status_code=429,
                detail=f"Daily token limit ({settings.daily_token_limit}) exceeded"
            )
        
        # Call LLM
        logger.info(f"   🤖 Calling LLM: {model_name}...")
        llm_start = time.time()
        try:
            response_text = await call_huggingface_api(model_name, request.query)
            llm_duration = time.time() - llm_start
            if not response_text:
                logger.error(f"   ❌ Empty response from LLM API")
                raise HTTPException(status_code=500, detail="Empty response from LLM API")
            logger.info(f"   ✅ LLM response received | Length: {len(response_text)} chars | Duration: {llm_duration:.3f}s")
        except HTTPException:
            raise
        except Exception as e:
            error_msg = str(e) if str(e) else f"{type(e).__name__}: {repr(e)}"
            logger.error(f"   ❌ LLM API error: {error_msg}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"LLM API error: {error_msg}")
        
        # Estimate token usage
        logger.debug(f"   🔢 Estimating token usage...")
        token_usage = estimate_token_usage(request.query, response_text, model_name)
        logger.info(
            f"   📊 Token usage: {token_usage['tokens_in']} in + "
            f"{token_usage['tokens_out']} out = {token_usage['total_tokens']} total"
        )
        
        # Check if this would exceed limit
        new_total = current_usage + token_usage["total_tokens"]
        if new_total > settings.daily_token_limit:
            logger.warning(f"   ⛔ Request would exceed daily limit: {new_total:,} > {settings.daily_token_limit:,}")
            raise HTTPException(
                status_code=429,
                detail="Request would exceed daily token limit"
            )
        
        # Calculate cost
        cost = calculate_cost(difficulty, token_usage["total_tokens"])
        logger.info(f"   💵 Cost calculated: ${cost:.4f} for {difficulty} difficulty")
        
        # Increment token usage
        logger.debug(f"   📈 Updating daily token usage...")
        increment_daily_tokens(user_id, token_usage["total_tokens"])
        logger.info(f"   ✅ Daily usage updated: {new_total:,} tokens")
        
        # Get algorithmic and ML labels for logging
        logger.debug(f"   🏷️  Getting classification labels...")
        from app.router.algorithmic_scorer import score_difficulty
        from app.ml.classifier import classifier
        
        algorithmic_label = score_difficulty(request.query)
        ml_label = None
        if algorithmic_label == "UNSURE":
            logger.debug(f"   🤖 Using ML classifier (algorithmic was UNSURE)...")
            ml_label, _ = classifier.predict(request.query)
        logger.info(f"   🏷️  Labels - Algorithmic: {algorithmic_label}, ML: {ml_label or 'N/A'}")
        
        # Save query (with query_text - will be auto-cleaned after 30 days)
        logger.debug(f"   💾 Saving query to database...")
        query_record = Query(
            user_id=user_id,
            query_text=request.query,
            algorithmic_label=algorithmic_label,
            ml_label=ml_label,
            final_label=difficulty,
            routing_source=routing_source,
            model_name=model_name
        )
        saved_query = save_query(query_record)
        logger.info(f"   ✅ Query saved with ID: {saved_query.id}")
        
        # Save usage log
        logger.debug(f"   💾 Saving usage log to database...")
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
        logger.info(f"   ✅ Usage log saved")
        
        total_duration = time.time() - start_time
        logger.info(
            f"✅ QUERY COMPLETED | User: {user_id[:8]}... | Model: {model_name} | "
            f"Total duration: {total_duration:.3f}s | Cost: ${cost:.4f}"
        )
        
        return QueryResponse(
            answer=response_text,
            model_name=model_name,
            difficulty=difficulty,
            routing_source=routing_source,
            usage=token_usage
        )
        
    except HTTPException as e:
        duration = time.time() - start_time
        logger.warning(
            f"⚠️  QUERY FAILED | User: {user_id[:8]}... | Status: {e.status_code} | "
            f"Detail: {e.detail} | Duration: {duration:.3f}s"
        )
        raise
    except Exception as e:
        duration = time.time() - start_time
        logger.error(
            f"❌ QUERY ERROR | User: {user_id[:8]}... | Error: {type(e).__name__}: {str(e)} | "
            f"Duration: {duration:.3f}s",
            exc_info=True
        )
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

