#!/bin/bash
# Spanish Fort Waterboard - Network Discovery Script
# Date: Tomorrow's site visit
# Run this script on-site to scan their network

SITE_NAME="SpanishFort_Waterboard"
SCAN_DATE=$(date +%Y%m%d_%H%M%S)
OUTPUT_DIR="./scans/${SITE_NAME}_${SCAN_DATE}"

echo "=============================================="
echo "  Spanish Fort Waterboard Network Discovery"
echo "=============================================="
echo ""

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Detect network automatically
echo "[1/4] Detecting network configuration..."
GATEWAY=$(ip route | grep default | awk '{print $3}' | head -1)
NETWORK=$(ip route | grep -v default | grep "src" | head -1 | awk '{print $1}')

if [ -z "$NETWORK" ]; then
    # Fallback: try common networks
    echo "Could not auto-detect. Trying common networks..."
    NETWORK="192.168.1.0/24"
fi

echo "      Gateway: $GATEWAY"
echo "      Network: $NETWORK"
echo ""

# Allow manual override
read -p "Press Enter to scan $NETWORK or type a different range: " CUSTOM_NETWORK
if [ -n "$CUSTOM_NETWORK" ]; then
    NETWORK="$CUSTOM_NETWORK"
fi

echo ""
echo "[2/4] Quick Discovery Scan (finding hosts)..."
echo "      Scanning $NETWORK"
nmap -sn "$NETWORK" -oA "$OUTPUT_DIR/01_discovery" | tee "$OUTPUT_DIR/discovery_output.txt"

# Count hosts found
HOSTS_FOUND=$(grep "Host is up" "$OUTPUT_DIR/discovery_output.txt" | wc -l)
echo ""
echo "      Found $HOSTS_FOUND hosts"
echo ""

# Standard scan
echo "[3/4] Standard Scan (common ports + services)..."
nmap -F -sV "$NETWORK" -oA "$OUTPUT_DIR/02_standard" | tee "$OUTPUT_DIR/standard_output.txt"

echo ""
read -p "Run intensive scan on all ports? (y/n): " RUN_INTENSIVE

if [ "$RUN_INTENSIVE" = "y" ] || [ "$RUN_INTENSIVE" = "Y" ]; then
    echo ""
    echo "[4/4] Intensive Scan (all 65535 ports + scripts)..."
    echo "      This may take 20-40 minutes..."
    nmap -p- -sV -sC -T4 "$NETWORK" -oA "$OUTPUT_DIR/03_intensive" | tee "$OUTPUT_DIR/intensive_output.txt"
fi

echo ""
echo "=============================================="
echo "  Scan Complete!"
echo "=============================================="
echo ""
echo "Results saved to: $OUTPUT_DIR"
echo ""
echo "Files:"
ls -la "$OUTPUT_DIR"
echo ""
echo "Quick Summary:"
echo "--------------"
grep "Host is up" "$OUTPUT_DIR/01_discovery.nmap" 2>/dev/null | wc -l
echo " hosts discovered"
echo ""
grep "open" "$OUTPUT_DIR/02_standard.nmap" 2>/dev/null | head -20
