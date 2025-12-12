# AI Agents Container
# Tools: agent_orchestrator, agent_notebooklm_analyst, mcp_obsidian_server
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN useradd --create-home --shell /bin/bash app

WORKDIR /app

# Copy and install requirements
COPY docker/agents/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy tool scripts (from root context)
COPY agent_orchestrator.py .
COPY agent_notebooklm_analyst.py .
COPY agent_obsidian_manager.py .
COPY config.py .

# Copy API server
COPY docker/agents/api_server.py .

# Create data directories and fix ownership
RUN mkdir -p /app/data/agents /app/data/mcp && chown -R app:app /app

# Switch to non-root user
USER app

# Expose API port
EXPOSE 8080

# Mount point for agent data
VOLUME ["/app/data"]

# Run agent API server
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "--timeout", "300", "api_server:app"]
