from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class User(BaseModel):
    id: str
    email: str
    role: str
    created_at: datetime


class Query(BaseModel):
    id: Optional[str] = None
    user_id: str
    algorithmic_label: Optional[str] = None
    ml_label: Optional[str] = None
    final_label: str
    routing_source: str
    model_name: str
    created_at: Optional[datetime] = None


class UsageLog(BaseModel):
    id: Optional[str] = None
    user_id: str
    query_id: Optional[str] = None
    model_name: str
    difficulty: str
    tokens_in: int
    tokens_out: int
    total_tokens: int
    cost: float
    created_at: Optional[datetime] = None

