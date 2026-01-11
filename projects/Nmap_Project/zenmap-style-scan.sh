#!/bin/bash
# Zenmap-Style Comprehensive Network Scan
# Provides: IP inventory, service detection, vendor info, and topology mapping

if [ -z "$1" ]; then
    echo "Usage: $0 <network> [output-name]"
    echo "Example: $0 192.168.1.0/24"
    echo "Example: $0 192.168.1.0/24 customer_name"
    exit 1
fi

NETWORK=$1
OUTPUT_NAME=${2:-"zenmap_scan"}
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_DIR="$HOME/scans/${OUTPUT_NAME}_${TIMESTAMP}"

mkdir -p "$OUTPUT_DIR"

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║           ZENMAP-STYLE COMPREHENSIVE NETWORK SCAN              ║"
echo "╔════════════════════════════════════════════════════════════════╗"
echo ""
echo "Target Network: $NETWORK"
echo "Output Directory: $OUTPUT_DIR"
echo "Timestamp: $(date)"
echo ""
echo "This scan will provide:"
echo "  ✓ Complete host inventory"
echo "  ✓ Service detection with versions"
echo "  ✓ Vendor identification"
echo "  ✓ OS fingerprinting"
echo "  ✓ Network topology mapping"
echo "  ✓ Visual host relationships"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo ""

# Phase 1: Host Discovery
echo "🔍 Phase 1: Host Discovery..."
echo "   Scanning for live hosts..."
nmap -sn "$NETWORK" --host-timeout 2m --max-retries 1 -oA "${OUTPUT_DIR}/01_host_discovery"

LIVE_HOSTS=$(grep "Host is up" "${OUTPUT_DIR}/01_host_discovery.nmap" | wc -l)
echo "   ✓ Found $LIVE_HOSTS live hosts"
echo ""

if [ "$LIVE_HOSTS" -eq 0 ]; then
    echo "⚠️  No live hosts found. Exiting."
    echo "   Check your network range and connectivity."
    exit 1
fi

# Phase 2: Port Scanning
echo "🔍 Phase 2: Port Scanning (Common ports)..."
echo "   Scanning common ports on all hosts..."
nmap -T4 "$NETWORK" --open --host-timeout 5m --max-retries 1 -oA "${OUTPUT_DIR}/02_port_scan"
echo "   ✓ Port scan complete"
echo ""

# Phase 3: Service Detection with Version Info
echo "🔍 Phase 3: Service & Version Detection..."
echo "   Detecting services and versions (this provides vendor info)..."
nmap -sV -T4 "$NETWORK" --version-intensity 5 --host-timeout 10m --max-retries 1 -oA "${OUTPUT_DIR}/03_service_detection"
echo "   ✓ Service detection complete"
echo ""

# Phase 4: OS Detection
echo "🔍 Phase 4: OS Fingerprinting..."
echo "   Identifying operating systems..."
nmap -O "$NETWORK" --host-timeout 5m --max-retries 1 -oA "${OUTPUT_DIR}/04_os_detection"
echo "   ✓ OS detection complete"
echo ""

# Phase 5: Comprehensive Intense Scan
echo "🔍 Phase 5: Comprehensive NSE Script Scan..."
echo "   Running detailed scripts for additional info..."
nmap -A -T4 "$NETWORK" --host-timeout 15m --max-retries 1 -oA "${OUTPUT_DIR}/05_comprehensive"
echo "   ✓ Comprehensive scan complete"
echo ""

echo "════════════════════════════════════════════════════════════════"
echo "📊 Generating Zenmap-Style Reports..."
echo "════════════════════════════════════════════════════════════════"
echo ""

# Generate Host Inventory Report
cat > "${OUTPUT_DIR}/HOST_INVENTORY.txt" << 'HOSTEOF'
╔════════════════════════════════════════════════════════════════╗
║                    HOST INVENTORY REPORT                        ║
║                   (Zenmap-Style Output)                         ║
╔════════════════════════════════════════════════════════════════╗

HOSTEOF

echo "Scan Date: $(date)" >> "${OUTPUT_DIR}/HOST_INVENTORY.txt"
echo "Network: $NETWORK" >> "${OUTPUT_DIR}/HOST_INVENTORY.txt"
echo "Live Hosts: $LIVE_HOSTS" >> "${OUTPUT_DIR}/HOST_INVENTORY.txt"
echo "" >> "${OUTPUT_DIR}/HOST_INVENTORY.txt"
echo "════════════════════════════════════════════════════════════════" >> "${OUTPUT_DIR}/HOST_INVENTORY.txt"
echo "" >> "${OUTPUT_DIR}/HOST_INVENTORY.txt"

# Parse comprehensive scan for detailed host information
python3 << 'PYEOF' > "${OUTPUT_DIR}/DETAILED_HOST_REPORT.txt"
import xml.etree.ElementTree as ET
import sys
import os

xml_file = os.environ.get('OUTPUT_DIR') + '/05_comprehensive.xml'

try:
    tree = ET.parse(xml_file)
    root = tree.getroot()

    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "DETAILED HOST REPORT (Zenmap-Style)" + " " * 23 + "║")
    print("╔" + "═" * 78 + "╗")
    print()

    host_count = 0

    for host in root.findall('host'):
        # Skip if host is down
        status = host.find('status')
        if status is not None and status.get('state') != 'up':
            continue

        host_count += 1

        # Get IP address
        address_elem = host.find("address[@addrtype='ipv4']")
        if address_elem is None:
            address_elem = host.find("address[@addrtype='ipv6']")

        ip_addr = address_elem.get('addr') if address_elem is not None else 'Unknown'

        # Get MAC address and vendor
        mac_elem = host.find("address[@addrtype='mac']")
        mac_addr = mac_elem.get('addr') if mac_elem is not None else 'N/A'
        mac_vendor = mac_elem.get('vendor') if mac_elem is not None else 'Unknown'

        # Get hostname
        hostnames = host.find('hostnames')
        hostname = 'N/A'
        if hostnames is not None:
            hostname_elem = hostnames.find('hostname')
            if hostname_elem is not None:
                hostname = hostname_elem.get('name')

        # Get OS info
        os_info = 'Unknown'
        os_elem = host.find('os')
        if os_elem is not None:
            osmatch = os_elem.find('osmatch')
            if osmatch is not None:
                os_info = osmatch.get('name')
                accuracy = osmatch.get('accuracy')
                os_info += f" ({accuracy}% accuracy)"

        print(f"{'═' * 80}")
        print(f"HOST #{host_count}: {ip_addr}")
        print(f"{'═' * 80}")
        print()
        print(f"  Hostname:      {hostname}")
        print(f"  MAC Address:   {mac_addr}")
        print(f"  Vendor:        {mac_vendor}")
        print(f"  OS Detected:   {os_info}")
        print()

        # Get ports and services
        ports = host.find('ports')
        if ports is not None:
            port_list = ports.findall('port')
            if port_list:
                print("  OPEN PORTS & SERVICES:")
                print("  " + "-" * 76)
                print(f"  {'Port':<10} {'State':<12} {'Service':<15} {'Version/Vendor':<39}")
                print("  " + "-" * 76)

                for port in port_list:
                    state_elem = port.find('state')
                    if state_elem is not None and state_elem.get('state') == 'open':
                        portid = port.get('portid')
                        protocol = port.get('protocol')

                        service_elem = port.find('service')
                        service_name = service_elem.get('name') if service_elem is not None else 'unknown'

                        # Get version info (vendor and version)
                        version_info = ''
                        if service_elem is not None:
                            product = service_elem.get('product', '')
                            version = service_elem.get('version', '')
                            extrainfo = service_elem.get('extrainfo', '')

                            if product:
                                version_info = product
                            if version:
                                version_info += f" {version}"
                            if extrainfo:
                                version_info += f" ({extrainfo})"

                        if not version_info:
                            version_info = 'Version not detected'

                        state = state_elem.get('state')

                        port_str = f"{portid}/{protocol}"
                        print(f"  {port_str:<10} {state:<12} {service_name:<15} {version_info:<39}")

                print()
            else:
                print("  No open ports detected")
                print()

        # Get scripts output if any
        hostscript = host.find('hostscript')
        if hostscript is not None:
            scripts = hostscript.findall('script')
            if scripts:
                print("  ADDITIONAL INFORMATION (NSE Scripts):")
                print("  " + "-" * 76)
                for script in scripts[:5]:  # Limit to first 5 scripts
                    script_id = script.get('id')
                    output = script.get('output', '').replace('\n', '\n  ')
                    print(f"  [{script_id}]")
                    print(f"  {output}")
                    print()

        print()

    print(f"{'═' * 80}")
    print(f"Total Hosts Scanned: {host_count}")
    print(f"{'═' * 80}")

except FileNotFoundError:
    print("Error: Scan results not found. Please ensure scan completed successfully.")
except Exception as e:
    print(f"Error parsing scan results: {e}")

PYEOF

# Generate Network Topology Map
echo "📊 Generating Network Topology Map..."

python3 << 'TOPOEOF' > "${OUTPUT_DIR}/NETWORK_TOPOLOGY.txt"
import xml.etree.ElementTree as ET
import os

xml_file = os.environ.get('OUTPUT_DIR') + '/05_comprehensive.xml'

try:
    tree = ET.parse(xml_file)
    root = tree.getroot()

    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 25 + "NETWORK TOPOLOGY MAP" + " " * 33 + "║")
    print("╔" + "═" * 78 + "╗")
    print()

    # Find gateway (usually .1)
    gateway = None
    hosts = []

    for host in root.findall('host'):
        status = host.find('status')
        if status is not None and status.get('state') == 'up':
            address_elem = host.find("address[@addrtype='ipv4']")
            if address_elem is not None:
                ip = address_elem.get('addr')

                # Get MAC for vendor info
                mac_elem = host.find("address[@addrtype='mac']")
                vendor = mac_elem.get('vendor') if mac_elem is not None else None

                # Get hostname
                hostnames = host.find('hostnames')
                hostname = None
                if hostnames is not None:
                    hostname_elem = hostnames.find('hostname')
                    if hostname_elem is not None:
                        hostname = hostname_elem.get('name')

                # Check if it's likely a gateway
                if ip.endswith('.1') or ip.endswith('.254'):
                    gateway = {'ip': ip, 'vendor': vendor, 'hostname': hostname}
                else:
                    hosts.append({'ip': ip, 'vendor': vendor, 'hostname': hostname})

    # Draw topology
    print("                        ┌─────────────────┐")
    print("                        │   INTERNET /    │")
    print("                        │   EXTERNAL      │")
    print("                        └────────┬────────┘")
    print("                                 │")

    if gateway:
        print("                        ┌────────┴────────┐")
        print(f"                        │  GATEWAY/ROUTER │")
        print(f"                        │  {gateway['ip']:<14} │")
        if gateway['vendor']:
            vendor_short = gateway['vendor'][:14]
            print(f"                        │  {vendor_short:<14} │")
        print("                        └────────┬────────┘")
        print("                                 │")
        print("        ┌────────────────────────┼────────────────────────┐")
    else:
        print("                        ┌────────┴────────┐")
        print("                        │   SWITCH/HUB    │")
        print("                        └────────┬────────┘")
        print("        ┌────────────────────────┼────────────────────────┐")

    # Draw hosts
    print("        │                        │                        │")

    # Group hosts into rows of 3
    for i in range(0, len(hosts), 3):
        row_hosts = hosts[i:i+3]

        # Top of boxes
        line = "   "
        for h in row_hosts:
            line += "┌─────────────────┐   "
        print(line)

        # IP addresses
        line = "   "
        for h in row_hosts:
            ip_display = h['ip'][-15:]  # Last 15 chars of IP
            line += f"│ {ip_display:<15} │   "
        print(line)

        # Vendor/Hostname
        line = "   "
        for h in row_hosts:
            if h['vendor']:
                vendor_display = h['vendor'][:15]
            elif h['hostname']:
                vendor_display = h['hostname'][:15]
            else:
                vendor_display = "Unknown Device"
            line += f"│ {vendor_display:<15} │   "
        print(line)

        # Bottom of boxes
        line = "   "
        for h in row_hosts:
            line += "└─────────────────┘   "
        print(line)
        print()

    print()
    print(f"Total Devices: {len(hosts) + (1 if gateway else 0)}")
    print()

except FileNotFoundError:
    print("Error: Topology data not available")
except Exception as e:
    print(f"Error generating topology: {e}")

TOPOEOF

# Generate Service Summary
cat > "${OUTPUT_DIR}/SERVICE_SUMMARY.txt" << 'SERVEOF'
╔════════════════════════════════════════════════════════════════╗
║                    SERVICE SUMMARY REPORT                       ║
║                   (By Service Type)                             ║
╔════════════════════════════════════════════════════════════════╗

SERVEOF

echo "" >> "${OUTPUT_DIR}/SERVICE_SUMMARY.txt"
echo "Scan Date: $(date)" >> "${OUTPUT_DIR}/SERVICE_SUMMARY.txt"
echo "" >> "${OUTPUT_DIR}/SERVICE_SUMMARY.txt"

# Extract services from scan results
grep -h "open" "${OUTPUT_DIR}/05_comprehensive.nmap" | \
    awk '{print $1, $3}' | \
    sort | uniq >> "${OUTPUT_DIR}/SERVICE_SUMMARY.txt"

# Create GraphML for visualization tools
python3 << 'GRAPHEOF' > "${OUTPUT_DIR}/network_topology.graphml"
import xml.etree.ElementTree as ET
import os

xml_file = os.environ.get('OUTPUT_DIR') + '/05_comprehensive.xml'

try:
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Create GraphML
    print('<?xml version="1.0" encoding="UTF-8"?>')
    print('<graphml xmlns="http://graphml.graphdrawing.org/xmlns">')
    print('  <key id="label" for="node" attr.name="label" attr.type="string"/>')
    print('  <key id="ip" for="node" attr.name="ip" attr.type="string"/>')
    print('  <key id="type" for="node" attr.name="type" attr.type="string"/>')
    print('  <graph id="network" edgedefault="undirected">')

    # Add gateway node
    print('    <node id="gateway">')
    print('      <data key="label">Gateway</data>')
    print('      <data key="type">router</data>')
    print('    </node>')

    node_id = 0
    for host in root.findall('host'):
        status = host.find('status')
        if status is not None and status.get('state') == 'up':
            address_elem = host.find("address[@addrtype='ipv4']")
            if address_elem is not None:
                ip = address_elem.get('addr')
                node_id += 1

                print(f'    <node id="host{node_id}">')
                print(f'      <data key="label">{ip}</data>')
                print(f'      <data key="ip">{ip}</data>')
                print(f'      <data key="type">host</data>')
                print(f'    </node>')

                # Connect to gateway
                print(f'    <edge source="gateway" target="host{node_id}"/>')

    print('  </graph>')
    print('</graphml>')

except:
    pass

GRAPHEOF

echo "   ✓ Host Inventory Report"
echo "   ✓ Detailed Host Report (with services & vendors)"
echo "   ✓ Network Topology Map"
echo "   ✓ Service Summary"
echo "   ✓ GraphML file (importable to visualization tools)"
echo ""

echo "════════════════════════════════════════════════════════════════"
echo "✅ SCAN COMPLETE!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "📁 Results Location: $OUTPUT_DIR"
echo ""
echo "📄 Generated Files:"
ls -lh "$OUTPUT_DIR/" | grep -v "^total" | awk '{print "   " $9 " (" $5 ")"}'
echo ""
echo "🔍 Key Reports to Review:"
echo "   1. DETAILED_HOST_REPORT.txt  - Complete host details (like Zenmap)"
echo "   2. NETWORK_TOPOLOGY.txt      - Visual network map"
echo "   3. SERVICE_SUMMARY.txt       - Services by type"
echo "   4. 05_comprehensive.nmap     - Full scan output"
echo "   5. network_topology.graphml  - Import to visualization tools"
echo ""
echo "💡 View Reports:"
echo "   cat $OUTPUT_DIR/DETAILED_HOST_REPORT.txt"
echo "   cat $OUTPUT_DIR/NETWORK_TOPOLOGY.txt"
echo ""
echo "════════════════════════════════════════════════════════════════"
