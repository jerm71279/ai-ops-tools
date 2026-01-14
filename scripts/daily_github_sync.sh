#!/bin/bash
# Daily GitHub Sync for oberaconnect-ai-ops
# Syncs key directories and commits changes to GitHub
# Runs via cron at 6:00 AM daily

LOG_FILE="/home/mavrick/logs/github_sync.log"
REPO_DIR="/home/mavrick/oberaconnect-ai-ops"

echo "========================================" >> "$LOG_FILE"
echo "GitHub Sync Started: $(date)" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

# ============================================
# STEP 1: Sync Directories to oberaconnect-ai-ops
# ============================================

# Rsync options:
# -a = archive mode (preserves permissions, timestamps, etc.)
# -v = verbose
# --delete = remove files in dest that aren't in source
# --exclude = skip these directories/files

# 1a. Sync Secondbrain (excluding large/generated dirs)
echo "Syncing Secondbrain..." >> "$LOG_FILE"
rsync -a --delete \
    --exclude 'venv/' \
    --exclude 'node_modules/' \
    --exclude '.git/' \
    --exclude '__pycache__/' \
    --exclude '*.pyc' \
    --exclude '.venv/' \
    --exclude 'dist/' \
    --exclude 'build/' \
    --exclude '.cache/' \
    --exclude 'logs/' \
    --exclude '*.log' \
    --exclude 'input_documents/' \
    --exclude 'swa-build/' \
    /home/mavrick/Projects/Secondbrain/ \
    "$REPO_DIR/core/Secondbrain/" >> "$LOG_FILE" 2>&1
echo "  Secondbrain sync complete" >> "$LOG_FILE"

# 1b. Sync network-config-builder
echo "Syncing network-config-builder..." >> "$LOG_FILE"
rsync -a --delete \
    --exclude 'venv/' \
    --exclude '__pycache__/' \
    --exclude '*.pyc' \
    --exclude '.git/' \
    /home/mavrick/Projects/network-config-builder/ \
    "$REPO_DIR/projects/network-config-builder/" >> "$LOG_FILE" 2>&1
echo "  network-config-builder sync complete" >> "$LOG_FILE"

# 1c. Sync scripts
echo "Syncing scripts..." >> "$LOG_FILE"
rsync -a --delete \
    /home/mavrick/scripts/ \
    "$REPO_DIR/scripts/" >> "$LOG_FILE" 2>&1
echo "  scripts sync complete" >> "$LOG_FILE"

# 1d. Sync Setco_Migration
echo "Syncing Setco_Migration..." >> "$LOG_FILE"
rsync -a --delete \
    --exclude '.claude/' \
    /home/mavrick/Projects/Setco_Migration/ \
    "$REPO_DIR/projects/Setco_Migration/" >> "$LOG_FILE" 2>&1
echo "  Setco_Migration sync complete" >> "$LOG_FILE"

# ============================================
# STEP 2: Git Operations
# ============================================

cd "$REPO_DIR" || { echo "ERROR: Cannot cd to $REPO_DIR" >> "$LOG_FILE"; exit 1; }

# Check for changes
CHANGES=$(git status --porcelain | wc -l)
echo "Uncommitted changes: $CHANGES" >> "$LOG_FILE"

if [ "$CHANGES" -eq 0 ]; then
    echo "No changes to commit. Exiting." >> "$LOG_FILE"
    echo "Sync Complete: $(date)" >> "$LOG_FILE"
    exit 0
fi

# Show summary of changes
echo "Changed files:" >> "$LOG_FILE"
git status --short | head -50 >> "$LOG_FILE"
if [ "$CHANGES" -gt 50 ]; then
    echo "  ... and $((CHANGES - 50)) more files" >> "$LOG_FILE"
fi

# Stage all changes
git add -A >> "$LOG_FILE" 2>&1

# Commit with timestamp
COMMIT_MSG="Daily sync $(date +%Y-%m-%d) - $CHANGES files"
git commit -m "$COMMIT_MSG" >> "$LOG_FILE" 2>&1

if [ $? -eq 0 ]; then
    echo "Committed: $COMMIT_MSG" >> "$LOG_FILE"
else
    echo "ERROR: Commit failed" >> "$LOG_FILE"
    exit 1
fi

# Push to origin
git push origin main >> "$LOG_FILE" 2>&1

if [ $? -eq 0 ]; then
    echo "Pushed to GitHub successfully" >> "$LOG_FILE"
else
    echo "ERROR: Push failed" >> "$LOG_FILE"
    exit 1
fi

echo "Sync Complete: $(date)" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"
