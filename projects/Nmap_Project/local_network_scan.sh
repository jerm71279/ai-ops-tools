#!/bin/bash
# Local Network Scan - 10.55.1.0/24
# Generated: 2025-11-18
#
# This script performs a comprehensive network scan of your local network

# Configuration
NETWORK="10.55.1.0/24"
OUTPUT_DIR="/home/mavrick/Projects/Nmap_Project/scan_results"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Create output directory
mkdir -p "$OUTPUT_DIR"

echo "============================================================"
echo "LOCAL NETWORK SCANNER - 10.55.1.0/24"
echo "============================================================"
echo ""

# Check if nmap is installed
if ! command -v nmap &> /dev/null; then
    echo "ERROR: nmap is not installed"
    echo "Install with: sudo apt install nmap"
    exit 1
fi

echo "Starting scan at $(date)"
echo "Target: $NETWORK"
echo "Output: $OUTPUT_DIR"
echo ""

# Phase 1: Quick host discovery
echo "[Phase 1] Host Discovery (ping sweep)..."
echo "----------------------------------------"
nmap -sn $NETWORK -oG "$OUTPUT_DIR/discovery_${TIMESTAMP}.gnmap" 2>&1

# Extract live hosts
LIVE_HOSTS=$(grep "Status: Up" "$OUTPUT_DIR/discovery_${TIMESTAMP}.gnmap" | awk '{print $2}' | tr '\n' ' ')
HOST_COUNT=$(grep -c "Status: Up" "$OUTPUT_DIR/discovery_${TIMESTAMP}.gnmap" 2>/dev/null || echo "0")

echo ""
echo "Found $HOST_COUNT live hosts"
echo ""

if [ "$HOST_COUNT" -eq 0 ]; then
    echo "No hosts found. The network may be blocking ping probes."
    echo "Try running with sudo for more accurate results."
    exit 0
fi

# Phase 2: Port scan on live hosts
echo "[Phase 2] Port Scan (common ports)..."
echo "----------------------------------------"
nmap -sV -sC -T4 --top-ports 100 $LIVE_HOSTS \
    -oN "$OUTPUT_DIR/portscan_${TIMESTAMP}.txt" \
    -oX "$OUTPUT_DIR/portscan_${TIMESTAMP}.xml" 2>&1

echo ""
echo "============================================================"
echo "SCAN COMPLETE"
echo "============================================================"
echo ""
echo "Results saved to:"
echo "  - $OUTPUT_DIR/discovery_${TIMESTAMP}.gnmap"
echo "  - $OUTPUT_DIR/portscan_${TIMESTAMP}.txt"
echo "  - $OUTPUT_DIR/portscan_${TIMESTAMP}.xml"
echo ""
echo "Quick Summary:"
echo "----------------------------------------"
grep -E "^Nmap scan report|open" "$OUTPUT_DIR/portscan_${TIMESTAMP}.txt" 2>/dev/null | head -50

echo ""
echo "For full results: cat $OUTPUT_DIR/portscan_${TIMESTAMP}.txt"
