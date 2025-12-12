#!/bin/bash
# Claude CLI wrapper for n8n SSH execution
# Usage: claude-query.sh "prompt" [session-id] [--resume]

PROMPT="$1"
SESSION_ID="${2:-}"
RESUME="${3:-}"

if [ -z "$PROMPT" ]; then
    echo "Error: No prompt provided"
    exit 1
fi

if [ -n "$SESSION_ID" ]; then
    if [ "$RESUME" == "--resume" ] || [ "$RESUME" == "-r" ]; then
        claude -r -s "$SESSION_ID" -p "$PROMPT" --output-format text
    else
        claude -s "$SESSION_ID" -p "$PROMPT" --output-format text
    fi
else
    claude -p "$PROMPT" --output-format text
fi
