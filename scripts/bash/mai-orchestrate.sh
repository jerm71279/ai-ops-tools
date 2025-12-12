#!/bin/bash
# Multi-AI Orchestrator wrapper
# Usage: mai-orchestrate.sh "task" [workflow]

TASK="$1"
WORKFLOW="${2:-default}"
MAI_DIR="$HOME/oberaconnect-ai-ops/core/multi-ai-orchestrator"

if [ -z "$TASK" ]; then
    echo "Error: No task provided"
    exit 1
fi

cd "$MAI_DIR"
./mai "$TASK" --workflow "$WORKFLOW"
