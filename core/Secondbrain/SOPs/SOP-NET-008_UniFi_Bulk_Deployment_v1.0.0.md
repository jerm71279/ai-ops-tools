# SOP: UniFi Bulk Network Deployment via API

**Document ID:** SOP-NET-008
**Version:** 1.0.0
**Created:** 2025-12-30
**Author:** OberaConnect Engineering
**Source Project:** St Anne's Terrace MDU Migration

---

## Purpose

Standardized procedure for bulk VLAN/network configuration on Ubiquiti Dream Machine Pro (UDM-Pro) and similar UniFi devices using API automation.

---

## Scope

- Multi-dwelling unit (MDU) deployments
- Hotel/hospitality networks
- Multi-tenant office buildings
- Any deployment requiring 10+ VLANs

---

## Prerequisites

### Hardware
- UDM-Pro, UDM-SE, or UniFi Cloud Gateway
- Firmware: UniFi OS 3.x+ recommended

### Software
- Python 3.8+
- Required packages: `requests`, `urllib3`

### Access Requirements
- **Local admin account** on UDM device (NOT Ubiquiti cloud SSO)
- Super Admin role
- HTTPS access to device (port 443)

---

## Creating Local Admin Account

1. Access UDM directly: `https://<UDM-IP>`
2. Navigate: Settings → Admins → Create New
3. Select: **Local Access Only**
4. Assign: **Super Admin** role
5. Save credentials securely

**Note:** Cloud/SSO accounts do not work with API scripts.

---

## API Authentication

### Endpoint
```
POST https://<UDM-IP>/api/auth/login
Content-Type: application/json

{"username": "localadmin", "password": "yourpassword"}
```

### CSRF Token
- Required for POST/PUT/DELETE operations
- Extract from login response headers: `X-CSRF-Token`
- Include in subsequent requests: `X-CSRF-Token: <token>`

---

## Key API Endpoints

| Operation | Method | Endpoint |
|-----------|--------|----------|
| Login | POST | `/api/auth/login` |
| Logout | POST | `/api/auth/logout` |
| List Networks | GET | `/proxy/network/api/s/{site}/rest/networkconf` |
| Create Network | POST | `/proxy/network/api/s/{site}/rest/networkconf` |
| Update Network | PUT | `/proxy/network/api/s/{site}/rest/networkconf/{id}` |
| Delete Network | DELETE | `/proxy/network/api/s/{site}/rest/networkconf/{id}` |
| List Zones | GET | `/proxy/network/v2/api/site/{site}/firewall/zone` |
| Delete Zone | DELETE | `/proxy/network/v2/api/site/{site}/firewall/zone/{id}` |

**Default site:** `default`

---

## Network Creation Payload

```json
{
  "name": "Unit-101",
  "purpose": "corporate",
  "ip_subnet": "10.10.2.1/24",
  "dhcp_enabled": true,
  "dhcp_start": "10.10.2.10",
  "dhcp_stop": "10.10.2.200",
  "dhcpd_dns_1": "4.2.2.2",
  "dhcpd_dns_2": "8.8.8.8",
  "vlan_enabled": true,
  "vlan": "101",
  "networkgroup": "LAN",
  "network_isolation": true
}
```

### Important Notes
- `ip_subnet`: Use **gateway IP** format (e.g., `10.10.2.1/24`), NOT network address
- `vlan`: Must be string, not integer
- VLAN 1: Do not create - use existing Default network instead
- `network_isolation`: Set `true` for tenant isolation

---

## Deployment Scripts

**Location:** `/home/mavrick/Projects/Secondbrain/Tools/UniFi-Automation/`

| Script | Purpose | Usage |
|--------|---------|-------|
| `udm_pro_bulk_config.py` | Bulk VLAN creation | `--dry-run`, `--building N`, `--rollback` |
| `enable_network_isolation.py` | Toggle isolation | `--dry-run`, `--disable` |
| `delete_units_zone.py` | Delete firewall zone | `--dry-run`, `--zone-name` |
| `find_zone_api.py` | API endpoint discovery | Diagnostic tool |

---

## Standard Deployment Procedure

### Phase 1: Preparation
1. Gather requirements (VLAN count, IP scheme, special configs)
2. Create/modify deployment script with customer data
3. Create local admin account on UDM device

### Phase 2: Validation
```bash
# Test connectivity and preview changes
python3 udm_pro_bulk_config.py --host <IP> -u <user> -p <pass> --dry-run
```

### Phase 3: Staged Deployment
```bash
# Infrastructure first
python3 udm_pro_bulk_config.py --host <IP> -u <user> -p <pass> --infra-only

# Then building by building (recommended for large deployments)
python3 udm_pro_bulk_config.py --host <IP> -u <user> -p <pass> --building 1
# Monitor, then continue with --building 2, 3, etc.
```

### Phase 4: Isolation Configuration
```bash
# Enable network isolation on tenant VLANs
python3 enable_network_isolation.py --host <IP> -u <user> -p <pass>
```

### Phase 5: Manual Configuration
Items requiring UniFi UI:
- WAN/Internet settings
- Port forwarding rules
- Static DHCP reservations
- Firewall rules (if needed beyond isolation)

### Phase 6: Verification
- Verify all networks created in UniFi UI
- Test sample tenant VLAN connectivity
- Confirm isolation (tenant A cannot ping tenant B)
- Document final configuration

---

## Rollback Procedure

```bash
# Delete all created networks
python3 udm_pro_bulk_config.py --host <IP> -u <user> -p <pass> --rollback
```

**Caution:** Rollback deletes networks matching script patterns. Verify before executing.

---

## Troubleshooting

### Login Failed
- Verify LOCAL admin account (not cloud SSO)
- Check account not locked (Settings → Admins)
- Avoid special characters in password (`'`, `!`, `$`)

### 403 Forbidden on Create/Update
- Missing CSRF token in headers
- Session expired - re-login

### 400 Bad Request
- Check `ip_subnet` format (gateway IP, not network address)
- Verify VLAN ID not already in use
- VLAN 1 cannot be created (reserved)

### Rate Limiting
- Add delay between API calls (0.2-0.5s recommended)
- Process in batches for large deployments

---

## Capacity Considerations

| Device | Recommended Max VLANs |
|--------|----------------------|
| UDM-Pro | ~100 |
| UDM-SE | ~100 |
| Cloud Gateway Ultra | ~50 |

Monitor device memory usage (>80% = risk). Deploy incrementally for large VLAN counts.

---

## Security Notes

- Store credentials securely (not in scripts)
- Delete local admin accounts after deployment (or use View Only for ongoing)
- Scripts disable SSL verification for self-signed certs - acceptable for direct device access
- Audit API access via UDM logs

---

## Appendix: IP Scheme Template (MDU)

**Infrastructure:**
| VLAN | Name | Network | Purpose |
|------|------|---------|---------|
| 1 | MGMT | 192.168.10.0/23 | Management |
| 10 | LAN | 192.168.20.0/23 | Staff/General |
| 22 | CAMERA | 10.11.12.0/24 | Security/IoT |
| 40 | GUEST | 10.1.40.0/24 | Guest WiFi |
| 50 | CORP | 172.16.13.0/24 | Corporate |

**Tenant Units:**
| Pattern | Network | Gateway | DHCP Range |
|---------|---------|---------|------------|
| Unit-XXX | 10.10.X.0/24 | 10.10.X.1 | .10 - .200 |

---

## Document History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-12-30 | Initial release from St Anne's Terrace project |
