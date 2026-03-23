from typing import Optional
from app.router.algorithmic_scorer import score_difficulty
from app.ml.classifier import classifier
from app.router.modality_detector import detect_modality
from app.config import MODEL_MAP
from app.utils.logger import get_logger

logger = get_logger("intelrouter.router.hybrid")

# Budget threshold: if less than this USD left today, downgrade MEDIUM → EASY
BUDGET_FALLBACK_THRESHOLD = 0.10


def route_query(
    query: str,
    user_override: Optional[str] = None,
    has_image: bool = False,
    has_document: bool = False,
    remaining_budget: Optional[float] = None,
) -> tuple[str, str, str]:
    """
    Hybrid router: Modality → ML → Algorithmic → Budget → Final routing.

    Returns: (difficulty, model_name, routing_source)
    """
    # Step 0: Modality detection — short-circuits difficulty routing
    modality = detect_modality(query, has_image, has_document)
    if modality == "vision":
        model_name = MODEL_MAP.get("VISION", MODEL_MAP["HARD"])
        logger.info(f"   🖼️  Vision routing → {model_name}")
        return "HARD", model_name, "modality_vision"
    if modality == "document":
        model_name = MODEL_MAP.get("DOCUMENT", MODEL_MAP["HARD"])
        logger.info(f"   📄 Document routing → {model_name}")
        return "HARD", model_name, "modality_document"

    # Step 1: User override takes precedence
    if user_override and user_override.upper() in ["EASY", "MEDIUM", "HARD"]:
        difficulty = user_override.upper()
        model_name = MODEL_MAP.get(difficulty, MODEL_MAP["MEDIUM"])
        return difficulty, model_name, "user_override"

    # Step 2: ML classifier (primary)
    ml_label, confidence = classifier.predict(query)

    # Step 3: Use algorithmic scorer as fallback if ML is uncertain
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

    # Step 4: Budget-aware downgrade
    if (
        remaining_budget is not None
        and remaining_budget < BUDGET_FALLBACK_THRESHOLD
        and difficulty == "MEDIUM"
    ):
        logger.info(
            f"   💰 Budget fallback: MEDIUM → EASY "
            f"(remaining: ${remaining_budget:.4f} < ${BUDGET_FALLBACK_THRESHOLD})"
        )
        difficulty = "EASY"
        routing_source = "budget_fallback"

    # Step 5: Final model selection
    model_name = MODEL_MAP.get(difficulty, MODEL_MAP["MEDIUM"])

    return difficulty, model_name, routing_source

