"""
Utilities for storing and loading models from Supabase Storage.
"""
import os
import joblib
import tempfile
from typing import Optional, Tuple
from supabase import create_client, Client
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger("intelrouter.ml.storage")

# Supabase Storage bucket name
MODEL_BUCKET = "ml-models"
MODEL_METADATA_TABLE = "model_metadata"


def get_storage_client() -> Client:
    """Get Supabase client with service key for storage access."""
    return create_client(settings.supabase_url, settings.supabase_service_key)


def upload_model(model, vectorizer, version: str, metadata: dict) -> bool:
    """
    Upload model and vectorizer to Supabase Storage.
    Returns True if successful.
    """
    try:
        storage = get_storage_client()
        
        # Create temporary files
        with tempfile.NamedTemporaryFile(delete=False, suffix='.joblib') as model_file, \
             tempfile.NamedTemporaryFile(delete=False, suffix='.joblib') as vec_file:
            
            # Save model and vectorizer
            joblib.dump(model, model_file.name)
            joblib.dump(vectorizer, vec_file.name)
            
            # Upload to storage
            model_path = f"{version}/model.joblib"
            vectorizer_path = f"{version}/vectorizer.joblib"
            
            with open(model_file.name, 'rb') as f:
                file_data = f.read()
                storage.storage.from_(MODEL_BUCKET).upload(
                    model_path,
                    file_data,
                    file_options={"content-type": "application/octet-stream", "upsert": "true"}
                )
            
            with open(vec_file.name, 'rb') as f:
                file_data = f.read()
                storage.storage.from_(MODEL_BUCKET).upload(
                    vectorizer_path,
                    file_data,
                    file_options={"content-type": "application/octet-stream", "upsert": "true"}
                )
            
            # Cleanup
            os.unlink(model_file.name)
            os.unlink(vec_file.name)
            
            logger.info(f"✅ Model {version} uploaded to Supabase Storage")
            return True
            
    except Exception as e:
        logger.error(f"❌ Failed to upload model: {str(e)}", exc_info=True)
        return False


def download_model(version: str) -> Optional[Tuple]:
    """
    Download model and vectorizer from Supabase Storage.
    Returns (model, vectorizer) or None if failed.
    """
    try:
        storage = get_storage_client()
        
        model_path = f"{version}/model.joblib"
        vectorizer_path = f"{version}/vectorizer.joblib"
        
        # Download files
        model_data = storage.storage.from_(MODEL_BUCKET).download(model_path)
        vectorizer_data = storage.storage.from_(MODEL_BUCKET).download(vectorizer_path)
        
        # Load from bytes
        import io
        model = joblib.load(io.BytesIO(model_data))
        vectorizer = joblib.load(io.BytesIO(vectorizer_data))
        
        logger.info(f"✅ Model {version} downloaded from Supabase Storage")
        return model, vectorizer
        
    except Exception as e:
        logger.error(f"❌ Failed to download model {version}: {str(e)}", exc_info=True)
        return None


def get_active_model_version() -> Optional[str]:
    """Get the currently active model version from metadata table."""
    try:
        storage = get_storage_client()
        response = storage.table(MODEL_METADATA_TABLE)\
            .select("version")\
            .eq("is_active", True)\
            .order("created_at", desc=True)\
            .limit(1)\
            .execute()
        
        if response.data:
            return response.data[0]["version"]
        return None
    except Exception as e:
        logger.error(f"❌ Failed to get active model version: {str(e)}")
        return None

