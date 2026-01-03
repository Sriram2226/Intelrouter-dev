"""
Model metadata management for versioning and tracking.
"""
from datetime import datetime
from typing import Dict, Optional
from supabase import create_client
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger("intelrouter.ml.metadata")

METADATA_TABLE = "model_metadata"


def get_metadata_client():
    """Get Supabase client for metadata operations."""
    return create_client(settings.supabase_url, settings.supabase_service_key)


def save_model_metadata(
    version: str,
    metrics: Dict,
    confidence_threshold: float,
    training_timestamp: datetime,
    is_active: bool = False
) -> bool:
    """Save model metadata to database."""
    try:
        client = get_metadata_client()
        
        # Deactivate all previous models if this is active
        if is_active:
            client.table(METADATA_TABLE).update({"is_active": False}).execute()
        
        metadata = {
            "version": version,
            "accuracy": metrics.get("accuracy", 0.0),
            "f1_score": metrics.get("f1_score", 0.0),
            "confidence_threshold": confidence_threshold,
            "training_timestamp": training_timestamp.isoformat(),
            "is_active": is_active,
            "created_at": datetime.utcnow().isoformat(),
            "metrics": metrics  # Store full metrics as JSON
        }
        
        client.table(METADATA_TABLE).insert(metadata).execute()
        logger.info(f"✅ Model metadata saved for version {version}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to save metadata: {str(e)}", exc_info=True)
        return False


def get_model_metadata(version: str) -> Optional[Dict]:
    """Get metadata for a specific model version."""
    try:
        client = get_metadata_client()
        response = client.table(METADATA_TABLE)\
            .select("*")\
            .eq("version", version)\
            .execute()
        
        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        logger.error(f"❌ Failed to get metadata: {str(e)}")
        return None


def get_active_model_metadata() -> Optional[Dict]:
    """Get metadata for the currently active model."""
    try:
        client = get_metadata_client()
        response = client.table(METADATA_TABLE)\
            .select("*")\
            .eq("is_active", True)\
            .order("created_at", desc=True)\
            .limit(1)\
            .execute()
        
        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        logger.error(f"❌ Failed to get active model metadata: {str(e)}")
        return None

