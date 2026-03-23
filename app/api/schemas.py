from pydantic import BaseModel
from typing import Optional


class QueryRequest(BaseModel):
    query: str
    difficulty_override: Optional[str] = None
    has_image: Optional[bool] = False
    has_document: Optional[bool] = False


class QueryResponse(BaseModel):
    answer: str
    model_name: str
    difficulty: str
    routing_source: str
    usage: dict
    cache_hit: Optional[bool] = False
    modality: Optional[str] = "text"


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


class FeedbackRequest(BaseModel):
    query: str
    difficulty: str
    is_correct: bool
    correct_difficulty: Optional[str] = None  # Required if is_correct is False


class FeedbackResponse(BaseModel):
    success: bool
    message: str
