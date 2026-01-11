# Network Migration Toolkit

Migrate network configurations from legacy platforms to UniFi.

## Migration Paths

```
MikroTik  ──┐
            ├──► UniFi Gateway (UDM-Pro, UCG-Max, etc.)
SonicWall ──┘

Cisco IOS ────► UniFi Switches (USW-8, 16, 24, 48)
```

## Workflow

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  /migrate-parse │ ──► │  /migrate-build │ ──► │ /migrate-deploy │
│                 │     │                 │     │                 │
│ Parse device    │     │ Generate UniFi  │     │ Push to UniFi   │
│ config file     │     │ config files    │     │ via API         │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## Quick Start

### 1. Parse Source Config

```bash
cd /home/mavrick/oberaconnect-ai-ops/projects/network-migration

# MikroTik
python3 migrate.py parse mikrotik --input /path/to/export.rsc --output configs/customer.json --customer "Customer Name"

# SonicWall
python3 migrate.py parse sonicwall --input /path/to/config.txt --output configs/customer.json --customer "Customer Name"

# Cisco
python3 migrate.py parse cisco --input /path/to/show-run.txt --output configs/customer.json --customer "Customer Name"
```

### 2. Build UniFi Config

```bash
python3 migrate.py build unifi --config configs/customer.json --output configs/customer_unifi/
```

**Generates:**
- `unifi_networks.json` - Network/VLAN definitions
- `unifi_firewall.json` - Firewall rules
- `MIGRATION_GUIDE.md` - Step-by-step checklist

### 3. Deploy to UniFi (Optional)

```bash
# Always dry-run first!
python3 migrate.py deploy unifi --config configs/customer.json --host 192.168.1.1 --dry-run

# Actual deployment
python3 migrate.py deploy unifi --config configs/customer.json --host 192.168.1.1 --user admin
```

## Supported Devices

### Source (Parse)
| Platform | Config Format |
|----------|--------------|
| MikroTik | RouterOS `/export` |
| SonicWall | CLI config |
| Cisco | IOS `show run` |

### Target (Deploy)
| Device | Model |
|--------|-------|
| UDM-Pro | UniFi Dream Machine Pro |
| UDM-SE | UniFi Dream Machine SE |
| UDM-Pro-Max | UniFi Dream Machine Pro Max |
| UCG-Max | UniFi Cloud Gateway Max |
| UCG-Ultra | UniFi Cloud Gateway Ultra |
| UX | UniFi Express |

## Slash Commands

| Command | Description |
|---------|-------------|
| `/migrate` | Migration toolkit overview |
| `/migrate-parse` | Parse MikroTik, SonicWall, or Cisco config |
| `/migrate-build` | Generate UniFi-compatible configs |
| `/migrate-deploy` | Deploy to UniFi device via API |

## Directory Structure

```
network-migration/
├── migrate.py          # Main CLI
├── parsers/
│   ├── mikrotik_parser.py
│   ├── sonicwall_parser.py
│   └── cisco_parser.py
├── builders/
│   └── unifi_builder.py
├── deployers/
│   └── unifi_deployer.py
├── schemas/
│   └── universal_schema.json
├── configs/            # Parsed & generated configs
│   ├── customer.json
│   └── customer_unifi/
└── requirements.txt
```

## What Gets Migrated

### From MikroTik/SonicWall
- VLANs and network definitions
- IP addresses and DHCP pools
- Firewall rules (filter and NAT)
- Static DHCP leases
- Port forwards

### From Cisco
- VLAN definitions
- Switch port configurations
- Port profiles
- Trunk/access port settings

## Safety Notes

1. **Always dry-run first** before deploying
2. **Backup existing config** on target device
3. **Verify VLAN IDs** don't conflict
4. **Test one network** before deploying all

## Requirements

```bash
pip install -r requirements.txt
```

---

*Part of OberaConnect AI Operations*
