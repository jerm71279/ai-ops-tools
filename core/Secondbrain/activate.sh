#!/bin/bash
# Quick activation script for Second Brain environment

cd /home/mavrick/Projects/Secondbrain
source venv/bin/activate

echo "✅ Second Brain environment activated!"
echo ""
echo "📍 Location: $(pwd)"
echo "🐍 Python: $(which python)"
echo "📦 Vault: /mnt/c/Users/JeremySmith/OneDrive - Obera Connect/MyVault"
echo ""
echo "Quick commands:"
echo "  python agent_orchestrator.py    # Test the orchestrator"
echo "  claude                          # Start Claude CLI"
echo "  deactivate                      # Exit environment"
echo ""
