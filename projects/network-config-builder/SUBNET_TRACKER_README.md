# Customer Subnet Tracker - Integration Guide

## Existing Tracker Location

✅ **You already have a customer IP tracking system!**

**Primary Tracker:**
```
/home/mavrick/Projects/Secondbrain/input_documents/OberaConnect/Org Development/customer_ip_assignments.xlsx
```

**Alternative Views:**
```
/home/mavrick/Projects/Secondbrain/input_documents/OberaConnect/Org Development/
├── customer_ip_assignments.xlsx          (Main tracker - Excel)
├── CustomerIP_Network_Registry.html      (HTML view)
├── Customer_IP_Scheme.html               (Scheme documentation)
└── CustomerIPNetworksetup.html           (Setup guide)
```

---

## Quick Links

### 📊 Main Tracker (Excel)
```bash
# Open existing tracker
libreoffice /home/mavrick/Projects/Secondbrain/input_documents/OberaConnect/Org\ Development/customer_ip_assignments.xlsx

# Or with Excel (if installed)
excel /home/mavrick/Projects/Secondbrain/input_documents/OberaConnect/Org\ Development/customer_ip_assignments.xlsx
```

### 🌐 HTML View (Browser)
```bash
# Open HTML registry
xdg-open /home/mavrick/Projects/Secondbrain/input_documents/OberaConnect/Org\ Development/CustomerIP_Network_Registry.html
```

---

## Adding DC Lawn to Existing Tracker

### Method 1: Update Excel File

1. **Open the tracker:**
   ```bash
   cd /home/mavrick/Projects/Secondbrain/input_documents/OberaConnect/Org\ Development/
   libreoffice customer_ip_assignments.xlsx
   ```

2. **Add DC Lawn with these details:**
   ```
   Customer ID: 205922
   Customer Name: DC Lawn
   LAN Subnet: 192.168.1.0/24
   LAN Gateway: 192.168.1.1
   DHCP Range: 192.168.1.100-200
   WAN IP: 142.190.216.66/30
   WAN Gateway: 142.190.216.65
   Location: 16520 Gaineswood Dr N, Fairhope, AL 36532-5164
   Circuit ID: 205922
   Circuit Type: Unifi
   Date Assigned: 2025-11-24
   Status: Active
   Notes: Initial deployment, MikroTik router
   ```

3. **Save and close**

### Method 2: Use CSV Version (Quick Add)

I've created a CSV version for easy updates:
```bash
# Edit CSV
nano /home/mavrick/Projects/network-config-builder/CUSTOMER_SUBNET_TRACKER.csv

# Or open in LibreOffice
libreoffice /home/mavrick/Projects/network-config-builder/CUSTOMER_SUBNET_TRACKER.csv
```

---

## Backup Strategy

### Before Making Changes

1. **Backup existing tracker:**
   ```bash
   cp /home/mavrick/Projects/Secondbrain/input_documents/OberaConnect/Org\ Development/customer_ip_assignments.xlsx \
      /home/mavrick/Projects/Secondbrain/input_documents/OberaConnect/Org\ Development/customer_ip_assignments_backup_$(date +%Y%m%d).xlsx
   ```

2. **Make changes**

3. **Verify entries**

---

## Subnet Assignment Workflow

### For New Customers:

1. **Check existing tracker for conflicts**
   - Open customer_ip_assignments.xlsx
   - Review all assigned LAN subnets
   - Choose next available /24 subnet

2. **Assign subnet sequentially**
   ```
   192.168.1.0/24  → DC Lawn (ASSIGNED)
   192.168.2.0/24  → Next customer
   192.168.3.0/24  → Next customer
   etc.
   ```

3. **Update all trackers:**
   - Main Excel: customer_ip_assignments.xlsx
   - CSV backup: CUSTOMER_SUBNET_TRACKER.csv
   - HTML view: CustomerIP_Network_Registry.html (if manually maintained)

4. **Generate customer config**
   ```bash
   cd /home/mavrick/Projects/network-config-builder
   ./network-config generate -i customers/[CUSTOMER]/customer_config.yaml
   ```

---

## Subnet Assignment Rules

### Standard Deployments (192.168.x.0/24)
- **Reserve:** 192.168.0.0/24 for testing/lab
- **Assign:** 192.168.1.0/24 through 192.168.254.0/24 sequentially
- **Capacity:** 254 possible customer subnets

### Large Deployments (Multiple /24s needed)
- Use 10.x.x.x space
- Example: Customer needs 5 subnets → 10.10.0.0/24, 10.10.1.0/24, etc.

### VPN/Interconnects
- Use 172.16.x.x space
- Example: Site-to-site VPN → 172.16.0.0/24

---

## Conflict Prevention Checklist

Before assigning a new subnet:

- [ ] Open customer_ip_assignments.xlsx
- [ ] Check all existing LAN subnet assignments
- [ ] Verify no overlaps with new assignment
- [ ] Confirm next sequential number available
- [ ] Document assignment immediately
- [ ] Update all tracker versions
- [ ] Test configuration in lab if possible

---

## Why Unique Subnets Matter

### Problems with Duplicate Subnets:
1. **VPN Conflicts:** Site-to-site VPNs fail with overlapping subnets
2. **Routing Issues:** Router doesn't know which path to take
3. **Support Complexity:** Remote access becomes impossible
4. **Merger Problems:** Can't connect networks later
5. **Troubleshooting:** Network issues become exponentially harder

### Example Scenario:
```
Customer A: 192.168.1.0/24
Customer B: 192.168.1.0/24  ❌ CONFLICT!

When connecting via VPN:
- Traffic to 192.168.1.10 goes where?
- Customer A or Customer B?
- Router can't decide → FAILURE
```

### Correct Approach:
```
Customer A: 192.168.1.0/24
Customer B: 192.168.2.0/24  ✅ UNIQUE!

VPN works perfectly:
- 192.168.1.x → Customer A
- 192.168.2.x → Customer B
- Clear routing, no conflicts
```

---

## Integration with Network Config Builder

### Workflow:

1. **Check Tracker** → Assign subnet → **Update Tracker**
   ↓
2. **Create customer folder**
   ```bash
   mkdir -p customers/[CUSTOMER_NAME]
   ```
   ↓
3. **Create customer_config.yaml**
   ```yaml
   vendor: mikrotik
   customer:
     name: [Customer Name]
   lan:
     ip: [From Tracker]
     netmask: 24
     dhcp:
       pool_start: [From Tracker]
       pool_end: [From Tracker]
   ```
   ↓
4. **Generate config**
   ```bash
   ./network-config generate -i customers/[CUSTOMER]/customer_config.yaml
   ```
   ↓
5. **Deploy and document**

---

## Quick Reference Commands

### View Current Assignments
```bash
# Excel
libreoffice ~/Projects/Secondbrain/input_documents/OberaConnect/Org\ Development/customer_ip_assignments.xlsx

# HTML
xdg-open ~/Projects/Secondbrain/input_documents/OberaConnect/Org\ Development/CustomerIP_Network_Registry.html

# CSV (this project)
cat CUSTOMER_SUBNET_TRACKER.csv
```

### Add New Customer
```bash
# 1. Open tracker
libreoffice ~/Projects/Secondbrain/input_documents/OberaConnect/Org\ Development/customer_ip_assignments.xlsx

# 2. Find next available subnet (e.g., 192.168.2.0/24)

# 3. Add row with customer info

# 4. Save and close

# 5. Create config
mkdir -p customers/[CUSTOMER]
nano customers/[CUSTOMER]/customer_config.yaml
./network-config generate -i customers/[CUSTOMER]/customer_config.yaml
```

### Backup Tracker
```bash
cp ~/Projects/Secondbrain/input_documents/OberaConnect/Org\ Development/customer_ip_assignments.xlsx \
   ~/Projects/Secondbrain/input_documents/OberaConnect/Org\ Development/customer_ip_assignments_backup_$(date +%Y%m%d).xlsx
```

---

## Files in This Project

For convenience, I've created local copies:

1. **CUSTOMER_SUBNET_TRACKER.csv** - Simple CSV version for quick reference
2. **CUSTOMER_SUBNET_TRACKER.html** - Visual HTML dashboard
3. **This file** - Integration documentation

However, the **primary source of truth** remains:
```
~/Projects/Secondbrain/input_documents/OberaConnect/Org Development/customer_ip_assignments.xlsx
```

---

## Next Steps for DC Lawn

✅ DC Lawn Configuration Complete:
- LAN Subnet: 192.168.1.0/24 assigned
- Config generated: `customers/DC_Lawn/configs/router.rsc`
- Documentation complete

⏳ **ACTION REQUIRED:**
1. Open the main tracker Excel file
2. Add DC Lawn entry with info above
3. Verify no conflicts
4. Save tracker

---

## Support

For questions about subnet assignments or conflicts:
1. Check the existing tracker first
2. Review this documentation
3. Follow the conflict prevention checklist
4. Document all assignments immediately

---

**Last Updated:** 2025-11-24
**System:** Obera Connect Network Config Builder
**Primary Tracker:** ~/Projects/Secondbrain/.../customer_ip_assignments.xlsx
