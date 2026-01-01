from app.config import settings


def calculate_cost(difficulty: str, total_tokens: int) -> float:
    """Calculate cost based on difficulty and token count."""
    tokens_per_1k = total_tokens / 1000.0
    
    if difficulty == "EASY":
        return tokens_per_1k * settings.cost_per_1k_easy
    elif difficulty == "MEDIUM":
        return tokens_per_1k * settings.cost_per_1k_medium
    elif difficulty == "HARD":
        return tokens_per_1k * settings.cost_per_1k_hard
    
    # Default to medium
    return tokens_per_1k * settings.cost_per_1k_medium

