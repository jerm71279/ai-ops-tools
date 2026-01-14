# OberaConnect Tools - Production Docker Image

FROM python:3.11-slim

# Labels
LABEL org.opencontainers.image.title="OberaConnect Tools"
LABEL org.opencontainers.image.description="MSP operations tools - UniFi fleet management, NinjaOne integration"
LABEL org.opencontainers.image.vendor="OberaConnect"
LABEL org.opencontainers.image.version="1.0.0"

# Create non-root user
RUN groupadd -r oberaconnect && useradd -r -g oberaconnect oberaconnect

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir flask requests tenacity redis

# Copy application code
COPY __init__.py .
COPY common/ common/
COPY n8n/ n8n/
COPY ninjaone/ ninjaone/
COPY unifi/ unifi/

# Set ownership
RUN chown -R oberaconnect:oberaconnect /app

# Switch to non-root user
USER oberaconnect

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app
ENV LOG_FORMAT=json
ENV LOG_LEVEL=INFO

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Expose API port
EXPOSE 5000

# Default command - run the API server
CMD ["python", "-c", "from n8n.webhook_api import run_server; run_server()"]
