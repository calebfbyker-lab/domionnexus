# Codex Continuum v100 - Continuum Σ (Sigma)
# Production-ready container image

FROM python:3.11-slim

LABEL maintainer="Codex Continuum v100" \
      version="v100" \
      release="Continuum Σ (Sigma)" \
      description="Policy-driven continuous deployment platform"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py .
COPY codex/ ./codex/
COPY policy/ ./policy/
COPY config/ ./config/
COPY runners/ ./runners/
COPY scripts/ ./scripts/
COPY tools/ ./tools/
COPY plugins/ ./plugins/
COPY secrets/ ./secrets/

# Create necessary directories
RUN mkdir -p /app/rollback /app/data

# Set environment variables
ENV APP_VERSION="v100" \
    APP_RELEASE="Continuum Σ (Sigma)" \
    PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Expose port
EXPOSE 8000

# Run as non-root user
RUN useradd -m -u 1000 codex && \
    chown -R codex:codex /app
USER codex

# Start application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
