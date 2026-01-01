import redis
from app.config import settings


redis_client = redis.Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    db=settings.redis_db,
    password=settings.redis_password if settings.redis_password else None,
    decode_responses=True
)


def get_daily_token_usage(user_id: str) -> int:
    """Get user's daily token usage from Redis."""
    key = f"tokens:{user_id}"
    usage = redis_client.get(key)
    return int(usage) if usage else 0


def increment_daily_tokens(user_id: str, tokens: int) -> int:
    """Increment daily token usage. Returns new total."""
    key = f"tokens:{user_id}"
    total = redis_client.incrby(key, tokens)
    redis_client.expire(key, 86400)  # 24h TTL
    return total


def get_override_count(user_id: str) -> int:
    """Get remaining override count for user."""
    key = f"overrides:{user_id}"
    count = redis_client.get(key)
    return int(count) if count else 0


def increment_override(user_id: str) -> int:
    """Increment override count. Returns new count."""
    key = f"overrides:{user_id}"
    count = redis_client.incr(key)
    redis_client.expire(key, 86400)  # 24h TTL
    return count


def reset_daily_limits(user_id: str):
    """Reset daily limits (for testing/admin)."""
    redis_client.delete(f"tokens:{user_id}")
    redis_client.delete(f"overrides:{user_id}")

