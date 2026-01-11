#!/bin/bash
# Network Discovery Script for Infrastructure Planning
# Usage: ./network-discovery.sh <target-network>

if [ -z "$1" ]; then
    echo "Usage: $0 <target-network>"
    echo "Example: $0 192.168.1.0/24"
    exit 1
fi

TARGET=$1
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="${SCRIPT_DIR}/scans/${TIMESTAMP}"
EXCLUDE_FILE="${SCRIPT_DIR}/exclude.txt"

# Create output directory
mkdir -p "$OUTPUT_DIR"

echo "======================================"
echo "Network Discovery Scan Starting"
echo "Target: $TARGET"
echo "Timestamp: $TIMESTAMP"
echo "Output Directory: $OUTPUT_DIR"
echo "======================================"

# Build exclude option if file exists
EXCLUDE_OPT=""
if [ -f "$EXCLUDE_FILE" ]; then
    EXCLUDE_OPT="--excludefile $EXCLUDE_FILE"
fi

# 1. Quick Ping Sweep - Discover live hosts
echo "[1/5] Running ping sweep to discover live hosts..."
nmap -sn -PE -n "$TARGET" -oA "${OUTPUT_DIR}/01_ping_sweep" $EXCLUDE_OPT 2>/dev/null

# 2. Fast Port Scan - Top 1000 ports on discovered hosts
echo "[2/5] Running fast port scan on common ports..."
nmap -T4 -F "$TARGET" -oA "${OUTPUT_DIR}/02_fast_scan" $EXCLUDE_OPT 2>/dev/null

# 3. Service Version Detection - Identify services
echo "[3/5] Running service version detection..."
nmap -sV -T4 "$TARGET" -oA "${OUTPUT_DIR}/03_service_detection" $EXCLUDE_OPT 2>/dev/null

# 4. OS Detection - Identify operating systems
echo "[4/5] Running OS detection..."
nmap -O -T4 "$TARGET" -oA "${OUTPUT_DIR}/04_os_detection" $EXCLUDE_OPT 2>/dev/null

# 5. Comprehensive Scan - All TCP ports (slower)
echo "[5/5] Running comprehensive TCP scan..."
nmap -p- -T4 "$TARGET" -oA "${OUTPUT_DIR}/05_full_tcp_scan" $EXCLUDE_OPT 2>/dev/null

echo "======================================"
echo "Scan Complete!"
echo "Results saved to: $OUTPUT_DIR"
echo "======================================"

# Generate summary report
echo "Generating summary report..."
cat > "${OUTPUT_DIR}/SUMMARY.txt" << EOF
Network Discovery Summary
=========================
Target Network: $TARGET
Scan Date: $(date)
Scan Duration: Check individual scan files for timing

Files Generated:
- 01_ping_sweep.*      : Live host discovery
- 02_fast_scan.*       : Fast port scan (top 1000 ports)
- 03_service_detection.*: Service and version information
- 04_os_detection.*    : Operating system fingerprinting
- 05_full_tcp_scan.*   : Comprehensive TCP port scan

Note: Each scan has three output formats:
  .nmap - Normal output
  .xml  - XML output (for import into other tools)
  .gnmap - Grepable output

Next Steps for Infrastructure Planning:
1. Review live hosts and IP usage
2. Identify existing services and potential conflicts
3. Document OS types for compatibility planning
4. Map network topology
5. Identify available IP ranges for new infrastructure
EOF

echo "Summary report created: ${OUTPUT_DIR}/SUMMARY.txt"
