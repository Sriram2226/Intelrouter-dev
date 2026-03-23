"""
A/B Testing Router.

Assigns users to group A (90%) or B (10%) based on a hash of their user_id.
Group A: Standard hybrid router (ML + algorithmic).
Group B: Algorithmic-only router (experimental variant).

The ab_group is persisted in the `queries` table for later analysis via
GET /api/admin/ab-stats.
"""
import hashlib
from typing import Optional
from app.router.hybrid_router import route_query
from app.router.algorithmic_scorer import score_difficulty
from app.config import MODEL_MAP
from app.utils.logger import get_logger

logger = get_logger("intelrouter.router.ab")

# Traffic split: 0.9 = 90% Group A, 10% Group B
AB_SPLIT = 0.9


def _get_ab_group(user_id: str) -> str:
    """
    Deterministically assign a user to group A or B using their user_id hash.
    Same user always gets the same group within a day.
    """
    digest = hashlib.md5(user_id.encode()).hexdigest()
    # Use first 8 hex chars → integer → map to [0, 1)
    bucket = int(digest[:8], 16) / 0xFFFFFFFF
    group = "A" if bucket < AB_SPLIT else "B"
    logger.debug(f"   🧪 A/B group: {group} (bucket={bucket:.4f}) | User: {user_id[:8]}...")
    return group


def ab_route(
    user_id: str,
    query: str,
    user_override: Optional[str] = None,
    has_image: bool = False,
    has_document: bool = False,
    remaining_budget: Optional[float] = None,
) -> tuple[str, str, str, str]:
    """
    Route a query using the A/B testing framework.

    Returns:
        (difficulty, model_name, routing_source, ab_group)
    """
    ab_group = _get_ab_group(user_id)

    if ab_group == "A":
        # Standard hybrid router
        difficulty, model_name, routing_source = route_query(
            query, user_override, has_image, has_document, remaining_budget
        )
        logger.info(f"   🅰️  Group A routing: {difficulty} via {routing_source}")
    else:
        # Experimental: algorithmic-only router
        if user_override and user_override.upper() in ["EASY", "MEDIUM", "HARD"]:
            difficulty = user_override.upper()
            routing_source = "user_override"
        else:
            algo_label = score_difficulty(query)
            difficulty = algo_label if algo_label != "UNSURE" else "MEDIUM"
            routing_source = "algorithmic_only_experiment"

        model_name = MODEL_MAP.get(difficulty, MODEL_MAP["MEDIUM"])
        logger.info(f"   🅱️  Group B routing: {difficulty} via {routing_source}")

    return difficulty, model_name, routing_source, ab_group
