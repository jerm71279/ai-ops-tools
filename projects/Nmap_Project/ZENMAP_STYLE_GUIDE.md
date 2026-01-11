# Zenmap-Style Scanning Guide

## Overview

The **zenmap-style-scan.sh** script provides comprehensive network analysis similar to Zenmap GUI, including:

✅ **Endpoint IP Addresses** - Complete host inventory
✅ **Services Running** - Detailed service detection with versions
✅ **Vendor Information** - Hardware/software vendor identification
✅ **Network Topology Map** - Visual ASCII representation
✅ **OS Fingerprinting** - Operating system detection
✅ **GraphML Export** - Import to visualization tools

---

## Quick Start

### Basic Usage:

```bash
docker exec kali-network-discovery zenmap-style-scan.sh <network> [customer-name]
```

### Examples:

```bash
# Scan with default name
docker exec kali-network-discovery zenmap-style-scan.sh 192.168.1.0/24

# Scan with customer name
docker exec kali-network-discovery zenmap-style-scan.sh 192.168.1.0/24 acme_corp

# Scan discovered network
docker exec kali-network-discovery zenmap-style-scan.sh 10.50.0.0/16 customer_site1
```

---

## What You Get

### 📄 Report 1: DETAILED_HOST_REPORT.txt

**Zenmap-style host-by-host breakdown:**

```
HOST #1: 192.168.65.254
════════════════════════════════════════════════════════════════

  Hostname:      server1.domain.local
  MAC Address:   5A:94:EF:E4:0C:DD
  Vendor:        Microsoft Corporation     ← VENDOR
  OS Detected:   Microsoft Windows Server 2019 (99% accuracy)

  OPEN PORTS & SERVICES:
  ──────────────────────────────────────────────────────────────
  Port       State    Service         Version/Vendor
  ──────────────────────────────────────────────────────────────
  135/tcp    open     msrpc           Microsoft Windows RPC
  445/tcp    open     microsoft-ds    Microsoft Windows Server 2019
  3389/tcp   open     ms-wbt-server   Microsoft Terminal Services
  80/tcp     open     http            Apache httpd 2.4.41
  22/tcp     open     ssh             OpenSSH 7.6p1 Ubuntu
```

**Shows for EACH host:**
- IP address
- Hostname (if available)
- MAC address
- **Hardware/Software Vendor**
- **Operating System with confidence %**
- Every open port
- **Service name with version**
- **Product vendor** (Apache, Microsoft, Cisco, etc.)

---

### 📄 Report 2: NETWORK_TOPOLOGY.txt

**Visual network map:**

```
                    ┌─────────────────┐
                    │   INTERNET /    │
                    │   EXTERNAL      │
                    └────────┬────────┘
                             │
                    ┌────────┴────────┐
                    │  GATEWAY/ROUTER │
                    │  192.168.1.1    │
                    │  Cisco Systems  │ ← VENDOR
                    └────────┬────────┘
                             │
    ┌────────────────────────┼────────────────────────┐
    │                        │                        │
┌────────────────┐   ┌──────────────┐   ┌──────────────┐
│ 192.168.1.10   │   │ 192.168.1.20 │   │ 192.168.1.30 │
│ Dell Inc.      │   │ HP Enterprise│   │ Apple Inc.   │
│ Windows Server │   │ Linux Server │   │ macOS        │
└────────────────┘   └──────────────┘   └──────────────┘
```

**Shows:**
- Network hierarchy
- Device relationships
- Vendor for each device
- Visual connections

---

###  📄 Report 3: SERVICE_SUMMARY.txt

**Services grouped by type:**

```
WEB SERVERS:
  192.168.1.10:80    → Apache httpd 2.4.41
  192.168.1.10:443   → Apache httpd 2.4.41 (SSL)
  192.168.1.20:8080  → nginx 1.18.0

DNS SERVERS:
  192.168.1.1:53     → ISC BIND 9.16.1
  192.168.1.5:53     → dnsmasq 2.80

DATABASE SERVERS:
  192.168.1.15:3306  → MySQL 5.7.33
  192.168.1.16:5432  → PostgreSQL 12.5

WINDOWS SERVICES:
  192.168.1.50:135   → Microsoft Windows RPC
  192.168.1.50:445   → Microsoft Windows Server 2019
  192.168.1.50:3389  → Microsoft Terminal Services

MAIL SERVERS:
  192.168.1.25:25    → Postfix smtpd
  192.168.1.25:143   → Dovecot imapd 2.3.7
```

---

### 📄 Bonus: network_topology.graphml

**Import to visualization tools:**

- **yEd Graph Editor** (Free - https://www.yworks.com/products/yed)
- **Gephi** (Network visualization)
- **Cytoscape** (Scientific visualization)
- **Microsoft Visio** (Professional diagrams)
- **Draw.io** (Free online tool)

**Creates interactive, professional network diagrams!**

---

## Scan Phases

The script runs 5 comprehensive phases:

```
🔍 Phase 1: Host Discovery
   └─ Finds all live hosts on network

🔍 Phase 2: Port Scanning
   └─ Scans all TCP ports on discovered hosts

🔍 Phase 3: Service & Version Detection
   └─ Identifies service versions and vendors

🔍 Phase 4: OS Fingerprinting
   └─ Determines operating systems

🔍 Phase 5: Comprehensive NSE Scan
   └─ Runs additional scripts for extra intel
```

**Total Time:** 5-15 minutes depending on network size

---

## Complete Workflow Example

### Scenario: Customer Site Visit

```bash
# Step 1: Auto-discover their network
docker exec -it kali-network-discovery auto-discover-network.sh
# Output: Network detected: 10.50.0.0/16

# Step 2: Run Zenmap-style comprehensive scan
docker exec kali-network-discovery zenmap-style-scan.sh 10.50.0.0/16 techcorp_hq

# Step 3: Wait 10 minutes for completion
# (Scan runs all 5 phases)

# Step 4: Review results
docker exec kali-network-discovery cat /scans/techcorp_hq_*/DETAILED_HOST_REPORT.txt

# Step 5: View topology
docker exec kali-network-discovery cat /scans/techcorp_hq_*/NETWORK_TOPOLOGY.txt

# Step 6: Access from Windows
# Navigate to: \\wsl.localhost\Ubuntu\home\mavrick\Projects\scans\techcorp_hq_*\
```

---

## Output Files Created

```
/scans/customer_name_20251110_150000/
├── DETAILED_HOST_REPORT.txt         ← Main report (like Zenmap)
├── NETWORK_TOPOLOGY.txt             ← Visual topology map
├── SERVICE_SUMMARY.txt              ← Services by type
├── network_topology.graphml         ← Import to viz tools
│
├── 01_host_discovery.nmap           ← Raw nmap outputs
├── 01_host_discovery.xml
├── 02_port_scan.nmap
├── 02_port_scan.xml
├── 03_service_detection.nmap
├── 03_service_detection.xml
├── 04_os_detection.nmap
├── 04_os_detection.xml
├── 05_comprehensive.nmap
└── 05_comprehensive.xml
```

---

## Vendor Detection Examples

The script identifies vendors for:

### Hardware Vendors:
- Cisco Systems
- Dell Inc.
- HP/HPE
- Apple Inc.
- Ubiquiti Networks
- Netgear
- TP-Link
- MikroTik

### Software Vendors:
- Microsoft (Windows, IIS, SQL Server)
- Apache Software Foundation
- nginx Inc.
- Oracle Corporation
- PostgreSQL Global Development Group
- ISC (BIND DNS)
- OpenSSH Project

### Network Equipment:
- Fortinet (FortiGate)
- Palo Alto Networks
- SonicWall
- Juniper Networks
- Aruba Networks

---

## OS Detection Examples

**Windows:**
```
OS Detected: Microsoft Windows Server 2019 (99% accuracy)
OS Detected: Microsoft Windows 10 Professional (95% accuracy)
OS Detected: Microsoft Windows Server 2016 (92% accuracy)
```

**Linux:**
```
OS Detected: Linux 4.15-5.8 (Ubuntu 18.04-20.04) (98% accuracy)
OS Detected: Linux 3.10-4.11 (CentOS 7) (94% accuracy)
OS Detected: Linux 5.4 (Debian 10) (96% accuracy)
```

**Network Devices:**
```
OS Detected: Cisco IOS 15.2 (97% accuracy)
OS Detected: FortiOS 6.4 (93% accuracy)
OS Detected: pfSense 2.5 (91% accuracy)
```

---

## Service Version Examples

```
PORT     SERVICE       VERSION/VENDOR
───────────────────────────────────────────────────────────
22/tcp   ssh           OpenSSH 8.2p1 Ubuntu 4ubuntu0.3
80/tcp   http          Apache httpd 2.4.41 ((Ubuntu))
443/tcp  ssl/http      Apache httpd 2.4.41
3306/tcp mysql         MySQL 5.7.33-0ubuntu0.18.04.1
5432/tcp postgresql    PostgreSQL DB 12.5
6379/tcp redis         Redis key-value store 5.0.7
8080/tcp http-proxy    Squid http proxy 4.10
```

---

## Integration with Customer Config

After running Zenmap-style scan:

```bash
# Use discovered info to create customer config
docker exec -it kali-network-discovery network-config.py

# Enter information from scan:
Customer Name: TechCorp HQ
Primary Network: 10.50.0.0/16
Gateway: 10.50.0.1

Exclusions (from scan results):
  10.50.0.1    (Gateway - Cisco Router)
  10.50.1.10   (Domain Controller - Windows Server 2019)
  10.50.2.5    (Database Server - MySQL)
```

---

## Viewing Results on Windows

### Option 1: File Explorer
```
1. Open File Explorer
2. Navigate to: \\wsl.localhost\Ubuntu\home\mavrick\Projects\scans\
3. Find your scan folder: customer_name_20251110_150000\
4. Open DETAILED_HOST_REPORT.txt in Notepad
```

### Option 2: From WSL
```bash
cd ~/Projects/scans/customer_name_*/
cat DETAILED_HOST_REPORT.txt
cat NETWORK_TOPOLOGY.txt
```

---

## Comparison: Zenmap GUI vs This Tool

| Feature | Zenmap GUI | zenmap-style-scan.sh |
|---------|------------|----------------------|
| **Host Discovery** | ✅ Yes | ✅ Yes |
| **Service Detection** | ✅ Yes | ✅ Yes |
| **Vendor ID** | ✅ Yes | ✅ Yes |
| **OS Detection** | ✅ Yes | ✅ Yes |
| **Topology Map** | ✅ Visual | ✅ ASCII Art |
| **Export Format** | XML | XML + GraphML |
| **Runs on Server** | ❌ No | ✅ Yes |
| **CLI/Remote** | ❌ GUI Only | ✅ CLI Ready |
| **Customer Reports** | Manual | ✅ Auto-generated |

---

## Advanced Usage

### Scan Specific Subnets:
```bash
# Scan just servers VLAN
zenmap-style-scan.sh 10.50.20.0/24 customer_servers

# Scan just workstations
zenmap-style-scan.sh 10.50.30.0/24 customer_workstations
```

### Multiple Sites:
```bash
# Site 1
zenmap-style-scan.sh 192.168.1.0/24 acme_site1

# Site 2
zenmap-style-scan.sh 192.168.2.0/24 acme_site2

# Site 3
zenmap-style-scan.sh 192.168.3.0/24 acme_site3
```

### Import to Visualization Tools:

1. **Get the GraphML file:**
   ```bash
   cp ~/Projects/scans/customer_*/network_topology.graphml ~/Downloads/
   ```

2. **Open in yEd:**
   - Download yEd: https://www.yworks.com/products/yed/download
   - File → Open → Select network_topology.graphml
   - Layout → Hierarchical → Apply
   - Get beautiful network diagram!

---

## Troubleshooting

### Issue: "Scan takes too long"
**Solution:** Large networks take time. For /16 or larger:
```bash
# Option 1: Scan in chunks
zenmap-style-scan.sh 10.50.0.0/24  # First subnet
zenmap-style-scan.sh 10.50.1.0/24  # Second subnet

# Option 2: Use faster timing (less accurate)
# Edit script: change -T4 to -T5
```

### Issue: "OS detection failed"
**Cause:** Firewall blocking OS fingerprinting packets
**Solution:** Expected for some devices, vendor info still available

### Issue: "Service version unknown"
**Cause:** Service banner disabled or custom service
**Solution:** Port number still shows what service likely is

---

## Real-World Use Cases

### 1. **Infrastructure Documentation**
- Scan entire network
- Generate topology map
- Document all services and vendors
- Keep for reference

### 2. **Pre-Deployment Assessment**
- Scan before installing new equipment
- Identify available IPs
- Check for conflicts
- Plan new deployments

### 3. **Security Audits**
- Identify outdated software versions
- Find unsupported OSes
- Locate unauthorized services
- Compliance reporting

### 4. **Vendor Management**
- Identify all vendor equipment
- Track warranty/support status
- Plan upgrades by vendor
- License management

### 5. **Network Changes**
- Before/after comparison
- Verify new deployments
- Validate configurations
- Change documentation

---

## Command Reference

```bash
# Basic scan
zenmap-style-scan.sh <network>

# Named scan
zenmap-style-scan.sh <network> <customer-name>

# View main report
cat /scans/<name>_*/DETAILED_HOST_REPORT.txt

# View topology
cat /scans/<name>_*/NETWORK_TOPOLOGY.txt

# View services
cat /scans/<name>_*/SERVICE_SUMMARY.txt

# Find scan results
ls -lh /scans/

# From Windows
# \\wsl.localhost\Ubuntu\home\mavrick\Projects\scans\
```

---

## Summary

**zenmap-style-scan.sh provides everything Zenmap does:**

✅ **All endpoint IPs** - Complete inventory
✅ **All services** - With versions
✅ **All vendors** - Hardware and software
✅ **Network topology** - Visual ASCII map
✅ **OS detection** - With confidence scores
✅ **Professional reports** - Customer-ready
✅ **Export capability** - GraphML for visualization

**Plus additional benefits:**
- Runs on headless servers
- Remote execution via Docker
- Auto-generated reports
- Customer-named output
- Integration with config tool

---

**You now have full Zenmap functionality in CLI format!** 🎯
