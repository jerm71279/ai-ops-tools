# Customer Network Configuration Interface

## Overview

The **Network Configuration Interface** (`network-config.py`) is an interactive tool that collects customer network topology information before running scans. This ensures proper documentation, authorization tracking, and scan planning.

---

## Why Use This?

### Before This Tool:
- Manual network mapping
- No standardized documentation
- Risk of missing VLANs or network segments
- No authorization tracking
- Manual exclusion list creation

### With This Tool:
✅ **Structured data collection** - Guided prompts for all network info
✅ **VLAN discovery** - Automatically configure scans for each VLAN
✅ **Authorization tracking** - Document scan approval
✅ **Auto-generated exclusion lists** - Protect critical systems
✅ **Ready-to-run scan plans** - Executable bash scripts created automatically
✅ **Customer documentation** - JSON configs for records

---

## How to Use

### Step 1: Access the Container

After starting the container with `quickstart.sh`:

```bash
docker exec -it kali-network-discovery /bin/bash
```

### Step 2: Run the Configuration Tool

```bash
python3 /usr/local/bin/network-config.py
```

### Step 3: Follow the Interactive Prompts

The tool will guide you through:

1. **Customer Information**
   - Customer name
   - Customer ID/code
   - Primary contact
   - Contact email

2. **Scan Authorization**
   - Confirmation of written authorization
   - Authorization reference/ticket number
   - Warning if no authorization received

3. **Primary Network Configuration**
   - Primary network in CIDR notation (e.g., `192.168.1.0/24`)
   - Additional networks if applicable

4. **VLAN Configuration** (if applicable)
   - VLAN ID (1-4094)
   - VLAN name/description
   - VLAN network range (CIDR)
   - Default gateway (optional)
   - Repeat for each VLAN

5. **Exclusion List**
   - Critical systems to avoid scanning
   - Reason for each exclusion
   - Generates exclude.txt automatically

6. **Scan Configuration**
   - Scan type (Quick/Standard/Intense/Custom)
   - Timing (Polite/Normal/Aggressive)
   - Optional scheduled time

---

## Example Workflow

### Scenario: Customer with Multiple VLANs

**Input:**
```
Customer Name: Acme Corporation
Customer ID: ACME-001
Primary Contact: John Smith
Contact Email: jsmith@acme.com

Authorization: Yes
Reference: Ticket #12345

Primary Network: 10.0.0.0/24

Additional Networks:
  - 10.10.0.0/24
  - 172.16.0.0/16

VLANs:
  VLAN 10: Management (10.0.10.0/24, gateway: 10.0.10.1)
  VLAN 20: Servers (10.0.20.0/24, gateway: 10.0.20.1)
  VLAN 30: Workstations (10.0.30.0/24, gateway: 10.0.30.1)
  VLAN 40: Guest (10.0.40.0/24, gateway: 10.0.40.1)

Exclusions:
  - 10.0.0.1 (Production router)
  - 10.0.20.5 (Database server)
  - 10.0.20.10 (Domain controller)

Scan Type: Intense
Timing: Normal (T3)
```

**Output Files Created:**

```
/scans/configs/
├── acme_corporation_20251110_083015.json        # Full configuration
├── acme_corporation_20251110_083015_exclude.txt # Exclusion list
└── acme_corporation_20251110_083015_scan_plan.sh # Ready-to-run scan script
```

---

## Generated Files

### 1. Configuration JSON

Complete record of all network information:

```json
{
  "customer": {
    "name": "Acme Corporation",
    "id": "ACME-001",
    "contact": {
      "name": "John Smith",
      "email": "jsmith@acme.com"
    },
    "authorization": {
      "received": true,
      "reference": "Ticket #12345",
      "date": "2025-11-10T08:30:15.123456"
    }
  },
  "network": {
    "primary": "10.0.0.0/24",
    "additional": ["10.10.0.0/24", "172.16.0.0/16"],
    "vlans": [
      {
        "id": 10,
        "name": "Management",
        "network": "10.0.10.0/24",
        "gateway": "10.0.10.1"
      }
      // ... more VLANs
    ]
  },
  "exclusions": [
    {
      "target": "10.0.0.1",
      "reason": "Production router"
    }
    // ... more exclusions
  ],
  "scan_config": {
    "type": "intense",
    "timing": "T3"
  }
}
```

### 2. Exclusion File

Auto-generated `exclude.txt`:

```
# Exclusion list for Acme Corporation
# Generated: 2025-11-10T08:30:15.123456

10.0.0.1      # Production router
10.0.20.5     # Database server
10.0.20.10    # Domain controller
```

### 3. Scan Plan Script

Executable bash script with all scans:

```bash
#!/bin/bash
# Scan Plan for Acme Corporation
# Generated: 2025-11-10T08:30:15.123456

echo 'Scanning primary network: 10.0.0.0/24...'
nmap -T3 -A -v --excludefile /scans/configs/acme_corporation_*_exclude.txt 10.0.0.0/24 -oA /scans/acme_corporation_primary_20251110_083015

echo 'Scanning VLAN 10 (Management): 10.0.10.0/24...'
nmap -T3 -A -v --excludefile /scans/configs/acme_corporation_*_exclude.txt 10.0.10.0/24 -oA /scans/acme_corporation_vlan_10_20251110_083015

# ... more scans for each VLAN and additional network

echo 'All scans complete!'
```

---

## Running the Generated Scan Plan

### Option 1: Execute Immediately

```bash
# From inside container
/scans/configs/acme_corporation_20251110_083015_scan_plan.sh
```

### Option 2: Execute from Host

```bash
# From your host machine
docker exec kali-network-discovery /scans/configs/acme_corporation_20251110_083015_scan_plan.sh
```

### Option 3: Schedule for Later

```bash
# Schedule with 'at' command (if available)
echo "/scans/configs/acme_corporation_20251110_083015_scan_plan.sh" | at 2:00 AM

# Or use cron
crontab -e
# Add: 0 2 * * * /scans/configs/acme_corporation_20251110_083015_scan_plan.sh
```

---

## Menu Options

### 1. Create New Customer Configuration
- Interactive guided setup
- Collects all network topology info
- Generates all files automatically

### 2. List Saved Configurations
- Shows all previous customer configs
- Displays key information:
  - Customer name
  - Primary network
  - Number of VLANs
  - Creation date

### 3. Exit
- Closes the configuration tool

---

## VLAN Configuration Tips

### Common VLAN Schemes:

**Small Business:**
```
VLAN 1:  Management (192.168.1.0/24)
VLAN 10: Servers (192.168.10.0/24)
VLAN 20: Workstations (192.168.20.0/24)
VLAN 99: Guest (192.168.99.0/24)
```

**Enterprise:**
```
VLAN 10:  Management (10.0.10.0/24)
VLAN 20:  Infrastructure (10.0.20.0/24)
VLAN 30:  Servers (10.0.30.0/23)
VLAN 40:  Workstations (10.0.40.0/22)
VLAN 50:  VoIP (10.0.50.0/24)
VLAN 60:  Security (10.0.60.0/24)
VLAN 100: Guest/DMZ (10.0.100.0/24)
```

### What to Exclude:

Always exclude from scans:
- **Production routers/firewalls** - Can cause disruptions
- **Domain controllers** - Critical authentication
- **Database servers** - Production data
- **VoIP systems** - Can drop calls
- **Industrial control systems** - Safety critical
- **Backup systems** - May trigger alerts

---

## Scan Type Recommendations

### By Customer Type:

| Customer Type | Recommended Scan | Timing | Notes |
|--------------|------------------|--------|-------|
| **New Infrastructure** | Intense | T4 | No production load |
| **Active Business Hours** | Quick/Standard | T2 | Minimal disruption |
| **After Hours** | Intense | T3/T4 | Thorough analysis |
| **Critical Systems** | Standard | T2 | Cautious approach |
| **Large Networks (>1000 hosts)** | Quick first, then Intense on key hosts | T3 | Staged approach |

---

## Integration with Claude

After generating the scan plan, you can use Claude to:

1. **Review the plan:**
   ```
   "Review the scan plan for Acme Corporation and tell me what will be scanned"
   ```

2. **Execute specific scans:**
   ```
   "Run the intense scan for VLAN 10 on the Acme network"
   ```

3. **Analyze results:**
   ```
   "Show me what services were found on the Acme Corporation server VLAN"
   ```

---

## Best Practices

### Before Scanning:

1. ✅ **Get written authorization** - Always required
2. ✅ **Document the scope** - Use this tool to record everything
3. ✅ **Identify exclusions** - Protect critical systems
4. ✅ **Schedule appropriately** - Avoid peak hours for aggressive scans
5. ✅ **Notify stakeholders** - IT team should know scanning is happening

### During Scanning:

1. ✅ **Monitor progress** - Watch for errors or timeouts
2. ✅ **Check for alerts** - Customer IDS/IPS may trigger
3. ✅ **Be ready to stop** - If issues arise, cancel immediately
4. ✅ **Document issues** - Note any problems for the report

### After Scanning:

1. ✅ **Review results** - Check all VLANs were scanned
2. ✅ **Validate data** - Ensure results make sense
3. ✅ **Secure storage** - Keep configs and results encrypted
4. ✅ **Generate reports** - Use results for infrastructure planning
5. ✅ **Archive properly** - Customer records for compliance

---

## Troubleshooting

### Issue: "Invalid network format"
**Solution:** Use CIDR notation (e.g., `192.168.1.0/24`, not `192.168.1.0`)

### Issue: "VLAN ID must be between 1 and 4094"
**Solution:** Check the VLAN ID - 0 and 4095+ are reserved

### Issue: "Configuration file not found"
**Solution:** Ensure you're in the container and the /scans directory is mounted

### Issue: "Permission denied on scan plan"
**Solution:** The script should be executable by default, but run:
```bash
chmod +x /scans/configs/*_scan_plan.sh
```

---

## File Locations

### Inside Container:
```
/usr/local/bin/network-config.py   # The configuration tool
/scans/configs/                     # Generated configurations
/scans/                             # Scan results
```

### On Host:
```
~/Projects/network-config.py        # Source file
~/Projects/scans/configs/           # Configurations (mounted volume)
~/Projects/scans/                   # Scan results (mounted volume)
```

---

## Security Considerations

### Configuration Files Contain:
- Customer contact information
- Network topology details
- IP addressing schemes
- VLAN structure
- Critical system locations (exclusions)

### Protection Measures:

1. **Encrypt at rest:**
   ```bash
   # Encrypt config directory
   gpg --symmetric /scans/configs/customer_config.json
   ```

2. **Limit access:**
   ```bash
   chmod 600 /scans/configs/*.json
   ```

3. **Secure transmission:**
   - Never email unencrypted configs
   - Use secure file transfer
   - Delete from unsecured systems

4. **Retention policy:**
   - Keep only as long as needed
   - Document destruction
   - Follow compliance requirements

---

## Example: Complete Workflow

```bash
# 1. Start container
./quickstart.sh

# 2. Access container
docker exec -it kali-network-discovery /bin/bash

# 3. Run configuration tool
python3 /usr/local/bin/network-config.py

# 4. Enter customer information
# (Follow interactive prompts)

# 5. Review generated files
ls -lh /scans/configs/

# 6. Execute scan plan
/scans/configs/acme_corporation_20251110_083015_scan_plan.sh

# 7. Review results
ls -lh /scans/acme_corporation_*

# 8. Analyze with Claude (from host)
# Open Claude Desktop and ask:
# "Show me the scan results for Acme Corporation VLAN 10"
```

---

## Advanced Usage

### Export Configuration for Documentation

```bash
# Pretty print JSON
cat /scans/configs/customer_config.json | python3 -m json.tool

# Convert to CSV for IPAM import
python3 << 'EOF'
import json
with open('/scans/configs/customer_config.json') as f:
    config = json.load(f)
    print("VLAN_ID,Name,Network,Gateway")
    for vlan in config['network']['vlans']:
        print(f"{vlan['id']},{vlan['name']},{vlan['network']},{vlan.get('gateway', 'N/A')}")
EOF
```

### Batch Configuration

Create multiple customer configs from a template:

```bash
# Create template
python3 /usr/local/bin/network-config.py
# Save as template

# Duplicate and modify for similar customers
cp /scans/configs/template.json /scans/configs/new_customer.json
# Edit with customer-specific details
```

---

## Support

For issues or questions:
- Check Docker logs: `docker logs kali-network-discovery`
- Verify file permissions in `/scans/configs/`
- Ensure network info is valid CIDR notation
- Review this guide's troubleshooting section

---

**Ready to configure your first customer network?**

```bash
docker exec -it kali-network-discovery python3 /usr/local/bin/network-config.py
```
