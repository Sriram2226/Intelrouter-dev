"""
ML Classifier for query difficulty prediction.
Loads model from Supabase Storage at startup.
"""
import os
from typing import Optional, Tuple
import numpy as np
from app.ml.model_storage import download_model, get_active_model_version
from app.ml.model_metadata import get_active_model_metadata
from app.ml.features import extract_text_features, extract_tfidf_features, combine_features
from app.utils.logger import get_logger

logger = get_logger("intelrouter.ml.classifier")


class DifficultyClassifier:
    """ML classifier for query difficulty (EASY/MEDIUM/HARD)."""
    
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.confidence_threshold = 0.6
        self.version = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Load active model from Supabase Storage."""
        try:
            # Get active model version
            version = get_active_model_version()
            
            if not version:
                logger.warning("⚠️  No active model found, using fallback")
                return
            
            # Download model and vectorizer
            result = download_model(version)
            if not result:
                logger.warning("⚠️  Failed to download model, using fallback")
                return
            
            self.model, self.vectorizer = result
            self.version = version
            
            # Get metadata for confidence threshold
            metadata = get_active_model_metadata()
            if metadata:
                self.confidence_threshold = metadata.get("confidence_threshold", 0.6)
            
            logger.info(
                f"✅ Model loaded: {version} "
                f"(confidence_threshold={self.confidence_threshold})"
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize model: {str(e)}", exc_info=True)
    
    def predict(self, query: str) -> Tuple[str, float]:
        """
        Predict difficulty and confidence.
        Returns: (difficulty, confidence)
        If confidence < threshold, returns ("UNCERTAIN", confidence)
        """
        if self.model is None or self.vectorizer is None:
            return "MEDIUM", 0.5
        
        try:
            # Extract features
            text_features = extract_text_features(query)
            tfidf_matrix, _ = extract_tfidf_features([query], self.vectorizer)
            feature_vector = combine_features(text_features, tfidf_matrix[0])
            
            # Predict
            probs = self.model.predict_proba([feature_vector])[0]
            classes = self.model.classes_
            
            # Get highest probability
            max_idx = np.argmax(probs)
            predicted_class = str(classes[max_idx])
            confidence = float(probs[max_idx])
            
            # Check confidence threshold
            if confidence < self.confidence_threshold:
                return "UNCERTAIN", confidence
            
            return predicted_class, confidence
            
        except Exception as e:
            logger.error(f"❌ Prediction error: {str(e)}", exc_info=True)
            return "MEDIUM", 0.5


# Global classifier instance
classifier = DifficultyClassifier()
