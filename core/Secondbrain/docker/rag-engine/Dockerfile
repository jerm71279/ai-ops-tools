# RAG Engine Container
# Tools: query_brain, vector_store, rag_web, rebuild_index
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Install system dependencies for ChromaDB
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN useradd --create-home --shell /bin/bash app

WORKDIR /app

# Copy and install requirements
COPY docker/rag-engine/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy tool scripts (from root context)
COPY query_brain.py .
COPY vector_store.py .
COPY rag_web.py .
COPY rebuild_index.py .
COPY config.py .
COPY suggest_links.py .
COPY obsidian_vault.py .
COPY html_generator.py .
COPY structured_store.py .
COPY query_classifier.py .
COPY agentic_rag.py .

# Create data directory for ChromaDB persistence and fix ownership
RUN mkdir -p /app/data/chroma && chown -R app:app /app

# Switch to non-root user
USER app

# Expose API port
EXPOSE 8080

# Mount point for persistent vector store
VOLUME ["/app/data"]

# Run RAG web server
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--timeout", "120", "rag_web:app"]
