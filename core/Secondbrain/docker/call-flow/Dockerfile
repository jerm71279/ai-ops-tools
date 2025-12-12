# Call Flow Container
# Tools: call_flow_processor, call_flow_generator, call_flow_web
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
COPY docker/call-flow/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy tool scripts (from root context)
COPY call_flow_processor.py .
COPY call_flow_generator.py .
COPY call_flow_web.py .
COPY call_flow_web_auth.py .
COPY config.py .
COPY contract_tracker.py .

# Create data directories and fix ownership
RUN mkdir -p /app/data/call_flows /app/data/templates && chown -R app:app /app

# Switch to non-root user
USER app

# Expose web port
EXPOSE 8080

# Mount point for call flow data
VOLUME ["/app/data"]

# Run call flow web app
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "call_flow_web:app"]
