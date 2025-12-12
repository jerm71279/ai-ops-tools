# Network Site Assessment Process
## OberaConnect Standard Operating Procedure

**Created:** 2025-12-01
**Last Updated:** 2025-12-01
**Based on:** Spanish Fort Waterboard Assessment

---

## Overview

This procedure documents the complete workflow for conducting network assessments at customer sites, including multi-location customers. The process covers network scanning, documentation, and SharePoint upload.

### Deliverables Per Customer
For each network assessment, the following documents must be created:

1. **Network Scan Report (Markdown)** - `Network_Scan_Report_[Customer]_[Date].md`
2. **Network Scan Report (Interactive HTML)** - `Network_Scan_Report_[Customer].html`
3. **Network Checklist (Markdown)** - `Network_Checklist_[Customer]_[Date].md`
4. **Network Checklist (Interactive HTML)** - `Network_Checklist_[Customer].html`

All four files must be uploaded to SharePoint in the customer's Technical Docs folder.

---

## Pre-Assessment Requirements

### Authorization
- [ ] Confirm authorized access to customer network
- [ ] Ensure technician is on-site or has VPN access
- [ ] Verify customer contact information

### Tools Required
- Windows machine with nmap installed (or WSL with PowerShell access)
- Python environment with `requests` library
- Azure credentials configured in `.env` file
- Access to OberaConnect SharePoint

---

## Phase 1: Network Discovery

### Step 1: Identify Network
```bash
# From WSL, get Windows network info
powershell.exe -Command "ipconfig /all"
```

Look for:
- WiFi adapter (not WSL virtual adapter)
- IPv4 Address (e.g., 192.168.1.x)
- Default Gateway
- Subnet Mask

### Step 2: Create Scan Output Directory
```bash
# Create scan directory with timestamp
SCAN_DIR="/home/mavrick/Projects/NetworkScannerSuite/service/scans/[customer]_[date]"
mkdir -p "$SCAN_DIR"

# Also create Windows temp directory
powershell.exe -Command "mkdir C:\Temp\[customer]_scan -Force"
```

### Step 3: Run Discovery Scan
```bash
# Find all live hosts on network
powershell.exe -Command "nmap -sn 192.168.1.0/24 -oA C:\Temp\[customer]_scan\01_discovery"
```

### Step 4: Run Standard Port Scan
```bash
# Extract host IPs from discovery, then scan common ports
powershell.exe -Command "nmap -F -sV [host_list] -oA C:\Temp\[customer]_scan\02_standard"
```

### Step 5: Run Intensive Scan (Optional)
```bash
# Full port scan with scripts - can take 20-40 minutes
# Use timeout flags to skip slow/filtered hosts
powershell.exe -Command "nmap -F -sV -T5 --host-timeout 60s [host_list] -oA C:\Temp\[customer]_scan\03_intensive"
```

**Note:** If hosts are heavily filtered, use faster scan with timeout:
```bash
powershell.exe -Command "nmap -F -sV -T5 --host-timeout 60s [host_list]"
```

---

## Phase 2: Collect Additional Information

### Printer Network Status Sheets
For each network printer, print the Network Status Sheet from the printer's control panel and capture:
- MAC Address
- IP Address (DHCP or Static)
- Firmware Version
- WiFi SSID (if wireless)
- Connection Type (Ethernet/WiFi)

### Device Identification
Document for each discovered device:
- IP Address
- Hostname
- MAC Address
- Manufacturer (from MAC OUI)
- Device Type
- Open Ports/Services

---

## Phase 3: Documentation

### Network Scan Report Structure
Create: `Network_Scan_Report_[Customer]_[Date].md`

```markdown
# Network Scan Report
## [Customer Name]
### Date: [Date]

## Executive Summary
[Overview of locations scanned and key findings]

## Network Overview
### Location #1 - [Name]
| Item | Value |
|------|-------|
| Network Range | x.x.x.x/24 |
| Gateway/Router | x.x.x.x (Make - MAC) |
| Total Hosts | X |

### Location #2 - [Name] (if applicable)
[Same format]

## Discovered Hosts Summary
### Location #1
| IP | Hostname | Device Type | Manufacturer |
[Device table]

### Location #2 (if applicable)
[Same format]

## Device Categories - Location #1
### Network Infrastructure
### Windows Workstations
### Printers
### VoIP/Phone System
### Servers/Special Systems

## Device Categories - Location #2 (if applicable)
[Same structure]

## Open Ports Summary
| Port | Service | Protocol | Hosts |

## Security Observations
### Critical Findings
### Moderate Findings
### Low Findings
### Positive Findings

## Recommendations
### Immediate Actions
### Short-Term Improvements
### Long-Term Recommendations

## Scan Details
[Commands used, duration, files generated]
```

### Network Checklist Update
Update existing: `Network_Checklist_[Customer]_[Date].md`

Add/Update sections:
- Project Overview (device counts, locations)
- Network Scan Results (tables for each location)
- Key Findings (per location)
- Security Observations

---

## Phase 3B: Interactive HTML Documents

### Why HTML Documents?
- **Interactive Features**: Clickable tabs, searchable tables, progress tracking
- **Better Presentation**: Modern UI for customer-facing reports
- **Offline Access**: Works without internet after download
- **Print-Friendly**: Proper styling for printed copies

### HTML Checklist Features
The interactive HTML checklist includes:
- Progress bar tracking completion percentage
- Clickable checkboxes that save state to localStorage
- Tabbed view for multi-location device tables
- Security findings with severity color coding
- Phase-by-phase task organization
- Print and export functionality

### HTML Network Report Features
The interactive HTML network report includes:
- Dark theme professional design
- Statistics dashboard (total devices, findings, ports)
- Location switching tabs
- Device filtering by type (PCs, Printers, Network)
- Search functionality across all devices
- Port badges with severity coloring
- Printer detail expansion panels
- ASCII network diagram
- Recommendations with priority levels
- JSON export functionality

### HTML Template Location
HTML templates are based on the Spanish Fort Waterboard files:
- `/home/mavrick/Projects/Secondbrain/output/Network_Checklist_Spanish_Fort_Water_System.html`
- `/home/mavrick/Projects/Secondbrain/output/Network_Scan_Report_Spanish_Fort_Waterboard.html`

Copy and modify these templates for new customers, updating:
- Customer name in title and headers
- Device tables with scanned data
- Printer details from status sheets
- Security findings specific to customer
- Network diagram

---

## Phase 4: SharePoint Upload

### Upload Script
```python
import os
import requests
from pathlib import Path

# Load credentials
env_path = Path('/home/mavrick/Projects/Secondbrain/.env')
env_vars = {}
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            key, value = line.split('=', 1)
            env_vars[key.strip()] = value.strip().strip('"').strip("'")

tenant_id = env_vars.get('AZURE_TENANT_ID')
client_id = env_vars.get('AZURE_CLIENT_ID')
client_secret = env_vars.get('AZURE_CLIENT_SECRET')

# Get access token
token_url = f'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token'
token_data = {
    'grant_type': 'client_credentials',
    'client_id': client_id,
    'client_secret': client_secret,
    'scope': 'https://graph.microsoft.com/.default'
}
token_response = requests.post(token_url, data=token_data)
access_token = token_response.json()['access_token']
headers = {'Authorization': f'Bearer {access_token}'}
base_url = 'https://graph.microsoft.com/v1.0'

# Find OberaConnect Technical site
resp = requests.get(f"{base_url}/sites?search=*", headers=headers)
sites = resp.json().get('value', [])
site_id = None
for site in sites:
    if site.get('displayName') == 'OberaConnect Technical':
        site_id = site['id']
        break

# Get Documents drive
resp = requests.get(f"{base_url}/sites/{site_id}/drives", headers=headers)
drives = resp.json().get('value', [])
drive_id = None
for drive in drives:
    if drive['name'] == 'Documents':
        drive_id = drive['id']
        break

# Upload file
folder_path = '[Customer Name]/Technical Docs'
filename = '[filename].md'
with open(local_file_path, 'rb') as f:
    content = f.read()

upload_url = f'{base_url}/sites/{site_id}/drives/{drive_id}/root:/{folder_path}/{filename}:/content'
upload_headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/octet-stream'
}
resp = requests.put(upload_url, headers=upload_headers, data=content)
```

### SharePoint Folder Structure
```
OberaConnect Technical (Site)
└── Documents (Drive)
    └── [Customer Name]
        └── Technical Docs
            ├── Network_Scan_Report_[Customer]_[Date].md
            ├── Network_Scan_Report_[Customer].html
            ├── Network_Checklist_[Customer]_[Date].md
            └── Network_Checklist_[Customer].html
```

**Note:** Upload 4 files per customer - 2 Markdown (dated) + 2 HTML (no date, always current)

---

## Multi-Location Process

When customer has multiple physical locations:

1. **Scan each location separately** - Different networks even if same subnet
2. **Identify by router MAC** - Same IP range but different router MACs = different networks
3. **Document in single report** - Use Location #1, Location #2 sections
4. **Update single checklist** - Combine device counts, separate findings by location

### Location Identification
```
Location #1 (Main Office): Router MAC 4C:ED:FB:AD:3D:88
Location #2 (Secondary Site): Router MAC 18:31:BF:5E:A5:70
```

---

## Output Files

### Local Storage
```
/home/mavrick/Projects/Secondbrain/output/
├── Network_Scan_Report_[Customer]_[Date].md
├── Network_Scan_Report_[Customer].html
├── Network_Checklist_[Customer]_[Date].md
└── Network_Checklist_[Customer].html
```

### Scan Data
```
/home/mavrick/Projects/NetworkScannerSuite/service/scans/[customer]_[date]/
├── 01_discovery.nmap
├── 01_discovery.xml
├── 02_standard.nmap
├── 02_standard.xml
├── 03_intensive.nmap (optional)
└── 03_intensive.xml (optional)
```

### Windows Temp (during scan)
```
C:\Temp\[customer]_scan\
├── 01_discovery.*
├── 02_standard.*
└── 03_intensive.*
```

---

## Common Issues & Solutions

### WSL Network Detection
- **Problem:** Detects WSL virtual network (172.x.x.x) instead of WiFi
- **Solution:** Use `powershell.exe -Command "ipconfig /all"` to find correct adapter

### Scan Timeouts on Filtered Hosts
- **Problem:** Intensive scan takes too long on Windows hosts with firewall
- **Solution:** Use `-T5 --host-timeout 60s` flags for faster scanning

### SharePoint Site Not Found
- **Problem:** Direct site path doesn't work
- **Solution:** Use `sites?search=*` to list all sites, find by displayName

### Duplicate Files in SharePoint
- **Problem:** Multiple uploads create duplicates
- **Solution:** List folder contents, delete duplicates by item ID

---

## Checklist Summary

### Per Location
- [ ] Connect to customer network
- [ ] Verify correct network (not WSL)
- [ ] Run discovery scan
- [ ] Run standard port scan
- [ ] Run intensive scan (if needed)
- [ ] Collect printer status sheets
- [ ] Document all devices

### Documentation
- [ ] Create/update Network Scan Report (Markdown) with all locations
- [ ] Create/update Network Scan Report (HTML) - interactive version
- [ ] Update Network Checklist (Markdown) with scan results
- [ ] Update Network Checklist (HTML) - interactive version
- [ ] Save all 4 files to local Secondbrain/output
- [ ] Upload all 4 files to SharePoint Technical Docs folder
- [ ] Verify 4 files in SharePoint folder (2 .md + 2 .html)

---

## Reference: Spanish Fort Waterboard

**Customer:** Spanish Fort Water System (SFWB)
**Locations:** 3 sites total (2 scanned on 2025-12-01)
**SharePoint Folder:** `Spanish Fort Water System/Technical Docs`

### Location #1 - Main Office
- 14 devices discovered
- Router: ASUS (MAC: 4C:ED:FB:AD:3D:88)
- Key devices: 4 Windows PCs, 2 Epson printers, 2 Yealink VoIP, Netgear switch, DMP security panel, Dell server

### Location #2 - Secondary Site
- 4 devices discovered
- Router: ASUS (MAC: 18:31:BF:5E:A5:70)
- Key devices: 1 Epson printer (WiFi), 1 NucBox mini PC, 1 mobile device
