from typing import Optional
from app.router.algorithmic_scorer import score_difficulty
from app.ml.classifier import classifier
from app.config import MODEL_MAP


def route_query(query: str, user_override: Optional[str] = None) -> tuple[str, str, str]:
    """
    Hybrid router: ML → Algorithmic → Final routing.
    
    Returns: (difficulty, model_name, routing_source)
    """
    # User override takes precedence
    if user_override and user_override.upper() in ["EASY", "MEDIUM", "HARD"]:
        difficulty = user_override.upper()
        model_name = MODEL_MAP.get(difficulty, MODEL_MAP["MEDIUM"])
        return difficulty, model_name, "user_override"
    
    # Step 1: ML classifier (primary)
    ml_label, confidence = classifier.predict(query)
    
    # Step 2: Use algorithmic scorer as fallback if ML is uncertain
    if ml_label == "UNCERTAIN":
        algorithmic_label = score_difficulty(query)
        if algorithmic_label == "UNSURE":
            difficulty = "MEDIUM"  # Default fallback
            routing_source = "algorithmic_fallback"
        else:
            difficulty = algorithmic_label
            routing_source = "algorithmic_fallback"
    else:
        difficulty = ml_label
        routing_source = "ml"
    
    # Step 3: Final routing
    model_name = MODEL_MAP.get(difficulty, MODEL_MAP["MEDIUM"])
    
    return difficulty, model_name, routing_source

