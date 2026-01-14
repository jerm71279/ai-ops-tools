# UniFi Automation Tools

Reusable Python scripts for bulk UniFi network configuration via API.

**Related SOP:** `SOP-NET-007_UniFi_Bulk_Deployment_v1.0.0.md`

---

## Scripts

| Script | Purpose |
|--------|---------|
| `udm_pro_bulk_config.py` | Bulk VLAN/network creation with dry-run, rollback |
| `enable_network_isolation.py` | Toggle network isolation on filtered networks |
| `delete_units_zone.py` | Delete firewall zones via API |
| `find_zone_api.py` | Discover UniFi API endpoints |

---

## Requirements

```bash
pip install requests urllib3
```

Python 3.8+

---

## Quick Start

```bash
# Preview changes (no modifications)
python3 udm_pro_bulk_config.py --host <UDM-IP> -u <user> -p <pass> --dry-run

# Create networks
python3 udm_pro_bulk_config.py --host <UDM-IP> -u <user> -p <pass>

# Enable isolation on Unit-* networks
python3 enable_network_isolation.py --host <UDM-IP> -u <user> -p <pass>
```

---

## Customization

The `udm_pro_bulk_config.py` script contains a `get_saint_annes_networks()` function with hardcoded network definitions. For new projects:

1. Copy the script
2. Rename/modify the network definition function
3. Update VLAN IDs, subnets, names to match customer requirements

---

## Origin

Created during St Anne's Terrace MDU migration project (December 2025).
