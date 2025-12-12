"""
Configuration file for Second Brain system
"""
import os
from pathlib import Path

# API Keys
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Model Configuration
CLAUDE_MODEL = "claude-sonnet-4-20250514"  # Latest Claude model

# Paths (WSL-compatible)
BASE_DIR = Path(__file__).parent

# Obsidian vault path (Docker-aware: uses /app/vault in container, WSL path on host)
OBSIDIAN_VAULT_PATH = Path(os.getenv("OBSIDIAN_VAULT_PATH", "/mnt/c/Users/JeremySmith/OneDrive - Obera Connect/MyVault"))

# Project directories (Docker-aware)
INPUT_DOCUMENTS_DIR = BASE_DIR / "input_documents"
PROCESSING_LOGS_DIR = BASE_DIR / "processing_logs"
CHROMA_DB_DIR = Path(os.getenv("CHROMA_PERSIST_DIRECTORY", str(BASE_DIR / "chroma_db")))
ORCHESTRATOR_LOGS_DIR = BASE_DIR / "orchestrator_logs"
NOTEBOOKLM_FEEDBACK_DIR = BASE_DIR / "notebooklm_feedback"
NOTEBOOKLM_EXPORTS_DIR = BASE_DIR / "notebooklm_exports"

# Processing settings
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Consistency thresholds
CONSISTENCY_THRESHOLD = 0.85
CRITICAL_CONSISTENCY_THRESHOLD = 0.70

# Scheduling (cron format)
DAILY_RUN_TIME = "17:00"  # 5 PM
WEEKLY_RUN_DAY = "Friday"
WEEKLY_RUN_TIME = "17:00"

# System version
SYSTEM_VERSION = "1.0.0"
