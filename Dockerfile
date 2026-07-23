# =============================================================================
# NUPUR32® AI Operating System - Production Dockerfile
# Multi-stage build for optimized, secure deployment
# =============================================================================

# ---- Build Stage ----
FROM python:3.12-slim AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    build-essential \
    cmake \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# ---- Production Stage ----
FROM python:3.12-slim AS production

LABEL maintainer="NUPUR32"
LABEL description="NUPUR32 AI Operating System - Autonomous AI Ecosystem"
LABEL version="2035.0.0"

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r nupur32 && useradd -r -g nupur32 -d /app -s /sbin/nologin nupur32

# Copy Python packages from builder
COPY --from=builder /root/.local /home/nupur32/.local

# Create application directory
WORKDIR /app

# Copy application code
COPY --chown=nupur32:nupur32 ai_ecosystem/ ai_ecosystem/
COPY --chown=nupur32:nupur32 main.py .
COPY --chown=nupur32:nupur32 dashboard_nova.py .
COPY --chown=nupur32:nupur32 requirements.txt .
COPY --chown=nupur32:nupur32 .env.example .env

# Create necessary directories
RUN mkdir -p /app/data /app/logs /app/output /app/memory /app/models

# Set ownership
RUN chown -R nupur32:nupur32 /app

# Switch to non-root user
USER nupur32

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=production

# Expose ports
EXPOSE 8000
EXPOSE 8501
EXPOSE 9090

# Set health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["python", "main.py", "--init"]


# ---- Development Stage ----
FROM production AS development

USER root

# Install development tools
RUN pip install --no-cache-dir \
    pytest \
    pytest-asyncio \
    pytest-cov \
    black \
    ruff \
    mypy

# Copy test files
COPY --chown=nupur32:nupur32 tests/ tests/

USER nupur32

ENV ENVIRONMENT=development
ENV DEBUG=true

CMD ["python", "main.py", "--init", "--debug"]


# ---- Dashboard Stage ----
FROM production AS dashboard

EXPOSE 8501

CMD ["streamlit", "run", "dashboard_nova.py", "--server.port=8501", "--server.address=0.0.0.0"]


# ---- API Stage ----
FROM production AS api

EXPOSE 8000

CMD ["uvicorn", "ai_ecosystem.api:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]