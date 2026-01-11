#!/bin/bash
# Auto-Discovery Script
# Automatically detects your current network and scans it
# Use this when you plug into an unknown customer network

echo "======================================"
echo "Network Auto-Discovery"
echo "======================================"
echo ""

# Function to get primary network interface
get_primary_interface() {
    # Get the interface with default route (excluding lo and docker)
    ip route | grep default | awk '{print $5}' | head -1
}

# Function to get IP and subnet for an interface
get_network_info() {
    local iface=$1
    # Get IP address and CIDR
    ip addr show "$iface" | grep "inet " | grep -v "127.0.0.1" | awk '{print $2}' | head -1
}

# Function to calculate network address from IP/CIDR
get_network_address() {
    local ip_cidr=$1
    python3 -c "
import ipaddress
network = ipaddress.ip_interface('$ip_cidr').network
print(f'{network}')
"
}

echo "Step 1: Detecting network interfaces..."
echo ""

# Get all non-loopback interfaces
interfaces=$(ip -o link show | awk -F': ' '{print $2}' | grep -v "^lo$" | grep -v "^docker")

echo "Available interfaces:"
for iface in $interfaces; do
    ip_info=$(ip addr show "$iface" | grep "inet " | awk '{print $2}' | head -1)
    if [ -n "$ip_info" ]; then
        echo "  ✓ $iface: $ip_info"
    else
        echo "  - $iface: No IP assigned"
    fi
done
echo ""

# Get primary interface
PRIMARY_IFACE=$(get_primary_interface)

if [ -z "$PRIMARY_IFACE" ]; then
    echo "❌ Error: No network interface with IP found"
    echo ""
    echo "Troubleshooting:"
    echo "  1. Check if you're connected to the network (cable plugged in)"
    echo "  2. Verify DHCP is working: ip addr show"
    echo "  3. Try manually: dhclient <interface>"
    exit 1
fi

echo "Step 2: Primary interface detected: $PRIMARY_IFACE"
echo ""

# Get IP and subnet
IP_CIDR=$(get_network_info "$PRIMARY_IFACE")

if [ -z "$IP_CIDR" ]; then
    echo "❌ Error: No IP address assigned to $PRIMARY_IFACE"
    exit 1
fi

echo "Step 3: Your IP assignment:"
echo "  Interface: $PRIMARY_IFACE"
echo "  IP/CIDR: $IP_CIDR"
echo ""

# Extract IP and subnet
YOUR_IP=$(echo "$IP_CIDR" | cut -d'/' -f1)
CIDR=$(echo "$IP_CIDR" | cut -d'/' -f2)

# Calculate network address
NETWORK=$(get_network_address "$IP_CIDR")

echo "Step 4: Calculated network information:"
echo "  Your IP: $YOUR_IP"
echo "  Subnet Mask: /$CIDR"
echo "  Network: $NETWORK"
echo ""

# Calculate estimated scan time
HOSTS=$((2 ** (32 - CIDR) - 2))
if [ $HOSTS -gt 1000 ]; then
    EST_TIME="30-60 minutes"
elif [ $HOSTS -gt 100 ]; then
    EST_TIME="5-15 minutes"
else
    EST_TIME="1-5 minutes"
fi

echo "  Scannable hosts: ~$HOSTS"
echo "  Estimated scan time: $EST_TIME"
echo ""

# Show gateway
GATEWAY=$(ip route | grep default | awk '{print $3}' | head -1)
if [ -n "$GATEWAY" ]; then
    echo "  Default Gateway: $GATEWAY"
    echo ""
fi

# Ask if they want to proceed
read -p "Do you want to scan this network? (y/n): " PROCEED

if [ "$PROCEED" != "y" ] && [ "$PROCEED" != "Y" ]; then
    echo ""
    echo "Scan cancelled."
    echo ""
    echo "To scan manually:"
    echo "  nmap -sn $NETWORK"
    exit 0
fi

echo ""
echo "======================================"
echo "Starting Network Scan"
echo "======================================"
echo ""

# Create output directory
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="${SCRIPT_DIR}/scans/auto_discovered_${TIMESTAMP}"
mkdir -p "$OUTPUT_DIR"

# Ask scan type
echo "Select scan type:"
echo "  1. Quick Discovery (ping sweep only - fastest)"
echo "  2. Port Scan (top 1000 ports)"
echo "  3. Intense Scan (full OS/service detection)"
read -p "Select (1-3) [default: 1]: " SCAN_TYPE
SCAN_TYPE=${SCAN_TYPE:-1}

echo ""

case $SCAN_TYPE in
    1)
        echo "Running quick discovery scan..."
        SCAN_NAME="quick_discovery"
        nmap -sn -n "$NETWORK" -oA "${OUTPUT_DIR}/${SCAN_NAME}" | tee "${OUTPUT_DIR}/scan_output.txt"
        ;;
    2)
        echo "Running port scan (this may take a while)..."
        SCAN_NAME="port_scan"
        nmap -F -T3 "$NETWORK" -oA "${OUTPUT_DIR}/${SCAN_NAME}" | tee "${OUTPUT_DIR}/scan_output.txt"
        ;;
    3)
        echo "Running intense scan (this will take significant time)..."
        SCAN_NAME="intense_scan"
        nmap -T3 -A -v "$NETWORK" -oA "${OUTPUT_DIR}/${SCAN_NAME}" | tee "${OUTPUT_DIR}/scan_output.txt"
        ;;
    *)
        echo "Invalid selection, using quick discovery..."
        SCAN_NAME="quick_discovery"
        nmap -sn -n "$NETWORK" -oA "${OUTPUT_DIR}/${SCAN_NAME}" | tee "${OUTPUT_DIR}/scan_output.txt"
        ;;
esac

echo ""
echo "======================================"
echo "Scan Complete!"
echo "======================================"
echo ""

# Count live hosts
LIVE_HOSTS=$(grep "Host is up" "${OUTPUT_DIR}/scan_output.txt" | wc -l)

echo "📊 Summary:"
echo "  Network scanned: $NETWORK"
echo "  Your IP: $YOUR_IP"
echo "  Live hosts found: $LIVE_HOSTS"
echo "  Scan type: $SCAN_NAME"
echo ""
echo "📁 Results saved to:"
echo "  $OUTPUT_DIR/"
echo ""
echo "Files created:"
ls -lh "$OUTPUT_DIR/"
echo ""

# Generate quick report
cat > "${OUTPUT_DIR}/NETWORK_INFO.txt" << EOF
Network Auto-Discovery Report
==============================
Scan Date: $(date)
Interface: $PRIMARY_IFACE
Your IP: $YOUR_IP
Network: $NETWORK
Gateway: $GATEWAY
CIDR: /$CIDR
Live Hosts: $LIVE_HOSTS

Network Details:
$(ip addr show "$PRIMARY_IFACE")

Routing Table:
$(ip route)

Live Hosts Discovered:
$(grep "Nmap scan report for" "${OUTPUT_DIR}/${SCAN_NAME}.nmap" | awk '{print $5}')
EOF

echo "📄 Network info saved: ${OUTPUT_DIR}/NETWORK_INFO.txt"
echo ""

# Suggest next steps
echo "📋 Next steps:"
echo "  1. Review results: cat ${OUTPUT_DIR}/${SCAN_NAME}.nmap"
echo "  2. View network info: cat ${OUTPUT_DIR}/NETWORK_INFO.txt"
echo "  3. Create customer config with this network: network-config.py"
echo "  4. Run detailed scans on specific hosts"
echo ""
echo "To use this network in config tool:"
echo "  Primary Network: $NETWORK"
echo ""
