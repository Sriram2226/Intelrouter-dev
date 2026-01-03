from typing import Optional
from app.router.algorithmic_scorer import score_difficulty
from app.ml.classifier import classifier
from app.config import MODEL_MAP


def route_query(query: str, user_override: Optional[str] = None) -> tuple[str, str, str]:
    """
    Hybrid router: Algorithmic → ML → Final routing.
    
    Returns: (difficulty, model_name, routing_source)
    """
    # User override takes precedence
    if user_override and user_override.upper() in ["EASY", "MEDIUM", "HARD"]:
        difficulty = user_override.upper()
        model_name = MODEL_MAP.get(difficulty, MODEL_MAP["MEDIUM"])
        return difficulty, model_name, "user_override"
    
    # Step 1: Algorithmic scorer
    algorithmic_label = score_difficulty(query)
    
    # Step 2: ML classifier (only for UNSURE)
    if algorithmic_label == "UNSURE":
        ml_label, confidence = classifier.predict(query)
        # Handle UNCERTAIN predictions (low confidence)
        if ml_label == "UNCERTAIN":
            difficulty = "MEDIUM"  # Default to MEDIUM for uncertain predictions
            routing_source = "ml_uncertain"
        else:
            difficulty = ml_label
            routing_source = "ml"
    else:
        difficulty = algorithmic_label
        routing_source = "algorithmic"
    
    # Step 3: Final routing
    model_name = MODEL_MAP.get(difficulty, MODEL_MAP["MEDIUM"])
    
    return difficulty, model_name, routing_source

