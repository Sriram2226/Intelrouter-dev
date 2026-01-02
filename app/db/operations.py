from datetime import datetime
from typing import List, Optional
from app.db.supabase_client import supabase
from app.db.models import User, Query, UsageLog
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger("intelrouter.db.operations")


def get_user(user_id: str) -> Optional[User]:
    """Get user by ID."""
    logger.debug(f"   🔍 Fetching user from database: {user_id[:8]}...")
    try:
        response = supabase.table("users").select("*").eq("id", user_id).execute()
        if response.data:
            user = User(**response.data[0])
            logger.debug(f"   ✅ User found: {user.email}")
            return user
        logger.debug(f"   ⚠️  User not found: {user_id[:8]}...")
        return None
    except Exception as e:
        logger.error(f"   ❌ Error fetching user: {type(e).__name__}: {str(e)}", exc_info=True)
        raise


def create_user(user_id: str, email: str, role: str = "user") -> User:
    """Create or update user."""
    logger.info(f"   ➕ Creating/updating user: {email} | Role: {role}")
    try:
        user_data = {
            "id": user_id,
            "email": email,
            "role": role,
            "created_at": datetime.utcnow().isoformat()
        }
        response = supabase.table("users").upsert(user_data).execute()
        user = User(**response.data[0])
        logger.info(f"   ✅ User created/updated: {user.id[:8]}...")
        return user
    except Exception as e:
        logger.error(f"   ❌ Error creating user: {type(e).__name__}: {str(e)}", exc_info=True)
        raise


def save_query(query: Query) -> Query:
    """Save query to database."""
    logger.debug(f"   💾 Saving query | Model: {query.model_name} | Difficulty: {query.final_label}")
    try:
        query_data = query.model_dump(exclude={"id", "created_at"})
        query_data["created_at"] = datetime.utcnow().isoformat()
        response = supabase.table("queries").insert(query_data).execute()
        saved_query = Query(**response.data[0])
        logger.debug(f"   ✅ Query saved with ID: {saved_query.id}")
        return saved_query
    except Exception as e:
        logger.error(f"   ❌ Error saving query: {type(e).__name__}: {str(e)}", exc_info=True)
        raise


def save_usage_log(usage_log: UsageLog) -> UsageLog:
    """Save usage log to database."""
    logger.debug(
        f"   💾 Saving usage log | Tokens: {usage_log.total_tokens:,} | "
        f"Cost: ${usage_log.cost:.4f} | Model: {usage_log.model_name}"
    )
    try:
        log_data = usage_log.model_dump(exclude={"id", "created_at"})
        log_data["created_at"] = datetime.utcnow().isoformat()
        response = supabase.table("usage_logs").insert(log_data).execute()
        saved_log = UsageLog(**response.data[0])
        logger.debug(f"   ✅ Usage log saved with ID: {saved_log.id}")
        return saved_log
    except Exception as e:
        logger.error(f"   ❌ Error saving usage log: {type(e).__name__}: {str(e)}", exc_info=True)
        raise


def get_user_queries(user_id: str, limit: int = 50) -> List[Query]:
    """Get user's query history."""
    logger.debug(f"   🔍 Fetching query history | User: {user_id[:8]}... | Limit: {limit}")
    try:
        response = (
            supabase.table("queries")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=False)
            .limit(limit)
            .execute()
        )
        # Reverse to get newest first
        data = response.data if response.data else []
        data.reverse()
        queries = [Query(**item) for item in data]
        logger.debug(f"   ✅ Retrieved {len(queries)} queries")
        return queries
    except Exception as e:
        logger.error(f"   ❌ Error fetching queries: {type(e).__name__}: {str(e)}", exc_info=True)
        raise


def get_user_usage_today(user_id: str) -> dict:
    """Get user's usage stats for today."""
    logger.debug(f"   🔍 Fetching today's usage | User: {user_id[:8]}...")
    try:
        today = datetime.utcnow().date().isoformat()
        response = (
            supabase.table("usage_logs")
            .select("tokens_in, tokens_out, total_tokens, cost")
            .eq("user_id", user_id)
            .gte("created_at", f"{today}T00:00:00")
            .execute()
        )
        
        data = response.data if response.data else []
        total_tokens = sum(item["total_tokens"] for item in data)
        total_cost = sum(item["cost"] for item in data)
        count = len(data)
        
        logger.debug(
            f"   ✅ Usage stats | Tokens: {total_tokens:,} | "
            f"Cost: ${total_cost:.4f} | Requests: {count}"
        )
        
        return {
            "total_tokens": total_tokens,
            "total_cost": total_cost,
            "request_count": count
        }
    except Exception as e:
        logger.error(f"   ❌ Error fetching usage: {type(e).__name__}: {str(e)}", exc_info=True)
        raise


def get_admin_metrics() -> dict:
    """Get admin metrics."""
    # Total users
    users_response = supabase.table("users").select("id").execute()
    total_users = len(users_response.data) if users_response.data else 0
    
    # Total queries
    queries_response = supabase.table("queries").select("id").execute()
    total_queries = len(queries_response.data) if queries_response.data else 0
    
    # Total usage
    usage_response = supabase.table("usage_logs").select("total_tokens, cost").execute()
    total_tokens = sum(item["total_tokens"] for item in usage_response.data) if usage_response.data else 0
    total_cost = sum(item["cost"] for item in usage_response.data) if usage_response.data else 0
    
    return {
        "total_users": total_users,
        "total_queries": total_queries,
        "total_tokens": total_tokens,
        "total_cost": total_cost
    }


def get_admin_costs() -> dict:
    """Get cost breakdown by difficulty."""
    response = supabase.table("usage_logs").select("difficulty, cost, total_tokens").execute()
    
    breakdown = {"EASY": {"cost": 0, "tokens": 0}, "MEDIUM": {"cost": 0, "tokens": 0}, "HARD": {"cost": 0, "tokens": 0}}
    
    data = response.data if response.data else []
    for item in data:
        diff = item["difficulty"]
        if diff in breakdown:
            breakdown[diff]["cost"] += item["cost"]
            breakdown[diff]["tokens"] += item["total_tokens"]
    
    return breakdown


def get_routing_stats() -> dict:
    """Get routing statistics."""
    response = supabase.table("queries").select("routing_source, final_label").execute()
    
    routing_counts = {"algorithmic": 0, "ml": 0, "user_override": 0}
    difficulty_counts = {"EASY": 0, "MEDIUM": 0, "HARD": 0}
    
    data = response.data if response.data else []
    for item in data:
        source = item["routing_source"]
        label = item["final_label"]
        
        if source in routing_counts:
            routing_counts[source] += 1
        
        if label in difficulty_counts:
            difficulty_counts[label] += 1
    
    return {
        "routing_sources": routing_counts,
        "difficulty_distribution": difficulty_counts
    }


def get_queries_by_time_range(
    start_time: datetime, 
    end_time: datetime, 
    user_id: Optional[str] = None
) -> List[Query]:
    """
    Get queries within a time range.
    """
    query = (
        supabase.table("queries")
        .select("*")
        .gte("created_at", start_time.isoformat())
        .lte("created_at", end_time.isoformat())
    )
    
    if user_id:
        query = query.eq("user_id", user_id)
    
    response = query.order("created_at", desc=False).execute()
    data = response.data if response.data else []
    return [Query(**item) for item in data]

