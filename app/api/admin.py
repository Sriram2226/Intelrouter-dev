from fastapi import APIRouter, HTTPException, Depends, Header
from app.auth.jwt import verify_admin, verify_admin_secret
from app.db.operations import get_admin_metrics, get_admin_costs, get_routing_stats


router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/metrics")
async def get_metrics(
    user_info: dict = Depends(verify_admin),
    x_admin_secret: str = Header(None)
):
    """Get admin metrics."""
    if not x_admin_secret or not verify_admin_secret(x_admin_secret):
        raise HTTPException(status_code=403, detail="Admin secret required")
    
    return get_admin_metrics()


@router.get("/costs")
async def get_costs(
    user_info: dict = Depends(verify_admin),
    x_admin_secret: str = Header(None)
):
    """Get cost breakdown by difficulty."""
    if not x_admin_secret or not verify_admin_secret(x_admin_secret):
        raise HTTPException(status_code=403, detail="Admin secret required")
    
    return get_admin_costs()


@router.get("/routing-stats")
async def get_routing_stats_endpoint(
    user_info: dict = Depends(verify_admin),
    x_admin_secret: str = Header(None)
):
    """Get routing statistics."""
    if not x_admin_secret or not verify_admin_secret(x_admin_secret):
        raise HTTPException(status_code=403, detail="Admin secret required")
    
    return get_routing_stats()

