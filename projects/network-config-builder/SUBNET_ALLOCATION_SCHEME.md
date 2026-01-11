# Customer Subnet Allocation Scheme

## Overview

This document describes the subnet allocation strategy for customer network deployments. The system uses a **block allocation model** where each customer receives a reserved block of IP subnets for future expansion, but only the first subnet is initially configured.

---

## Allocation Scheme

### Network Space: `10.54.0.0/16`

- **Base Network:** `10.54.0.0/16`
- **Subnet Size:** `/24` (254 usable hosts per subnet)
- **Block Size:** **4 consecutive /24 subnets per customer**
- **Total Capacity:** 64 customers (256 subnets ÷ 4 subnets per customer)

---

## Block Allocation Pattern

Each customer receives a **block of 4 consecutive /24 subnets** in the registry, but **only the first /24 is configured** on their MikroTik router. This provides room for future expansion without requiring subnet renumbering.

### Allocation Examples:

| Customer | Allocated Block | Configured Subnet | Gateway | DHCP Range |
|----------|----------------|-------------------|---------|------------|
| **Customer 1** | `10.54.0.0/24 - 10.54.3.0/24` | `10.54.0.0/24` | `10.54.0.1` | `10.54.0.100-200` |
| **Customer 2** | `10.54.4.0/24 - 10.54.7.0/24` | `10.54.4.0/24` | `10.54.4.1` | `10.54.4.100-200` |
| **Customer 3** | `10.54.8.0/24 - 10.54.11.0/24` | `10.54.8.0/24` | `10.54.8.1` | `10.54.8.100-200` |
| **Customer 4** | `10.54.12.0/24 - 10.54.15.0/24` | `10.54.12.0/24` | `10.54.12.1` | `10.54.12.100-200` |
| **...**  | ... | ... | ... | ... |
| **Customer 64** | `10.54.252.0/24 - 10.54.255.0/24` | `10.54.252.0/24` | `10.54.252.1` | `10.54.252.100-200` |

---

## Why Block Allocation?

### Benefits:

1. **Future Expansion:** Each customer has 3 additional /24 subnets reserved for:
   - Additional VLANs
   - Guest networks
   - IoT segments
   - VoIP networks
   - Security zones

2. **No Renumbering:** When a customer needs additional subnets, you can use their reserved blocks without changing existing IP addresses

3. **Clean Organization:** Blocks increment predictably (0-3, 4-7, 8-11, etc.)

4. **VPN-Ready:** Site-to-site VPNs work seamlessly because each customer has unique, non-overlapping address space

5. **Scalability:** Clear path for growth from small single-subnet deployments to multi-subnet enterprise configurations

### Example Expansion Scenario:

**Initial Deployment (DC Lawn):**
```
Allocated: 10.54.0.0/24 - 10.54.3.0/24
Configured on MikroTik:
  - LAN: 10.54.0.0/24 (gateway: 10.54.0.1)
```

**6 Months Later - Add Guest WiFi:**
```
Allocated: 10.54.0.0/24 - 10.54.3.0/24 (unchanged)
Configured on MikroTik:
  - LAN: 10.54.0.0/24 (gateway: 10.54.0.1)
  - Guest VLAN: 10.54.1.0/24 (gateway: 10.54.1.1) ✅ Uses reserved block!
```

**1 Year Later - Add VoIP Network:**
```
Allocated: 10.54.0.0/24 - 10.54.3.0/24 (unchanged)
Configured on MikroTik:
  - LAN: 10.54.0.0/24 (gateway: 10.54.0.1)
  - Guest VLAN: 10.54.1.0/24 (gateway: 10.54.1.1)
  - VoIP VLAN: 10.54.2.0/24 (gateway: 10.54.2.1) ✅ Uses reserved block!
```

---

## Subnet Allocation Tool

### Using the Subnet Allocator Script

The `subnet_allocator.py` script automates subnet block management.

#### View Current Allocations:
```bash
python3 subnet_allocator.py summary
```

**Output:**
```
================================================================================
CUSTOMER SUBNET ALLOCATION SUMMARY
================================================================================
Base Network: 10.54.0.0/16
Block Size: 4 x /24 subnets per customer
Total Allocated Blocks: 1

Allocated Ranges:
  • 10.54.0.0/24 - 10.54.3.0/24

Next Available Block: 10.54.4.0/24 - 10.54.7.0/24
  Configured Subnet: 10.54.4.0/24
  Gateway: 10.54.4.1
  DHCP Range: 10.54.4.100-200
================================================================================
```

#### Check Next Available Block:
```bash
python3 subnet_allocator.py next
```

**Output:**
```
Next Available Allocation:
  Block Range: 10.54.4.0/24 - 10.54.7.0/24
  Configured Subnet: 10.54.4.0/24
  Gateway: 10.54.4.1
  DHCP Range: 10.54.4.100-200
```

#### Allocate Block for New Customer:
```bash
python3 subnet_allocator.py allocate \
  --customer-id 206001 \
  --customer-name "Smith Enterprises" \
  --wan-ip "142.190.217.10/30" \
  --wan-gateway "142.190.217.9" \
  --location "123 Main St, Mobile, AL" \
  --circuit-id "206001" \
  --notes "MikroTik RB4011, Unifi circuit"
```

**Output:**
```
✅ Subnet Block Allocated Successfully!

Customer: Smith Enterprises (ID: 206001)
Allocated Block: 10.54.4.0/24 - 10.54.7.0/24
Configured Subnet: 10.54.4.0/24
Gateway: 10.54.4.1
DHCP Range: 10.54.4.100-200

Registry updated: CUSTOMER_SUBNET_TRACKER.csv
```

---

## Workflow for New Customer Deployment

### Step 1: Check Next Available Block
```bash
cd /home/mavrick/Projects/network-config-builder
python3 subnet_allocator.py next
```

### Step 2: Allocate Block
```bash
python3 subnet_allocator.py allocate \
  --customer-id [CUSTOMER_ID] \
  --customer-name "[CUSTOMER NAME]" \
  --wan-ip "[WAN_IP/CIDR]" \
  --wan-gateway "[WAN_GATEWAY]" \
  --location "[LOCATION]" \
  --circuit-id "[CIRCUIT_ID]" \
  --notes "[NOTES]"
```

### Step 3: Create Customer Configuration

Create `customers/[CUSTOMER_NAME]/customer_config.yaml`:

```yaml
vendor: mikrotik
device_model: MikroTik Router

customer:
  name: "[Customer Name]"
  site: "[Location]"
  contact: "[Contact Info]"

deployment_type: router_only

wan:
  interface: ether1
  mode: static
  ip: [WAN IP from allocation]
  netmask: [WAN netmask]
  gateway: [WAN gateway from allocation]
  dns:
    - 142.190.111.111
    - 142.190.222.222

lan:
  interface: bridge-lan
  ip: [Gateway from allocation, e.g., 10.54.4.1]
  netmask: 24
  dhcp:
    enabled: true
    pool_start: [DHCP start from allocation, e.g., 10.54.4.100]
    pool_end: [DHCP end from allocation, e.g., 10.54.4.200]
    lease_time: 24h
    dns_servers:
      - 142.190.111.111
      - 142.190.222.222

security:
  admin_username: admin
  admin_password: "[Secure Password]"
  allowed_management_ips:
    - [Configured subnet from allocation, e.g., 10.54.4.0/24]
    - [WAN subnet]
  disable_unused_services: true

mikrotik:
  enable_winbox: true
  enable_ssh: true
  bandwidth_test: false
  stun_port: false
```

### Step 4: Generate Configuration
```bash
./network-config generate -i customers/[CUSTOMER]/customer_config.yaml -o outputs -v
```

### Step 5: Deploy
```bash
./network-config deploy -i customers/[CUSTOMER]/customer_config.yaml \
  -d [DEVICE_IP] -u admin -v
```

---

## Registry Format

### CSV Structure: `CUSTOMER_SUBNET_TRACKER.csv`

| Column | Description | Example |
|--------|-------------|---------|
| **Customer ID** | Unique customer identifier | `205922` |
| **Customer Name** | Customer/company name | `DC Lawn` |
| **Allocated Subnet Block** | Full block range (4 subnets) | `10.54.0.0/24 - 10.54.3.0/24` |
| **Configured LAN Subnet** | Actually configured subnet | `10.54.0.0/24` |
| **LAN Gateway** | Gateway IP address | `10.54.0.1` |
| **DHCP Range** | DHCP pool range | `10.54.0.100-200` |
| **WAN IP** | WAN IP with CIDR | `142.190.216.66/30` |
| **WAN Gateway** | WAN gateway IP | `142.190.216.65` |
| **Location** | Physical address | `16520 Gaineswood Dr N, Fairhope, AL` |
| **Circuit ID** | Circuit identifier | `205922` |
| **Date Assigned** | Allocation date | `2025-11-24` |
| **Status** | Deployment status | `Active` |
| **Notes** | Additional information | `4x /24 block allocation` |

---

## Quick Reference

### Current Allocation (As of 2025-11-24):

| Customer | Block | Configured Subnet |
|----------|-------|-------------------|
| DC Lawn (205922) | `10.54.0.0/24 - 10.54.3.0/24` | `10.54.0.0/24` |

### Next Available:
- **Block:** `10.54.4.0/24 - 10.54.7.0/24`
- **Configured Subnet:** `10.54.4.0/24`
- **Gateway:** `10.54.4.1`

---

## Troubleshooting

### Issue: "Subnet exhaustion" error

**Cause:** All 256 /24 subnets in the 10.54.0.0/16 space have been allocated (64 customers × 4 subnets).

**Solution:** Expand to additional /16 blocks:
- `10.55.0.0/16` (next 64 customers)
- `10.56.0.0/16` (next 64 customers)
- etc.

### Issue: Registry shows gaps in allocation

**Cause:** Manual edits or deleted customer records.

**Solution:** Review `CUSTOMER_SUBNET_TRACKER.csv` and verify all allocated blocks. The allocator automatically finds the next available block based on the highest ending octet.

### Issue: Need to add VLANs to existing customer

**Solution:** Use the customer's reserved block subnets (the other 3 /24s in their allocated block). Example for DC Lawn:
- Already configured: `10.54.0.0/24`
- Available for VLANs: `10.54.1.0/24`, `10.54.2.0/24`, `10.54.3.0/24`

---

## Migration from Old Scheme

### Old Scheme (192.168.x.0/24):
- Each customer: `192.168.x.0/24` (single subnet)
- No expansion room
- Limited to 254 customers

### New Scheme (10.54.x.0/24):
- Each customer: Block of 4 × `/24` subnets
- Room for expansion within allocated block
- Capacity for 64 customers (expandable to additional /16 blocks)

### DC Lawn Migration Example:

**Before:**
```yaml
lan:
  ip: 192.168.1.1
  netmask: 24
  dhcp:
    pool_start: 192.168.1.100
    pool_end: 192.168.1.200
```

**After:**
```yaml
lan:
  ip: 10.54.0.1
  netmask: 24
  dhcp:
    pool_start: 10.54.0.100
    pool_end: 10.54.0.200
```

---

## Best Practices

1. **Always use the subnet allocator tool** - Don't manually assign subnets to avoid conflicts

2. **Document immediately** - Add customers to the registry as soon as blocks are allocated

3. **Reserve blocks properly** - Never skip blocks or allocate out of order

4. **Plan for growth** - Remember each customer has 4 subnets in their block

5. **Update configs consistently** - Use the wizard or templates to ensure proper formatting

6. **Backup the registry** - Keep versioned backups of `CUSTOMER_SUBNET_TRACKER.csv`

7. **Check before deploying** - Always run `python3 subnet_allocator.py summary` before new deployments

---

## Related Files

- `CUSTOMER_SUBNET_TRACKER.csv` - Main allocation registry
- `subnet_allocator.py` - Subnet allocation automation tool
- `cli/wizard.py` - Interactive configuration wizard (updated defaults)
- `customers/DC_Lawn/customer_config.yaml` - Example customer configuration

---

**Last Updated:** 2025-11-24
**Maintained By:** Obera Connect Network Engineering
**Questions?** Review this document and the subnet allocator tool help: `python3 subnet_allocator.py --help`
