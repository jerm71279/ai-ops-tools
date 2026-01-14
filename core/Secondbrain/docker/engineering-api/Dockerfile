# Engineering API Container
# Tools: engineering_tracker, daily_engineering_summary, contract_tracker, ee_team_dashboard
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
COPY docker/engineering-api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy core libraries
COPY core/ ./core/

# Copy tool scripts (from new structure)
COPY Tools/Dashboards/engineering_tracker.py .
COPY Tools/Dashboards/daily_engineering_summary.py .
COPY Tools/Dashboards/contract_tracker.py .
COPY Tools/Dashboards/ee_team_dashboard.py .
COPY Tools/Dashboards/ecs_dashboard.py .

# Copy API server
COPY docker/engineering-api/api_server.py .

# Create data directory and fix ownership
RUN mkdir -p /app/data && chown -R app:app /app

# Switch to non-root user
USER app

# Expose API port
EXPOSE 8080

# Run API server
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "api_server:app"]
