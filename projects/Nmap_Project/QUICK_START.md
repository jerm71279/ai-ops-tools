# Quick Start Guide - Customer Network Scanning

## Overview

This system automatically organizes scans by **customer name** - all scan files are named using the customer name you provide during configuration.

---

## File Naming Convention

When you enter a customer name like **"Acme Corporation"**, all files are automatically named:

```
acme_corporation_[type]_[timestamp].[ext]
```

### Example Files Created:

For customer: **"Acme Corporation"**

```
/scans/
├── configs/
│   ├── acme_corporation_20251110_083015.json              # Configuration
│   ├── acme_corporation_20251110_083015_exclude.txt      # Exclusions
│   └── acme_corporation_20251110_083015_scan_plan.sh     # Scan script
│
└── scan_results/
    ├── acme_corporation_primary_20251110_083015.nmap      # Primary network scan
    ├── acme_corporation_primary_20251110_083015.xml
    ├── acme_corporation_primary_20251110_083015.gnmap
    │
    ├── acme_corporation_vlan_10_20251110_083015.nmap      # VLAN 10 scan
    ├── acme_corporation_vlan_10_20251110_083015.xml
    ├── acme_corporation_vlan_10_20251110_083015.gnmap
    │
    └── acme_corporation_vlan_20_20251110_083015.nmap      # VLAN 20 scan
        └── ...
```

---

## 3-Step Process

### Step 1: Build & Start Container

```bash
cd ~/Projects
./quickstart.sh
```

This builds the Kali Linux container with all tools installed.

---

### Step 2: Configure Customer Network

```bash
# Access the container
docker exec -it kali-network-discovery /bin/bash

# Run the configuration tool
network-config.py
```

**You'll be prompted for:**

1. **Customer name** → This becomes your file prefix!
   - Example: "Acme Corporation" → `acme_corporation_*`
   - Example: "Smith & Co." → `smith_co_*`

2. **Customer ID** (optional)
   - Internal tracking code

3. **Contact information**
   - Primary contact name
   - Email address

4. **Authorization**
   - Confirmation you have permission to scan
   - Reference number/ticket

5. **Network information**
   - Primary network (e.g., `192.168.1.0/24`)
   - Additional networks
   - **VLAN details** (ID, name, network range)

6. **Exclusions**
   - Critical systems to skip
   - Auto-generates exclude.txt

7. **Scan preferences**
   - Scan type (Quick/Standard/Intense)
   - Timing (Polite/Normal/Aggressive)

---

### Step 3: Run the Scan

After configuration, the tool creates a ready-to-run scan script:

```bash
# Execute the auto-generated scan plan
/scans/configs/acme_corporation_20251110_083015_scan_plan.sh
```

Or run scans individually:

```bash
# Primary network
network-discovery.sh 192.168.1.0/24

# Intense scan on specific VLAN
intense-scan.sh 10.0.10.0/24 /scans/configs/acme_corporation_*_exclude.txt
```

---

## Customer Name Examples

The system automatically converts customer names to safe filenames:

| Customer Input | Filename Prefix |
|----------------|-----------------|
| "Acme Corporation" | `acme_corporation` |
| "Smith & Jones LLC" | `smith_jones_llc` |
| "Bob's Bakery" | `bobs_bakery` |
| "123 Manufacturing" | `123_manufacturing` |
| "café français" | `cafe_francais` |

**Rules:**
- Converted to lowercase
- Spaces → underscores
- Special characters → underscores or removed
- Safe for all filesystems

---

## Finding Your Scans

### List all scans for a customer:

```bash
# From inside container
ls -lh /scans/acme_corporation_*

# From host
ls -lh ~/Projects/scans/acme_corporation_*
```

### Search by customer name:

```bash
find /scans -name "*acme_corporation*"
```

### View scan results:

```bash
# Human-readable format
cat /scans/acme_corporation_primary_20251110_083015.nmap

# Open in text editor
vim /scans/acme_corporation_vlan_10_20251110_083015.nmap
```

---

## Multiple Customers

The system handles multiple customers easily - each gets their own file prefix:

```
/scans/
├── acme_corporation_primary_20251110_083015.nmap
├── acme_corporation_vlan_10_20251110_083015.nmap
│
├── smith_co_primary_20251110_091500.nmap
├── smith_co_vlan_20_20251110_091500.nmap
│
└── bobs_bakery_primary_20251110_103000.nmap
```

---

## VLAN Scanning Example

### Input:

```
Customer: "TechStart Inc"

VLANs:
  VLAN 10 - Management (10.0.10.0/24)
  VLAN 20 - Servers (10.0.20.0/24)
  VLAN 30 - Workstations (10.0.30.0/24)
```

### Generated Files:

```
/scans/
├── techstart_inc_primary_20251110_120000.nmap     # Primary network
├── techstart_inc_vlan_10_20251110_120000.nmap     # Management VLAN
├── techstart_inc_vlan_20_20251110_120000.nmap     # Server VLAN
└── techstart_inc_vlan_30_20251110_120000.nmap     # Workstation VLAN
```

---

## Using with Claude Desktop

After scanning, you can ask Claude to analyze results using the customer name:

**Example queries:**

```
"Show me the scan results for Acme Corporation"

"What services did we find on Acme Corporation's VLAN 10?"

"List all open ports discovered on Smith & Co network"

"Generate a report for Bob's Bakery infrastructure scan"

"Compare the results from Acme Corporation's management VLAN vs server VLAN"
```

Claude will automatically find files matching the customer name pattern.

---

## Best Practices

### ✅ DO:

1. **Use descriptive customer names**
   - "Acme Corp - Dallas Office" is better than "ACME1"

2. **Keep consistent naming**
   - Always use the same name for the same customer
   - "Acme Corporation" not sometimes "ACME" or "Acme Corp"

3. **Include location for multi-site customers**
   - "Acme Corp - HQ"
   - "Acme Corp - Branch 01"

4. **Document authorization before scanning**
   - The tool prompts for this
   - Keep authorization records with scan results

5. **Review generated exclusion lists**
   - Verify critical systems are excluded
   - Add more if needed before running scans

### ⚠️ DON'T:

1. **Don't use sensitive information in customer names**
   - Names are visible in filenames
   - Avoid proprietary/confidential identifiers

2. **Don't change customer names mid-project**
   - Keeps scans organized together
   - Historical scans won't match

3. **Don't skip the configuration tool**
   - Ensures proper documentation
   - Creates audit trail

4. **Don't share scan files without encryption**
   - Contains network topology
   - Customer confidential information

---

## Troubleshooting

### Issue: "Can't find my scans"

**Solution:**
```bash
# List ALL scans
ls -lh /scans/*.nmap

# Search for customer name
find /scans -name "*customer_name*"

# Check configs directory
ls -lh /scans/configs/
```

### Issue: "Scan files not named with customer"

**Solution:**
- Ensure you used `network-config.py` to create the scan plan
- If running manual scans, use the generated scan plan script
- The auto-generated scripts include customer names

### Issue: "Special characters in customer name"

**Solution:**
- The tool automatically sanitizes names
- "Smith & Jones" becomes "smith_jones"
- This is normal and expected

---

## Directory Structure

```
~/Projects/                                  # Host machine
├── quickstart.sh                            # Container startup script
├── network-config.py                        # Configuration tool (copied to container)
├── network-discovery.sh                     # Discovery scan script
├── intense-scan.sh                          # Intense scan script
│
└── scans/                                   # Mounted volume (shared with container)
    ├── configs/                             # Customer configurations
    │   ├── customer_name_timestamp.json
    │   ├── customer_name_timestamp_exclude.txt
    │   └── customer_name_timestamp_scan_plan.sh
    │
    └── [customer_name]_[segment]_timestamp.*  # Scan results
```

**Inside Container:**

```
/usr/local/bin/
├── network-config.py         # Configuration tool
├── network-discovery.sh      # Discovery scan
├── intense-scan.sh          # Intense scan
└── mcp-nmap-server          # MCP server for Claude

/scans/                      # Mounted from host
├── configs/                 # Customer configs
└── *.nmap, *.xml, *.gnmap  # Scan results
```

---

## Real-World Workflow

### Scenario: New Customer "Global Tech Solutions"

**1. Start Container:**
```bash
./quickstart.sh
```

**2. Configure Customer:**
```bash
docker exec -it kali-network-discovery network-config.py

# Enter:
Customer Name: Global Tech Solutions
Customer ID: GTS-2025-001
Contact: Jane Doe
Email: jdoe@globaltech.com
Authorization: Yes
Reference: SO-12345

Primary Network: 172.16.0.0/16

VLANs:
  10 - Management (172.16.10.0/24)
  20 - Production (172.16.20.0/23)
  30 - Development (172.16.30.0/24)
  40 - Guest (172.16.40.0/24)

Exclusions:
  172.16.10.1 - Core router
  172.16.20.5 - Production database
  172.16.20.10 - Exchange server

Scan Type: Intense
Timing: Normal (T3)
```

**3. Review Generated Files:**
```bash
ls /scans/configs/global_tech_solutions_*

# Output:
global_tech_solutions_20251110_140000.json
global_tech_solutions_20251110_140000_exclude.txt
global_tech_solutions_20251110_140000_scan_plan.sh
```

**4. Execute Scan Plan:**
```bash
/scans/configs/global_tech_solutions_20251110_140000_scan_plan.sh
```

**5. Review Results:**
```bash
ls /scans/global_tech_solutions_*

# Output:
global_tech_solutions_primary_20251110_140000.nmap
global_tech_solutions_vlan_10_20251110_140000.nmap
global_tech_solutions_vlan_20_20251110_140000.nmap
global_tech_solutions_vlan_30_20251110_140000.nmap
global_tech_solutions_vlan_40_20251110_140000.nmap
... (xml and gnmap versions)
```

**6. Analyze with Claude:**
```
"Review the Global Tech Solutions scan results and create an infrastructure summary"
```

---

## Next Steps

1. **Run quickstart.sh** to build the container
2. **Execute network-config.py** for your first customer
3. **Run the generated scan plan**
4. **Review results** in the `/scans` directory
5. **Use Claude** to analyze and report findings

All your scans will be neatly organized by customer name! 🎯
