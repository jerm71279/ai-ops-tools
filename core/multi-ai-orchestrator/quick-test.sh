#!/bin/bash
# MAI Quick Test Script
# Run this to verify your MAI setup

echo "========================================"
echo "   MAI Orchestrator Quick Test"
echo "========================================"
echo ""

cd /home/mavrick/multi-ai-orchestrator

# Test 1: Status Check
echo "TEST 1: Provider Status"
echo "------------------------"
./mai status
echo ""

# Test 2: Claude Test
echo "TEST 2: Claude Provider"
echo "------------------------"
echo "Prompt: Generate a one-line bash command to list files sorted by size"
./mai run --provider claude "Generate a one-line bash command to list files sorted by size. Output ONLY the command, no explanation."
echo ""

# Test 3: List Workflows
echo "TEST 3: Available Workflows"
echo "----------------------------"
./mai workflow --list
echo ""

echo "========================================"
echo "   Quick Test Complete"
echo "========================================"
echo ""
echo "Next steps:"
echo "  1. Test Gemini: ./mai run --provider gemini 'Explain what MAI does in 2 sentences'"
echo "  2. Run workflow: ./mai workflow customer_onboarding --customer Test --portal-url https://example.com"
echo "  3. Read docs: cat /home/mavrick/multi-ai-orchestrator/IMPLEMENTATION.md"
