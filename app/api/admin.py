import time
from fastapi import APIRouter, HTTPException, Depends, Header
from app.auth.jwt import verify_admin, verify_admin_secret
from app.db.operations import get_admin_metrics, get_admin_costs, get_routing_stats
from app.utils.logger import get_logger

logger = get_logger("intelrouter.api.admin")
router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/metrics")
async def get_metrics(
    user_info: dict = Depends(verify_admin),
    x_admin_secret: str = Header(None)
):
    """Get admin metrics."""
    start_time = time.time()
    user_id = user_info["user_id"]
    
    logger.info(f"📊 ADMIN_METRICS | User: {user_id[:8]}...")
    
    if not x_admin_secret or not verify_admin_secret(x_admin_secret):
        logger.warning(f"   ⛔ Admin secret verification failed")
        raise HTTPException(status_code=403, detail="Admin secret required")
    
    try:
        metrics = get_admin_metrics()
        duration = time.time() - start_time
        logger.info(
            f"   ✅ Metrics retrieved | Users: {metrics.get('total_users', 0)} | "
            f"Queries: {metrics.get('total_queries', 0)} | Duration: {duration:.3f}s"
        )
        return metrics
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"   ❌ Error getting metrics: {type(e).__name__}: {str(e)} | Duration: {duration:.3f}s", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error retrieving metrics: {str(e)}")


@router.get("/costs")
async def get_costs(
    user_info: dict = Depends(verify_admin),
    x_admin_secret: str = Header(None)
):
    """Get cost breakdown by difficulty."""
    start_time = time.time()
    user_id = user_info["user_id"]
    
    logger.info(f"💰 ADMIN_COSTS | User: {user_id[:8]}...")
    
    if not x_admin_secret or not verify_admin_secret(x_admin_secret):
        logger.warning(f"   ⛔ Admin secret verification failed")
        raise HTTPException(status_code=403, detail="Admin secret required")
    
    try:
        costs = get_admin_costs()
        duration = time.time() - start_time
        logger.info(f"   ✅ Cost breakdown retrieved | Duration: {duration:.3f}s")
        return costs
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"   ❌ Error getting costs: {type(e).__name__}: {str(e)} | Duration: {duration:.3f}s", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error retrieving costs: {str(e)}")


@router.get("/routing-stats")
async def get_routing_stats_endpoint(
    user_info: dict = Depends(verify_admin),
    x_admin_secret: str = Header(None)
):
    """Get routing statistics."""
    start_time = time.time()
    user_id = user_info["user_id"]
    
    logger.info(f"📈 ADMIN_ROUTING_STATS | User: {user_id[:8]}...")
    
    if not x_admin_secret or not verify_admin_secret(x_admin_secret):
        logger.warning(f"   ⛔ Admin secret verification failed")
        raise HTTPException(status_code=403, detail="Admin secret required")
    
    try:
        stats = get_routing_stats()
        duration = time.time() - start_time
        logger.info(f"   ✅ Routing stats retrieved | Duration: {duration:.3f}s")
        return stats
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"   ❌ Error getting routing stats: {type(e).__name__}: {str(e)} | Duration: {duration:.3f}s", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error retrieving routing stats: {str(e)}")


@router.get("/usage-over-time")
async def get_usage_over_time_endpoint(
    days: int = 30,
    user_info: dict = Depends(verify_admin),
    x_admin_secret: str = Header(None)
):
    """Get usage statistics over time."""
    start_time = time.time()
    user_id = user_info["user_id"]
    
    logger.info(f"📊 ADMIN_USAGE_OVER_TIME | User: {user_id[:8]}... | Days: {days}")
    
    if not x_admin_secret or not verify_admin_secret(x_admin_secret):
        logger.warning(f"   ⛔ Admin secret verification failed")
        raise HTTPException(status_code=403, detail="Admin secret required")
    
    try:
        from app.db.operations import get_usage_over_time
        usage_data = get_usage_over_time(days)
        duration = time.time() - start_time
        logger.info(f"   ✅ Usage over time retrieved | Records: {len(usage_data)} | Duration: {duration:.3f}s")
        return {"data": usage_data, "days": days}
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"   ❌ Error getting usage over time: {type(e).__name__}: {str(e)} | Duration: {duration:.3f}s", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error retrieving usage over time: {str(e)}")


@router.get("/ml-pipeline")
async def get_ml_pipeline_info(
    user_info: dict = Depends(verify_admin),
    x_admin_secret: str = Header(None)
):
    """Get ML model pipeline information."""
    start_time = time.time()
    user_id = user_info["user_id"]
    
    logger.info(f"🤖 ADMIN_ML_PIPELINE | User: {user_id[:8]}...")
    
    if not x_admin_secret or not verify_admin_secret(x_admin_secret):
        logger.warning(f"   ⛔ Admin secret verification failed")
        raise HTTPException(status_code=403, detail="Admin secret required")
    
    try:
        from app.ml.model_metadata import get_metadata_client, get_active_model_metadata
        from app.db.supabase_client import supabase
        from datetime import datetime
        from collections import defaultdict
        
        client = get_metadata_client()
        
        # Get all model versions
        models_response = client.table("model_metadata")\
            .select("*")\
            .order("created_at", desc=True)\
            .execute()
        
        models = models_response.data if models_response.data else []
        
        # Get active model
        active_model = get_active_model_metadata()
        
        # Get training data stats
        ml_data_response = supabase.table("ml_data")\
            .select("difficulty, created_at")\
            .execute()
        
        ml_data = ml_data_response.data if ml_data_response.data else []
        
        # Count by difficulty
        difficulty_counts = {"EASY": 0, "MEDIUM": 0, "HARD": 0}
        for item in ml_data:
            diff = item.get("difficulty", "").upper()
            if diff in difficulty_counts:
                difficulty_counts[diff] += 1
        
        # Get routing stats from queries table
        routing_response = supabase.table("queries")\
            .select("routing_source, created_at")\
            .execute()
        
        routing_data = routing_response.data if routing_response.data else []
        
        # Count routing sources
        routing_counts = {}
        for item in routing_data:
            source = item.get("routing_source", "unknown")
            routing_counts[source] = routing_counts.get(source, 0) + 1
        
        # Calculate training data growth over time
        training_growth = defaultdict(int)
        for item in ml_data:
            created_at = item.get("created_at")
            if created_at:
                try:
                    if created_at.endswith('Z'):
                        date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    else:
                        date = datetime.fromisoformat(created_at)
                    date_key = date.strftime('%Y-%m-%d')
                    training_growth[date_key] += 1
                except:
                    pass
        
        # Sort by date
        training_growth_sorted = sorted(training_growth.items())
        
        result = {
            "active_model": active_model,
            "all_models": models,
            "training_data": {
                "total": len(ml_data),
                "by_difficulty": difficulty_counts,
                "growth_over_time": [{"date": k, "count": v} for k, v in training_growth_sorted]
            },
            "routing_stats": {
                "total_queries": len(routing_data),
                "by_source": routing_counts
            }
        }
        
        duration = time.time() - start_time
        logger.info(f"   ✅ ML pipeline info retrieved | Duration: {duration:.3f}s")
        return result
        
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"   ❌ Error getting ML pipeline info: {type(e).__name__}: {str(e)} | Duration: {duration:.3f}s", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error retrieving ML pipeline info: {str(e)}")

