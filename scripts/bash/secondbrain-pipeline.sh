#!/bin/bash
# Secondbrain pipeline execution wrapper
# Usage: secondbrain-pipeline.sh "task" [pipeline-name]

TASK="$1"
PIPELINE="${2:-default}"
SECONDBRAIN_DIR="$HOME/oberaconnect-ai-ops/core/Secondbrain"

if [ -z "$TASK" ]; then
    echo "Error: No task provided"
    exit 1
fi

cd "$SECONDBRAIN_DIR"
python3 -m ai_os.layer1_interface.cli "$TASK" --pipeline "$PIPELINE"
