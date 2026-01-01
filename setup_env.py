"""
Helper script to create .env file from .env.example
Run: python setup_env.py
"""
import shutil
import os

if not os.path.exists(".env"):
    if os.path.exists(".env.example"):
        shutil.copy(".env.example", ".env")
        print("Created .env file from .env.example")
        print("Please edit .env and add your credentials")
    else:
        print("Creating .env file...")
        env_content = """# Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_key

# Hugging Face
HUGGINGFACE_API_KEY=your_huggingface_api_key

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# Limits & Budget
DAILY_TOKEN_LIMIT=100000
COST_PER_1K_EASY=0.001
COST_PER_1K_MEDIUM=0.01
COST_PER_1K_HARD=0.1

# Admin
ADMIN_SECRET_KEY=your_admin_secret_key_here

# App
ENVIRONMENT=development
"""
        with open(".env", "w") as f:
            f.write(env_content)
        print("Created .env file. Please edit it and add your credentials.")
else:
    print(".env file already exists")

