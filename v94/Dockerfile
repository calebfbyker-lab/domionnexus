FROM python:3.11-slim

LABEL maintainer="Caleb Fedor Byker Konev"
LABEL version="94.0.0"
LABEL description="Codex v94 Sentinel - Security hardened with JWKS, Glyph Guard, and SBOM"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py .
COPY glyph_guard_v14.py .
COPY glyph_policy.yaml .
COPY generate_sbom.py .
COPY scan_vulnerabilities.py .
COPY cosign_wrapper.py .
COPY generate_provenance.py .

# Create non-root user
RUN useradd -u 10001 -m -s /bin/bash codex && \
    chown -R codex:codex /app

# Create necessary directories with proper permissions
RUN mkdir -p /tmp /app/.cache && \
    chown -R codex:codex /tmp /app/.cache

# Switch to non-root user
USER codex

# Expose application port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Run application
CMD ["python", "app.py"]
