import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import query, dashboard, admin

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


app = FastAPI(
    title="IntelRouter API",
    description="Intelligent API Gateway for LLM Routing",
    version="1.0.0"
)

# CORS middleware - Allow frontend origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",  # Frontend dev server
        "http://localhost:3000",  # Alternative frontend port
        "http://127.0.0.1:8080",
        "http://127.0.0.1:3000",
        # Add production frontend URL here when deployed
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers
app.include_router(query.router)
app.include_router(dashboard.router)
app.include_router(admin.router)


@app.get("/")
async def root():
    return {"message": "IntelRouter API", "status": "running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}

