from pydantic import BaseModel
from typing import Optional


class QueryRequest(BaseModel):
    query: str
    difficulty_override: Optional[str] = None


class QueryResponse(BaseModel):
    answer: str
    model_name: str
    difficulty: str
    routing_source: str
    usage: dict


class UserInfo(BaseModel):
    id: str
    email: str
    role: str


class UsageToday(BaseModel):
    total_tokens: int
    total_cost: float
    request_count: int
    remaining_tokens: int


class OverrideStatus(BaseModel):
    remaining: int
    used: int
    limit: int

