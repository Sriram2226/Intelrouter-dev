import time
from fastapi import APIRouter, HTTPException, Depends
from app.api.schemas import QueryRequest, QueryResponse
from app.auth.jwt import verify_jwt
from app.router.ab_router import ab_route
from app.llm.huggingface_client import call_huggingface_api
from app.llm.token_tracker import estimate_token_usage
from app.metrics.cost_calculator import calculate_cost
from app.utils.redis_client import (
    get_daily_token_usage,
    increment_daily_tokens,
    get_override_count,
    increment_override,
    get_cached_response,
    set_cached_response,
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

        # --- Cache Check ---
        cached = get_cached_response(request.query)
        if cached and not request.difficulty_override:
            logger.info(f"   🎯 Returning cached response")
            return QueryResponse(
                answer=cached["answer"],
                model_name=cached["model_name"],
                difficulty=cached["difficulty"],
                routing_source=cached["routing_source"],
                usage={"tokens_in": 0, "tokens_out": 0, "total_tokens": 0},
                cache_hit=True,
            )

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

        # Compute remaining budget for cost-aware routing
        today_cost = 0.0
        try:
            from app.db.operations import get_user_usage_today
            today_stats = get_user_usage_today(user_id)
            today_cost = today_stats.get("total_cost", 0.0)
        except Exception:
            pass
        remaining_budget = settings.user_daily_budget - today_cost if settings.cost_aware_routing else None

        # Route query (A/B aware + budget + modality)
        logger.debug(f"   🧭 Routing query (A/B)...")
        route_start = time.time()
        difficulty, model_name, routing_source, ab_group = ab_route(
            user_id=user_id,
            query=request.query,
            user_override=request.difficulty_override,
            has_image=request.has_image or False,
            has_document=request.has_document or False,
            remaining_budget=remaining_budget,
        )
        route_duration = time.time() - route_start
        logger.info(
            f"   ✅ Routed to: {model_name} | Difficulty: {difficulty} | "
            f"Source: {routing_source} | A/B: {ab_group} | Routing time: {route_duration:.3f}s"
        )

        # Increment override count and save ML data if user override was used
        if routing_source == "user_override":
            logger.info(f"   🔄 Incrementing override count...")
            increment_override(user_id)
            logger.info(f"   📚 Saving override to ML training data...")
            try:
                save_ml_data(request.query, difficulty)
                logger.info(f"   ✅ Override saved to ML data")
            except Exception as e:
                logger.warning(f"   ⚠️  Failed to save override to ML data: {str(e)}")

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

        # Save query
        logger.debug(f"   💾 Saving query to database...")
        query_record = Query(
            user_id=user_id,
            query_text=request.query,
            algorithmic_label=None,
            ml_label=None,
            final_label=difficulty,
            routing_source=routing_source,
            model_name=model_name,
            ab_group=ab_group,
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

        # --- Cache Store ---
        set_cached_response(request.query, response_text, model_name, difficulty, routing_source)

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
            usage=token_usage,
            cache_hit=False,
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