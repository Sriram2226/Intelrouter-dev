"""
ML Model Training Script
Trains Logistic Regression on ml_data table.
Runs offline, evaluates on full dataset + last 30 days.
Only promotes if no regression on recent data.
"""
import sys
import os
from datetime import datetime, timedelta
from typing import List, Tuple, Dict
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, classification_report
from sklearn.model_selection import train_test_split
import joblib

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings
from app.ml.features import extract_text_features, extract_tfidf_features, combine_features
from app.ml.model_storage import upload_model, get_active_model_version, download_model
from app.ml.model_metadata import save_model_metadata, get_active_model_metadata
from app.db.supabase_client import supabase
from app.utils.logger import get_logger

logger = get_logger("intelrouter.training")

# Training configuration
CONFIDENCE_THRESHOLD = 0.6
MIN_TRAINING_SAMPLES = 50
TEST_SIZE = 0.2
RANDOM_STATE = 42


def load_training_data() -> Tuple[List[str], List[str]]:
    """
    Load all training data from ml_data table.
    Returns: (queries, labels)
    """
    logger.info("📊 Loading training data from ml_data table...")
    
    try:
        response = supabase.table("ml_data")\
            .select("query, difficulty")\
            .order("created_at", desc=False)\
            .execute()
        
        if not response.data:
            raise ValueError("No training data found in ml_data table")
        
        queries = [row["query"] for row in response.data]
        labels = [row["difficulty"].upper() for row in response.data]
        
        # Validate labels
        valid_labels = {"EASY", "MEDIUM", "HARD"}
        filtered_data = [(q, l) for q, l in zip(queries, labels) if l in valid_labels]
        
        if len(filtered_data) < MIN_TRAINING_SAMPLES:
            raise ValueError(
                f"Insufficient training data: {len(filtered_data)} samples "
                f"(minimum: {MIN_TRAINING_SAMPLES})"
            )
        
        queries, labels = zip(*filtered_data)
        logger.info(f"✅ Loaded {len(queries)} training samples")
        
        return list(queries), list(labels)
        
    except Exception as e:
        logger.error(f"❌ Failed to load training data: {str(e)}", exc_info=True)
        raise


def prepare_features(queries: List[str], vectorizer=None):
    """
    Prepare feature vectors for training/inference.
    Returns: (feature_matrix, vectorizer)
    """
    logger.info("🔧 Extracting features...")
    
    # Extract text features
    text_features_list = [extract_text_features(q) for q in queries]
    
    # Extract TF-IDF features
    tfidf_matrix, vectorizer = extract_tfidf_features(queries, vectorizer)
    
    # Combine features
    combined_features = []
    for i, text_feat in enumerate(text_features_list):
        tfidf_vec = tfidf_matrix[i]
        combined = combine_features(text_feat, tfidf_vec)
        combined_features.append(combined)
    
    feature_matrix = np.array(combined_features)
    logger.info(f"✅ Feature matrix shape: {feature_matrix.shape}")
    
    return feature_matrix, vectorizer


def train_model(X_train, y_train) -> LogisticRegression:
    """Train Logistic Regression model."""
    logger.info("🎓 Training Logistic Regression model...")
    
    model = LogisticRegression(
        max_iter=1000,
        random_state=RANDOM_STATE,
        solver='lbfgs',
        C=1.0
    )
    
    model.fit(X_train, y_train)
    logger.info("✅ Model training completed")
    
    return model


def evaluate_model(model, X, y, dataset_name: str) -> Dict:
    """Evaluate model and return metrics."""
    logger.info(f"📈 Evaluating on {dataset_name}...")
    
    y_pred = model.predict(X)
    accuracy = accuracy_score(y, y_pred)
    f1 = f1_score(y, y_pred, average='weighted')
    
    logger.info(f"   Accuracy: {accuracy:.4f}")
    logger.info(f"   F1 Score: {f1:.4f}")
    
    return {
        "accuracy": float(accuracy),
        "f1_score": float(f1),
        "dataset": dataset_name,
        "samples": len(y)
    }


def split_recent_data(queries: List[str], labels: List[str], days: int = 30):
    """
    Split data into full dataset and recent (last N days) dataset.
    Returns: (all_queries, all_labels, recent_queries, recent_labels)
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Load with timestamps
    response = supabase.table("ml_data")\
        .select("query, difficulty, created_at")\
        .order("created_at", desc=False)\
        .execute()
    
    all_queries = []
    all_labels = []
    recent_queries = []
    recent_labels = []
    
    for row in response.data:
        query = row["query"]
        label = row["difficulty"].upper()
        created_at_str = row["created_at"]
        
        # Parse timestamp
        try:
            if created_at_str.endswith('Z'):
                created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
            else:
                created_at = datetime.fromisoformat(created_at_str)
        except:
            # Fallback: assume recent if parsing fails
            created_at = datetime.utcnow()
        
        all_queries.append(query)
        all_labels.append(label)
        
        if created_at >= cutoff_date:
            recent_queries.append(query)
            recent_labels.append(label)
    
    return all_queries, all_labels, recent_queries, recent_labels


def compare_with_active_model(new_metrics: Dict, recent_metrics: Dict) -> bool:
    """
    Compare new model with active model.
    Returns True if new model should be promoted.
    """
    active_metadata = get_active_model_metadata()
    
    if not active_metadata:
        logger.info("ℹ️  No active model found, promoting new model")
        return True
    
    active_f1 = active_metadata.get("f1_score", 0.0)
    active_accuracy = active_metadata.get("accuracy", 0.0)
    
    new_f1 = recent_metrics["f1_score"]
    new_accuracy = recent_metrics["accuracy"]
    
    # Check for regression on recent data
    f1_regression = new_f1 < active_f1 * 0.95  # 5% tolerance
    accuracy_regression = new_accuracy < active_accuracy * 0.95
    
    if f1_regression or accuracy_regression:
        logger.warning(
            f"⚠️  Model regression detected:\n"
            f"   Active F1: {active_f1:.4f} → New F1: {new_f1:.4f}\n"
            f"   Active Accuracy: {active_accuracy:.4f} → New Accuracy: {new_accuracy:.4f}"
        )
        return False
    
    logger.info(
        f"✅ Model improvement:\n"
        f"   F1: {active_f1:.4f} → {new_f1:.4f}\n"
        f"   Accuracy: {active_accuracy:.4f} → {new_accuracy:.4f}"
    )
    return True


def main():
    """Main training pipeline."""
    logger.info("=" * 60)
    logger.info("🚀 Starting ML Model Training Pipeline")
    logger.info("=" * 60)
    
    try:
        # 1. Load training data
        all_queries, all_labels = load_training_data()
        
        # 2. Split into full and recent datasets
        all_q, all_l, recent_q, recent_l = split_recent_data(all_queries, all_labels, days=30)
        
        if len(recent_q) < 10:
            logger.warning("⚠️  Insufficient recent data (< 10 samples), using full dataset for recent evaluation")
            recent_q, recent_l = all_q, all_l
        
        # 3. Prepare features
        X_all, vectorizer = prepare_features(all_q)
        X_recent, _ = prepare_features(recent_q, vectorizer)
        
        # 4. Train-test split for full dataset
        X_train, X_test, y_train, y_test = train_test_split(
            X_all, all_l, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=all_l
        )
        
        # 5. Train model
        model = train_model(X_train, y_train)
        
        # 6. Evaluate on full test set
        full_metrics = evaluate_model(model, X_test, y_test, "full test set")
        
        # 7. Evaluate on recent data
        recent_metrics = evaluate_model(model, X_recent, recent_l, "recent 30 days")
        
        # 8. Compare with active model
        should_promote = compare_with_active_model(full_metrics, recent_metrics)
        
        if not should_promote:
            logger.warning("⚠️  Model not promoted due to regression")
            return
        
        # 9. Generate version
        version = f"v{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        # 10. Upload model to Supabase Storage
        if not upload_model(model, vectorizer, version, full_metrics):
            logger.error("❌ Failed to upload model")
            return
        
        # 11. Save metadata
        combined_metrics = {
            **full_metrics,
            "recent_accuracy": recent_metrics["accuracy"],
            "recent_f1_score": recent_metrics["f1_score"],
            "recent_samples": recent_metrics["samples"]
        }
        
        save_model_metadata(
            version=version,
            metrics=combined_metrics,
            confidence_threshold=CONFIDENCE_THRESHOLD,
            training_timestamp=datetime.utcnow(),
            is_active=True
        )
        
        logger.info("=" * 60)
        logger.info(f"✅ Training completed successfully!")
        logger.info(f"   Model version: {version}")
        logger.info(f"   Full Accuracy: {full_metrics['accuracy']:.4f}")
        logger.info(f"   Recent Accuracy: {recent_metrics['accuracy']:.4f}")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ Training failed: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

