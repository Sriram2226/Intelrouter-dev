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

