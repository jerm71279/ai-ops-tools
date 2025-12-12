# Data Processing Container
# Tools: sharepoint_importer, slack_importer, slab_importer, process_batch, download_sharepoint
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN useradd --create-home --shell /bin/bash app

WORKDIR /app

# Copy and install requirements
COPY docker/data-processing/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy tool scripts (from root context)
COPY sharepoint_importer.py .
COPY slack_importer.py .
COPY slab_importer.py .
COPY slab_scraper.py .
COPY download_sharepoint.py .
COPY download_all_sharepoint.py .
COPY sync_sharepoint.py .
COPY config.py .

# Copy API server
COPY docker/data-processing/api_server.py .

# Create data directory and fix ownership
RUN mkdir -p /app/data && chown -R app:app /app

# Switch to non-root user
USER app

# Expose API port
EXPOSE 8080

# Run API server
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "api_server:app"]
