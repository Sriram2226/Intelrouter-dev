import pickle
import os
from typing import Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import numpy as np


class DifficultyClassifier:
    """ML classifier for query difficulty (EASY/MEDIUM/HARD)."""
    
    def __init__(self):
        self.model: Optional[Pipeline] = None
        self.model_path = "app/ml/classifier_model.pkl"
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize or load classifier model."""
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, 'rb') as f:
                    self.model = pickle.load(f)
            except Exception:
                self.model = self._create_new_model()
        else:
            self.model = self._create_new_model()
    
    def _create_new_model(self) -> Pipeline:
        """Create a new classifier model."""
        # TF-IDF with 1-3 grams, max 5000 features
        vectorizer = TfidfVectorizer(
            ngram_range=(1, 3),
            max_features=5000,
            lowercase=True,
            stop_words='english'
        )
        
        # Logistic Regression for multiclass classification
        classifier = LogisticRegression(
            max_iter=1000,
            random_state=42
        )
        
        return Pipeline([('tfidf', vectorizer), ('clf', classifier)])
    
    def predict(self, query: str) -> tuple[str, float]:
        """
        Predict difficulty and confidence.
        Returns: (difficulty, confidence)
        """
        if self.model is None:
            return "MEDIUM", 0.5
        
        try:
            # Check if model has been trained (has classes_ attribute)
            if not hasattr(self.model.named_steps['clf'], 'classes_'):
                return "MEDIUM", 0.5
            
            # Get prediction probabilities
            probs = self.model.predict_proba([query])[0]
            classes = self.model.named_steps['clf'].classes_
            
            # Get highest probability
            max_idx = np.argmax(probs)
            predicted_class = classes[max_idx]
            confidence = float(probs[max_idx])
            
            # If confidence < 0.6, default to MEDIUM
            if confidence < 0.6:
                return "MEDIUM", confidence
            
            return str(predicted_class), confidence
        except Exception:
            return "MEDIUM", 0.5
    
    def train(self, queries: list[str], labels: list[str]):
        """Train the classifier with new data."""
        if len(queries) < 10:
            return  # Need minimum data
        
        self.model.fit(queries, labels)
        
        # Save model
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        with open(self.model_path, 'wb') as f:
            pickle.dump(self.model, f)


# Global classifier instance
classifier = DifficultyClassifier()

