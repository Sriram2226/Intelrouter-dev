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

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
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

