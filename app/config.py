from pydantic_settings import BaseSettings
from typing import Dict


class Settings(BaseSettings):
    # Supabase
    supabase_url: str
    supabase_key: str
    supabase_service_key: str
    
    # Hugging Face
    huggingface_api_key: str
    
    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str = ""
    
    # Limits & Budget
    daily_token_limit: int = 100000
    cost_per_1k_easy: float = 0.001
    cost_per_1k_medium: float = 0.01
    cost_per_1k_hard: float = 0.1
    user_daily_budget: float = 1.0  # USD budget per user per day
    cost_aware_routing: bool = True  # Downgrade model when budget is low
    
    # Admin
    admin_secret_key: str
    
    # App
    environment: str = "development"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

# Model mapping
# MODEL_MAP: Dict[str, str] = {
#     "EASY": "meta-llama/Llama-3.1-8B-Instruct",
#     "MEDIUM": "Qwen/Qwen2.5-7B-Instruct-1M",
#     "HARD": "deepseek-ai/DeepSeek-R1",
#     "VISION": "llava-hf/llava-1.5-7b-hf",     # Vision-capable model
#     "DOCUMENT": "deepseek-ai/DeepSeek-R1",    # Large-context model for documents
# }
MODEL_MAP: Dict[str, str] = {
    "EASY": "meta-llama/Llama-3.1-8B-Instruct",        # ✅ Keep this
    "MEDIUM": "Qwen/Qwen2.5-7B-Instruct",              # ✅ Drop the -1M suffix
    "HARD": "Qwen/Qwen2.5-72B-Instruct",               # ✅ Larger Qwen instead of DeepSeek-R1
    "VISION": "meta-llama/Llama-3.2-11B-Vision-Instruct",  # ✅ Supported vision model
    "DOCUMENT": "Qwen/Qwen2.5-72B-Instruct",           # ✅ Same as HARD
}
# Reasoning keywords
REASONING_KEYWORDS = [
    "why", "explain", "compare", "analyze", "evaluate", "justify",
    "reason", "rationale", "because", "therefore", "conclusion"
]

# System design keywords
SYSTEM_DESIGN_KEYWORDS = [
    "architecture", "scalable", "api", "pipeline", "microservice",
    "distributed", "database", "cache", "load", "performance",
    "optimization", "design pattern", "system design"
]

# Code indicators
CODE_INDICATORS = [
    "class", "def", "import", "function", "variable", "array",
    "object", "method", "syntax", "code", "programming", "algorithm"
]

