# Complete Workflow Guide

## Two Scenarios Covered:

1. **Unknown Network** - You plug in and don't know the subnet
2. **Known Network** - You have network info and want to configure/scan

---

## Scenario 1: UNKNOWN NETWORK (Auto-Discovery)

### **Use Case:**
- Customer site visit
- Plugged into their network
- Don't know IP ranges yet
- Need to discover the environment first

### **Steps:**

#### 1. Run Auto-Discovery Script
```bash
docker exec -it kali-network-discovery auto-discover-network.sh
```

#### 2. The Script Will:
- ✅ Detect your network interface
- ✅ Find your assigned IP address
- ✅ Calculate the network subnet automatically
- ✅ Show you the network information
- ✅ Ask if you want to scan

#### 3. Example Output:
```
======================================
Network Auto-Discovery
======================================

Step 1: Detecting network interfaces...
Available interfaces:
  ✓ eth0: 192.168.50.45/24

Step 2: Primary interface detected: eth0

Step 3: Your IP assignment:
  Interface: eth0
  IP/CIDR: 192.168.50.45/24

Step 4: Calculated network information:
  Your IP: 192.168.50.45
  Subnet Mask: /24
  Network: 192.168.50.0/24
  Scannable hosts: ~254
  Estimated scan time: 5-15 minutes
  Default Gateway: 192.168.50.1

Do you want to scan this network? (y/n): y

Select scan type:
  1. Quick Discovery (ping sweep only - fastest)
  2. Port Scan (top 1000 ports)
  3. Intense Scan (full OS/service detection)
Select (1-3) [default: 1]: 1

Running quick discovery scan...
[Scan runs...]

======================================
Scan Complete!
======================================

📊 Summary:
  Network scanned: 192.168.50.0/24
  Your IP: 192.168.50.45
  Live hosts found: 32

📁 Results saved to:
  /scans/auto_discovered_20251110_150000/

📋 Next steps:
  1. Review results
  2. Create customer config with this network

To use this network in config tool:
  Primary Network: 192.168.50.0/24
```

#### 4. Review Results
```bash
# View scan results
docker exec kali-network-discovery cat /scans/auto_discovered_20251110_150000/quick_discovery.nmap

# View network info
docker exec kali-network-discovery cat /scans/auto_discovered_20251110_150000/NETWORK_INFO.txt

# On host machine
cat ~/Projects/scans/auto_discovered_20251110_150000/quick_discovery.nmap
```

#### 5. Now Create Customer Config
Now that you know the network (e.g., `192.168.50.0/24`), create a proper customer configuration:

```bash
docker exec -it kali-network-discovery network-config.py
```

Enter:
- Customer name
- The discovered network: `192.168.50.0/24`
- VLANs (if you discovered multiple networks)
- Exclusions (gateway, critical hosts)

---

## Scenario 2: KNOWN NETWORK (Pre-Configured)

### **Use Case:**
- Customer provided network diagram
- You already know IP ranges and VLANs
- Want to configure and save for repeated scans

### **Steps:**

#### 1. Create Customer Configuration
```bash
docker exec -it kali-network-discovery network-config.py
```

Select: **1** (Create new customer configuration)

#### 2. Fill in Customer Details
```
Customer Name: Acme Corporation
Primary Network: 192.168.50.0/24
VLANs:
  - VLAN 10: Management (10.0.10.0/24)
  - VLAN 20: Servers (10.0.20.0/24)
Exclusions:
  - 192.168.50.1 (Core router)
  - 10.0.20.5 (Database server)
Scan Type: Intense
```

#### 3. Save Configuration
Type **y** when prompted

Output:
```
✓ Configuration saved: /scans/configs/acme_corporation_20251110_150000.json
✓ Exclusion file created: /scans/configs/acme_corporation_20251110_150000_exclude.txt
✓ Scan plan created: /scans/configs/acme_corporation_20251110_150000_scan_plan.sh
```

#### 4. Run the Scan Plan
```bash
docker exec kali-network-discovery /scans/configs/acme_corporation_20251110_150000_scan_plan.sh
```

---

## Managing Saved Configurations

### **List All Saved Configs**

#### Method 1: Using Menu
```bash
docker exec -it kali-network-discovery network-config.py
```
Select: **2** (List saved configurations)

#### Method 2: Direct File Listing
```bash
# List config files
docker exec kali-network-discovery ls -lh /scans/configs/*.json

# List scan plans
docker exec kali-network-discovery ls -lh /scans/configs/*_scan_plan.sh
```

### **View a Specific Configuration**
```bash
# Pretty print JSON
docker exec kali-network-discovery python3 -c "
import json
with open('/scans/configs/acme_corporation_20251110_150000.json') as f:
    print(json.dumps(json.load(f), indent=2))
"

# Or simple cat
docker exec kali-network-discovery cat /scans/configs/acme_corporation_20251110_150000.json
```

### **Re-run a Previous Scan**
```bash
# List available scan plans
docker exec kali-network-discovery ls -1 /scans/configs/*_scan_plan.sh

# Run a specific one
docker exec kali-network-discovery /scans/configs/acme_corporation_20251110_150000_scan_plan.sh
```

### **View Exclusion List**
```bash
docker exec kali-network-discovery cat /scans/configs/acme_corporation_20251110_150000_exclude.txt
```

---

## Complete Workflow Examples

### **Example 1: New Customer Site Visit**

```bash
# Step 1: Plug into customer network

# Step 2: Discover the network
docker exec -it kali-network-discovery auto-discover-network.sh
# -> Discovers: 10.50.0.0/16

# Step 3: Review quick scan results
docker exec kali-network-discovery cat /scans/auto_discovered_*/quick_discovery.nmap
# -> Found 127 live hosts

# Step 4: Create customer config with discovered info
docker exec -it kali-network-discovery network-config.py
# Enter customer name: "TechCorp Inc"
# Enter network: 10.50.0.0/16
# Add VLANs if discovered
# Add exclusions for critical hosts

# Step 5: Run comprehensive scan
docker exec kali-network-discovery /scans/configs/techcorp_inc_*_scan_plan.sh

# Step 6: Review results
ls ~/Projects/scans/techcorp_inc_*
```

---

### **Example 2: Return Visit to Known Customer**

```bash
# Step 1: List saved configurations
docker exec -it kali-network-discovery network-config.py
# Select: 2 (List saved configurations)
# Shows: Acme Corporation (saved last week)

# Step 2: Run the saved scan plan
docker exec kali-network-discovery /scans/configs/acme_corporation_20251103_140000_scan_plan.sh

# Step 3: Compare with previous results
diff ~/Projects/scans/acme_corporation_20251103_*/primary.nmap \
     ~/Projects/scans/acme_corporation_20251110_*/primary.nmap
```

---

### **Example 3: Multiple Locations Same Customer**

```bash
# Location 1: HQ
docker exec -it kali-network-discovery network-config.py
Customer: "Acme Corp - HQ"
Network: 10.0.0.0/16

# Location 2: Branch Office
docker exec -it kali-network-discovery network-config.py
Customer: "Acme Corp - Branch 01"
Network: 192.168.100.0/24

# Later: List all Acme configurations
docker exec kali-network-discovery ls -1 /scans/configs/acme_corp_*
```

---

## Troubleshooting Network Discovery

### **Issue: "No network interface with IP found"**

**Solution:**
```bash
# Check if DHCP assigned an IP
docker exec kali-network-discovery ip addr show

# If no IP, try DHCP manually
docker exec kali-network-discovery dhclient eth0

# Then run discovery again
docker exec -it kali-network-discovery auto-discover-network.sh
```

### **Issue: "Can't reach detected network"**

**Cause:** You might be on a restricted VLAN

**Solution:**
```bash
# Check your routing
docker exec kali-network-discovery ip route

# Test gateway connectivity
docker exec kali-network-discovery ping -c 3 <gateway-ip>

# Try scanning just your immediate subnet
docker exec kali-network-discovery nmap -sn <your-ip>/24
```

### **Issue: "Want to scan different network than auto-detected"**

**Solution:**
```bash
# Run manual scan instead
docker exec -it kali-network-discovery /bin/bash

# Inside container, scan specific network
nmap -sn 10.0.0.0/24 -oA /scans/manual_scan_<network>
```

---

## Quick Reference Commands

### **Auto-Discovery (Unknown Network)**
```bash
docker exec -it kali-network-discovery auto-discover-network.sh
```

### **Create Customer Config (Known Network)**
```bash
docker exec -it kali-network-discovery network-config.py
```

### **List Saved Configs**
```bash
docker exec kali-network-discovery ls -lh /scans/configs/*.json
```

### **Run Saved Scan Plan**
```bash
docker exec kali-network-discovery /scans/configs/<customer>_<timestamp>_scan_plan.sh
```

### **View Scan Results (from host)**
```bash
ls -lh ~/Projects/scans/
cat ~/Projects/scans/<customer>_*.nmap
```

### **Container Shell Access**
```bash
docker exec -it kali-network-discovery /bin/bash
```

### **Stop Container**
```bash
docker-compose down
```

### **Restart Container**
```bash
docker-compose up -d
```

---

## File Locations

### **On Host Machine (Windows/WSL):**
```
~/Projects/scans/                           # All scan results
~/Projects/scans/configs/                   # Customer configurations
~/Projects/scans/auto_discovered_*/         # Auto-discovery results
~/Projects/scans/<customer>_*.nmap          # Scan output files
```

### **Inside Container:**
```
/scans/                                     # Scan results (mounted)
/scans/configs/                             # Configurations
/usr/local/bin/auto-discover-network.sh     # Auto-discovery tool
/usr/local/bin/network-config.py            # Config tool
/usr/local/bin/network-discovery.sh         # Discovery scan
/usr/local/bin/intense-scan.sh              # Intense scan
```

---

## Best Practices

### **Before Scanning:**
1. ✅ Get written authorization
2. ✅ Use auto-discovery to understand the network first
3. ✅ Create customer config with proper exclusions
4. ✅ Start with quick discovery, then detailed scans

### **During Scanning:**
1. ✅ Monitor for network issues
2. ✅ Watch for IDS/IPS alerts (customer may notify you)
3. ✅ Be ready to stop if problems occur
4. ✅ Document everything

### **After Scanning:**
1. ✅ Review all results
2. ✅ Secure/encrypt scan files
3. ✅ Save configurations for future visits
4. ✅ Generate reports for customer
5. ✅ Archive or securely delete when done

---

## Summary

**Unknown Network → Use:** `auto-discover-network.sh`
- Automatically finds your subnet
- Quick discovery scan
- Gives you network info to create config

**Known Network → Use:** `network-config.py`
- Pre-configure customer details
- Save for repeated scans
- Generates ready-to-run scan plans

**Saved Configs → Use:** Scan plan scripts
- Re-run previous configurations
- Consistent scanning methodology
- Historical comparison capability

---

**You're now equipped to handle both scenarios!** 🎯
