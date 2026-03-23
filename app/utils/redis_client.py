import redis
import hashlib
import json
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger("intelrouter.utils.redis")

# Initialize Redis client with connection error handling
try:
    redis_client = redis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        db=settings.redis_db,
        password=settings.redis_password if settings.redis_password else None,
        decode_responses=True,
        socket_connect_timeout=2,
        socket_timeout=2
    )
    # Test connection
    redis_client.ping()
    REDIS_AVAILABLE = True
    logger.info(f"✅ Redis connected | Host: {settings.redis_host}:{settings.redis_port} | DB: {settings.redis_db}")
except (redis.ConnectionError, redis.TimeoutError, Exception) as e:
    logger.warning(f"⚠️  Redis not available: {type(e).__name__}: {str(e)} | Running without Redis caching")
    redis_client = None
    REDIS_AVAILABLE = False


def get_daily_token_usage(user_id: str) -> int:
    """Get user's daily token usage from Redis."""
    if not REDIS_AVAILABLE:
        logger.debug(f"   📊 Redis unavailable, returning 0 for token usage")
        return 0
    try:
        key = f"tokens:{user_id}"
        usage = redis_client.get(key)
        result = int(usage) if usage else 0
        logger.debug(f"   📊 Token usage retrieved | User: {user_id[:8]}... | Usage: {result:,}")
        return result
    except Exception as e:
        logger.error(f"   ❌ Error getting token usage: {type(e).__name__}: {str(e)}", exc_info=True)
        return 0


def increment_daily_tokens(user_id: str, tokens: int) -> int:
    """Increment daily token usage. Returns new total."""
    if not REDIS_AVAILABLE:
        logger.debug(f"   📊 Redis unavailable, skipping token increment")
        return tokens
    try:
        key = f"tokens:{user_id}"
        total = redis_client.incrby(key, tokens)
        redis_client.expire(key, 86400)  # 24h TTL
        logger.debug(f"   📈 Token usage incremented | User: {user_id[:8]}... | Added: {tokens:,} | Total: {total:,}")
        return total
    except Exception as e:
        logger.error(f"   ❌ Error incrementing tokens: {type(e).__name__}: {str(e)}", exc_info=True)
        return tokens


def get_override_count(user_id: str) -> int:
    """Get remaining override count for user."""
    if not REDIS_AVAILABLE:
        logger.debug(f"   🔒 Redis unavailable, returning 0 for override count")
        return 0
    try:
        key = f"overrides:{user_id}"
        count = redis_client.get(key)
        result = int(count) if count else 0
        logger.debug(f"   🔒 Override count retrieved | User: {user_id[:8]}... | Count: {result}")
        return result
    except Exception as e:
        logger.error(f"   ❌ Error getting override count: {type(e).__name__}: {str(e)}", exc_info=True)
        return 0


def increment_override(user_id: str) -> int:
    """Increment override count. Returns new count."""
    if not REDIS_AVAILABLE:
        logger.debug(f"   🔒 Redis unavailable, skipping override increment")
        return 1
    try:
        key = f"overrides:{user_id}"
        count = redis_client.incr(key)
        redis_client.expire(key, 86400)  # 24h TTL
        logger.info(f"   🔒 Override count incremented | User: {user_id[:8]}... | New count: {count}")
        return count
    except Exception as e:
        logger.error(f"   ❌ Error incrementing override: {type(e).__name__}: {str(e)}", exc_info=True)
        return 1


def reset_daily_limits(user_id: str):
    """Reset daily limits (for testing/admin)."""
    if not REDIS_AVAILABLE:
        logger.debug(f"   🔄 Redis unavailable, skipping limit reset")
        return
    try:
        redis_client.delete(f"tokens:{user_id}")
        redis_client.delete(f"overrides:{user_id}")
        logger.info(f"   🔄 Daily limits reset | User: {user_id[:8]}...")
    except Exception as e:
        logger.error(f"   ❌ Error resetting limits: {type(e).__name__}: {str(e)}", exc_info=True)


# ----- Response Caching -----

CACHE_TTL_SECONDS = 3600  # 1 hour


def _make_cache_key(query: str) -> str:
    """Create a SHA-256 hash key from the query text."""
    return "cache:" + hashlib.sha256(query.strip().lower().encode()).hexdigest()


def get_cached_response(query: str):
    """Return cached (response, model, difficulty) tuple or None."""
    if not REDIS_AVAILABLE:
        return None
    try:
        key = _make_cache_key(query)
        raw = redis_client.get(key)
        if raw:
            data = json.loads(raw)
            logger.info(f"   🎯 Cache HIT | Key: {key[:20]}...")
            return data
        logger.debug(f"   💨 Cache MISS | Key: {key[:20]}...")
        return None
    except Exception as e:
        logger.warning(f"   ⚠️  Cache get error: {type(e).__name__}: {str(e)}")
        return None


def set_cached_response(query: str, response: str, model_name: str, difficulty: str, routing_source: str):
    """Cache a response for the given query."""
    if not REDIS_AVAILABLE:
        return
    try:
        key = _make_cache_key(query)
        data = json.dumps({
            "answer": response,
            "model_name": model_name,
            "difficulty": difficulty,
            "routing_source": routing_source,
        })
        redis_client.setex(key, CACHE_TTL_SECONDS, data)
        logger.info(f"   💾 Cache SET | Key: {key[:20]}... | TTL: {CACHE_TTL_SECONDS}s")
    except Exception as e:
        logger.warning(f"   ⚠️  Cache set error: {type(e).__name__}: {str(e)}")

