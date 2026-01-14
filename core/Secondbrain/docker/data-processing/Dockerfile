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

# Copy core libraries
COPY core/ ./core/

# Copy tool scripts (from new structure)
COPY Tools/SharePoint-Sync/sharepoint_importer.py .
COPY Tools/Data-Processing/slack_importer.py .
COPY Tools/Data-Processing/slab_importer.py .
COPY Tools/Data-Processing/slab_scraper.py .
COPY Tools/SharePoint-Sync/download_sharepoint.py .
COPY Tools/SharePoint-Sync/download_all_sharepoint.py .
COPY Tools/SharePoint-Sync/sync_sharepoint.py .

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
