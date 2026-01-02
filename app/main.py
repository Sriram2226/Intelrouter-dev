import logging
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api import query, dashboard, admin
from app.utils.logger import setup_logger

# Set up structured logging
logger = setup_logger("intelrouter.main", logging.INFO)

# Suppress noisy third-party logs
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("hpack").setLevel(logging.WARNING)

app = FastAPI(
    title="IntelRouter API",
    description="Intelligent API Gateway for LLM Routing",
    version="1.0.0"
)

# Request/Response logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests and responses with timing."""
    start_time = time.time()
    
    # Extract request info
    method = request.method
    path = request.url.path
    client_ip = request.client.host if request.client else "unknown"
    query_params = str(request.query_params) if request.query_params else ""
    
    # Log incoming request
    logger.info(f"📥 INCOMING REQUEST | {method} {path} | IP: {client_ip}")
    if query_params:
        logger.debug(f"   Query params: {query_params}")
    
    try:
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        status_code = response.status_code
        
        # Log response with status indicator
        status_emoji = "✅" if 200 <= status_code < 300 else "⚠️" if 300 <= status_code < 400 else "❌"
        logger.info(
            f"📤 RESPONSE | {method} {path} | {status_emoji} {status_code} | "
            f"Duration: {duration:.3f}s | IP: {client_ip}"
        )
        
        return response
        
    except Exception as e:
        # Log errors
        duration = time.time() - start_time
        logger.error(
            f"💥 REQUEST ERROR | {method} {path} | {type(e).__name__}: {str(e)} | "
            f"Duration: {duration:.3f}s | IP: {client_ip}",
            exc_info=True
        )
        raise


# CORS middleware - Allow frontend origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",  # Frontend dev server
        "http://localhost:8081",  # Alternative frontend port
        "http://127.0.0.1:8080",
        "http://127.0.0.1:8081",
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


@app.on_event("startup")
async def startup_event():
    """Log application startup."""
    logger.info("=" * 60)
    logger.info("🚀 IntelRouter API Starting Up")
    logger.info("=" * 60)
    logger.info(f"📋 API Title: {app.title}")
    logger.info(f"📝 Version: {app.version}")
    logger.info(f"🌍 Environment: Development")
    logger.info("✅ All routers loaded successfully")
    logger.info("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """Log application shutdown."""
    logger.info("=" * 60)
    logger.info("🛑 IntelRouter API Shutting Down")
    logger.info("=" * 60)


@app.get("/")
async def root():
    """Root endpoint."""
    logger.debug("📍 Root endpoint accessed")
    return {"message": "IntelRouter API", "status": "running"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    logger.debug("💚 Health check endpoint accessed")
    return {"status": "healthy"}

