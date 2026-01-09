# Backend Dockerfile
# Multi-stage build for FastAPI backend

# Stage 1: Build dependencies
FROM python:3.11-slim as builder

WORKDIR /app

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies to prefix
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies (curl for healthcheck)
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder to /usr/local
# Ensure destination directories exist and copy packages
RUN mkdir -p /usr/local/lib/python3.11/site-packages /usr/local/bin
COPY --from=builder /install/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=builder /install/bin/ /usr/local/bin/

# Verify transformers is installed (for debugging)
RUN python -c "import sys; print('Python path:', sys.path)" && \
    python -c "import transformers; print('transformers version:', transformers.__version__)" || \
    (echo "ERROR: transformers not found" && ls -la /usr/local/lib/python3.11/site-packages/ | grep -i trans && exit 1)

# Copy application code (no training directory - models are in Supabase Storage)
# Since build context is ./app, copy to maintain app/ module structure
COPY . ./app/

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check using curl
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command (production)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
