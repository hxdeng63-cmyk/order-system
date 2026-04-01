# ============ Python Runtime ============
FROM python:3.11-slim AS base

# Prevent Python from writing pyc files and buffer output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    # Set default port
    PORT=8088

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    # For healthcheck
    curl \
    # For building some Python packages
    gcc \
    libffi-dev \
    # Clean up
    && rm -rf /var/lib/apt/lists/* \
    # Create non-root user for security
    && groupadd --gid 1000 appgroup \
    && useradd --uid 1000 --gid 1000 --shell /bin/bash --create-home appuser

WORKDIR /app

# ============ Dependencies Stage ============
FROM base AS deps

# Install pip dependencies
COPY requirements.txt .
# Use pip cache mount for faster builds
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir -r requirements.txt

# ============ Application Stage ============
FROM base AS runner

# Copy installed dependencies from deps stage
COPY --from=deps /root/.cache/pip /root/.cache/pip
COPY --from=deps /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=deps /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=appuser:appgroup . .

# Create directories for uploads and app data
RUN mkdir -p /app/static/uploads /app/data && \
    chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

EXPOSE 8088

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8088/health || exit 1

# Run with uvicorn (using bind address for Docker)
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8088"]
