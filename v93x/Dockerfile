FROM python:3.11-slim

LABEL org.opencontainers.image.source="https://github.com/calebfbyker-lab/domionnexus"
LABEL org.opencontainers.image.description="Codex v93.x Constellation - AI Orchestration Bundle"
LABEL org.opencontainers.image.licenses="MIT"

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create codex directory for artifacts
RUN mkdir -p codex

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python3 -c "import requests; requests.get('http://localhost:8000/health', headers={'x-api-key': 'dev-key'}).raise_for_status()" || exit 1

# Run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
