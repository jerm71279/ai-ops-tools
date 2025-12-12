#!/bin/bash
# Claude CLI agent mode for autonomous tasks
# Usage: claude-agent.sh "task" [working-directory]
# WARNING: Runs with --dangerously-skip-permissions

TASK="$1"
WORKDIR="${2:-$(pwd)}"

if [ -z "$TASK" ]; then
    echo "Error: No task provided"
    exit 1
fi

cd "$WORKDIR"
claude --dangerously-skip-permissions -p "$TASK" --output-format text
