#!/bin/bash
# Zenmap-style Intense Scan
# Equivalent to: nmap -T4 -A -v <target>
# 
# This performs:
# - OS detection (-O)
# - Version detection (-sV)
# - Script scanning (-sC)
# - Traceroute (--traceroute)
# - Aggressive timing (-T4)
# - Verbose output (-v)

if [ -z "$1" ]; then
    echo "Usage: $0 <target-network> [exclude-file]"
    echo "Example: $0 192.168.1.0/24"
    echo "Example: $0 192.168.1.0/24 exclude.txt"
    exit 1
fi

TARGET=$1
EXCLUDE_FILE=$2
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="${SCRIPT_DIR}/scans/intense_${TIMESTAMP}"

# Create output directory
mkdir -p "$OUTPUT_DIR"

echo "======================================"
echo "Zenmap Intense Scan"
echo "======================================"
echo "Target: $TARGET"
echo "Timestamp: $TIMESTAMP"
echo "Output Directory: $OUTPUT_DIR"
echo ""
echo "Scan Profile: nmap -T4 -A -v"
echo "  -T4: Aggressive timing"
echo "  -A: Enable OS detection, version detection, script scanning, and traceroute"
echo "  -v: Verbose output"
echo "======================================"
echo ""

# Build command
NMAP_CMD="nmap -T4 -A -v $TARGET"

# Add exclude file if provided
if [ ! -z "$EXCLUDE_FILE" ]; then
    if [ -f "$EXCLUDE_FILE" ]; then
        NMAP_CMD="$NMAP_CMD --excludefile $EXCLUDE_FILE"
        echo "Using exclude file: $EXCLUDE_FILE"
    else
        echo "Warning: Exclude file not found: $EXCLUDE_FILE"
    fi
fi

# Add output files
NMAP_CMD="$NMAP_CMD -oN ${OUTPUT_DIR}/intense_scan.nmap -oX ${OUTPUT_DIR}/intense_scan.xml -oG ${OUTPUT_DIR}/intense_scan.gnmap"

echo "Running command:"
echo "$NMAP_CMD"
echo ""
echo "Starting scan... (this may take a while)"
echo "======================================"
echo ""

# Run the scan
eval $NMAP_CMD

echo ""
echo "======================================"
echo "Scan Complete!"
echo "======================================"
echo "Results saved to: $OUTPUT_DIR"
echo ""
echo "Files generated:"
echo "  - intense_scan.nmap  (human-readable)"
echo "  - intense_scan.xml   (XML format)"
echo "  - intense_scan.gnmap (grepable)"
echo ""

# Generate summary
cat > "${OUTPUT_DIR}/SUMMARY.txt" << EOF
Zenmap Intense Scan Summary
===========================
Scan Type: Intense Scan (nmap -T4 -A -v)
Target: $TARGET
Scan Date: $(date)
Output Directory: $OUTPUT_DIR

Scan Features:
- Aggressive timing (-T4)
- OS detection
- Version detection
- Script scanning
- Traceroute
- Verbose output

Results:
- See intense_scan.nmap for detailed human-readable output
- See intense_scan.xml for machine-readable data
- See intense_scan.gnmap for grep-friendly format

Command Used:
$NMAP_CMD
EOF

echo "Summary: ${OUTPUT_DIR}/SUMMARY.txt"
echo "======================================"
