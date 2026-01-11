# Multi-Vendor Network Configuration Builder

A unified automation platform for generating network device configurations across multiple vendors. Transform simple YAML configurations into production-ready device scripts for MikroTik, SonicWall, and Ubiquiti devices.

## Features

- **Multi-Vendor Support**: Single configuration format works across:
  - MikroTik RouterOS (RB series, hEX, CCR) - ✅ Complete
  - SonicWall (TZ/NSa series) - ✅ Complete
  - Ubiquiti UniFi (UDM, USG) - ✅ Complete
  - Ubiquiti EdgeRouter - Coming Soon

- **Comprehensive Network Features**:
  - WAN configuration (static, DHCP, PPPoE)
  - LAN networks with DHCP server
  - VLAN segmentation with isolation
  - Wireless (WiFi 6 and legacy)
  - Port forwarding and NAT
  - VPN (IPsec, WireGuard, L2TP)
  - Firewall rules and security hardening

- **Production-Ready Automation**:
  - Interactive configuration wizard (no YAML knowledge required)
  - Secure SSH deployment to MikroTik devices
  - Automatic backup before deployment
  - Configuration verification and rollback
  - Dry-run mode for safe previewing

- **Developer-Friendly**:
  - Type-safe Python dataclasses
  - Comprehensive validation with clear error messages
  - YAML-based configuration (human-readable, version-controllable)
  - CLI with verbose output and progress indicators
  - Full test coverage with pytest

## Installation

### Prerequisites

- Python 3.12 or higher
- pip and virtualenv

### Setup

```bash
# Clone the repository
cd /path/to/network-config-builder

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Make CLI executable (Unix/Linux/macOS)
chmod +x network-config
```

## Quick Start

### Option 1: Interactive Wizard (Recommended for Beginners)

```bash
# Create configuration interactively (no YAML knowledge needed)
./network-config interactive

# Follow the prompts to configure:
# - Vendor selection (MikroTik/SonicWall/UniFi)
# - Customer information
# - WAN/LAN settings
# - VLANs (optional)
# - Wireless networks (optional)
# - Security settings

# Configuration is saved and optionally generated immediately
```

### Option 2: Using YAML Configuration Files

#### 1. Validate a Configuration

```bash
./network-config validate --input examples/mikrotik/basic_router.yaml --verbose
```

#### 2. Generate Configuration Scripts

```bash
./network-config generate --input examples/mikrotik/router_plus_wifi.yaml --output ./outputs
```

#### 3. Preview Without Saving (Dry-Run)

```bash
./network-config generate --input examples/mikrotik/router_with_vlans.yaml --dry-run
```

#### 4. Deploy to Device (MikroTik)

```bash
# Interactive deployment with automatic backup
./network-config deploy --input config.yaml --device 192.168.1.1

# Preview deployment without applying
./network-config deploy -i config.yaml -d 192.168.1.1 --dry-run

# Deploy with SSH key authentication
./network-config deploy -i config.yaml -d 192.168.1.1 --ssh-key ~/.ssh/id_rsa
```

## Configuration File Format

Configuration files use YAML format. Here's a simple example:

```yaml
vendor: mikrotik
device_model: hEX S

customer:
  name: Acme Corp
  site: Main Office
  contact: admin@acme.com

deployment_type: router_only

wan:
  interface: ether1
  mode: static
  ip: 203.0.113.10
  netmask: 29
  gateway: 203.0.113.9
  dns:
    - 8.8.8.8
    - 8.8.4.4

lan:
  interface: bridge-lan
  ip: 192.168.1.1
  netmask: 24
  dhcp:
    enabled: true
    pool_start: 192.168.1.100
    pool_end: 192.168.1.200
    lease_time: 12h
    dns_servers:
      - 8.8.8.8

security:
  admin_username: admin
  admin_password: StrongPassword123!
  allowed_management_ips:
    - 192.168.1.0/24
  disable_unused_services: true
```

### Complete Examples

Check the `examples/` directory for full configuration samples:

- `examples/mikrotik/basic_router.yaml` - Simple router with DHCP
- `examples/mikrotik/router_with_vlans.yaml` - Router with 3 VLANs (Management, Guest, IoT)
- `examples/mikrotik/router_plus_wifi.yaml` - Router + WiFi with 2 SSIDs

## CLI Commands

### `generate` - Generate Configuration Files

Generate device configuration scripts from YAML input.

```bash
./network-config generate [OPTIONS]

Options:
  -i, --input PATH    Input YAML configuration file (required)
  -o, --output PATH   Output directory (default: ./outputs)
  --dry-run          Preview output without writing files
  -v, --verbose      Show detailed progress
```

**Examples:**

```bash
# Basic generation
./network-config generate --input config.yaml

# Custom output directory with verbose mode
./network-config generate -i config.yaml -o /path/to/output -v

# Preview without saving
./network-config generate -i config.yaml --dry-run
```

### `validate` - Validate Configuration

Validate configuration without generating files.

```bash
./network-config validate [OPTIONS]

Options:
  -i, --input PATH   Input YAML file to validate (required)
  -v, --verbose     Show detailed validation info
```

**Examples:**

```bash
# Basic validation
./network-config validate --input config.yaml

# Verbose validation with summary
./network-config validate -i config.yaml -v
```

### `interactive` - Interactive Configuration Wizard

Step-by-step guided configuration builder. No YAML knowledge required.

```bash
./network-config interactive [OPTIONS]

Options:
  -o, --output PATH   Output directory for generated configs (default: ./outputs)
  -v, --verbose      Show detailed progress
```

**Examples:**

```bash
# Run interactive wizard
./network-config interactive

# Wizard will guide you through:
# 1. Vendor selection (MikroTik/SonicWall/UniFi)
# 2. Customer/site information
# 3. Deployment type (router/AP/firewall)
# 4. WAN configuration (static/DHCP/PPPoE)
# 5. LAN and DHCP settings
# 6. VLANs (optional, with automatic subnet calculation)
# 7. Wireless networks (optional, with guest mode)
# 8. Security configuration
# 9. Review and save

# Saves YAML file and optionally generates device config immediately
```

### `deploy` - Deploy to Device via SSH

Deploy configuration to MikroTik devices with automatic backup and verification.

```bash
./network-config deploy [OPTIONS]

Options:
  -i, --input PATH       Input configuration file (required)
  -d, --device IP        Device IP address (required)
  -u, --username TEXT    Admin username (default: admin)
  -p, --password TEXT    Admin password (prompted if not provided)
  --ssh-key PATH         Path to SSH private key (for key auth)
  --backup-path PATH     Local path to save backups (default: ./backups)
  --no-backup           Skip automatic backup
  --no-verify           Skip deployment verification
  --no-rollback         Do not rollback on failure
  --dry-run             Preview deployment without applying
  -v, --verbose         Verbose output
```

**Examples:**

```bash
# Interactive deployment (prompts for password)
./network-config deploy -i config.yaml -d 192.168.1.1

# Deployment with SSH key (most secure)
./network-config deploy -i config.yaml -d 192.168.1.1 --ssh-key ~/.ssh/id_rsa

# Preview deployment without applying (dry-run)
./network-config deploy -i config.yaml -d 192.168.1.1 --dry-run -v

# Full deployment with custom backup path
./network-config deploy -i config.yaml -d 192.168.1.1 \
  --backup-path /backups/production --verbose
```

**Security Features:**
- SSH encryption for all communication
- Automatic backup before deployment
- Configuration verification after deployment
- Automatic rollback on verification failure
- No credential storage (passwords only in memory)
- Support for SSH key authentication

**Note:** Currently supports MikroTik only. SonicWall and UniFi deployment coming in Phase 4.

## Project Structure

```
network-config-builder/
├── core/                      # Core framework
│   ├── models.py              # Data models (NetworkConfig, VLANConfig, etc.)
│   ├── validators.py          # Validation logic
│   └── exceptions.py          # Custom exceptions
├── vendors/                   # Vendor-specific generators
│   ├── base.py                # Abstract base class
│   ├── mikrotik/
│   │   ├── generator.py       # MikroTik RouterOS generator
│   │   └── deployer.py        # SSH deployment module (450+ lines)
│   ├── sonicwall/
│   │   └── generator.py       # SonicWall CLI generator
│   └── ubiquiti/
│       ├── unifi_generator.py # UniFi JSON generator
│       └── edgerouter_generator.py  # EdgeRouter (placeholder)
├── config_io/                 # Configuration I/O
│   └── readers/
│       ├── yaml_reader.py     # YAML parser
│       └── validation_framework.py
├── cli/                       # Command-line interface
│   ├── commands.py            # Click-based CLI
│   └── wizard.py              # Interactive wizard (350+ lines)
├── tests/                     # Unit tests
│   ├── test_validators.py    # Validator tests (27 tests)
│   └── test_generators.py    # Generator tests (11 tests)
├── examples/                  # Example configurations
│   ├── mikrotik/              # 3 MikroTik examples
│   ├── sonicwall/             # 2 SonicWall examples
│   └── unifi/                 # 2 UniFi examples
├── docs/                      # Documentation
│   └── SECURE_DEPLOYMENT.md   # Security architecture
├── outputs/                   # Generated configurations
├── backups/                   # Automatic device backups
├── network-config             # Main CLI entry point
├── PHASE3_COMPLETE.md         # Phase 3 summary
└── README.md                  # This file
```

## Development

### Running Tests

```bash
# Activate virtual environment
source venv/bin/activate

# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_validators.py -v

# Run with coverage
python -m pytest tests/ --cov=core --cov=vendors
```

### Adding a New Vendor

1. Create vendor directory: `vendors/yourvendor/`
2. Implement generator class extending `VendorGenerator`:

```python
from vendors.base import VendorGenerator

class YourVendorGenerator(VendorGenerator):
    vendor_name = "yourvendor"
    supported_features = ["routing", "firewall", "nat"]

    def generate_config(self, config: NetworkConfig) -> Dict[str, str]:
        # Your implementation
        pass
```

3. Add vendor to `cli/commands.py`
4. Create example configurations in `examples/yourvendor/`
5. Add tests in `tests/test_yourvendor.py`

## Validation

The framework includes comprehensive validation:

### IP Address Validation
- Valid IPv4 format
- CIDR notation for networks
- IP within subnet checks

### Network Configuration Validation
- DHCP pool ranges (start <= end)
- Pool within subnet boundaries
- VLAN ID ranges (1-4094)
- No duplicate VLAN IDs or names

### Security Validation
- Password strength (min 8 characters)
- Management IP restrictions
- Service hardening

### Error Messages

Clear, actionable error messages:

```
❌ Validation failed:
   • Invalid IPv4 address: 256.1.1.1
     Field: WAN IP
     Value: 256.1.1.1
     Suggestion: Use format: 192.168.1.1
```

## Supported Devices

### MikroTik (Current)

| Device Model | RouterOS Version | Status |
|-------------|------------------|--------|
| RB4011iGS+RM | 7.x | ✅ Tested |
| hEX S | 7.x | ✅ Tested |
| CCR series | 7.x | ⚠️ Compatible |
| CRS series | 7.x | ⚠️ Compatible |

**Features Supported:**
- Static/DHCP WAN
- LAN bridging
- DHCP server
- VLANs
- WiFi 6 and legacy wireless
- NAT/Masquerade
- Security hardening

### SonicWall (Coming Soon)

Target models: TZ series, NSa series

**Planned Features:**
- WAN/LAN configuration
- VLANs and zones
- NAT policies
- Firewall rules
- SSL VPN

### Ubiquiti (Coming Soon)

Target platforms:
- UniFi Dream Machine/USG
- EdgeRouter series

**Planned Features:**
- Network configuration
- VLANs
- WiFi networks
- Firewall rules
- Port forwarding

## Roadmap

### Phase 1: Core Framework ✅ (Completed)
- [x] Multi-vendor architecture
- [x] YAML configuration reader
- [x] CLI with Click
- [x] MikroTik generator
- [x] Validation framework
- [x] Unit tests (27 tests passing)

### Phase 2: Additional Vendors ✅ (Completed)
- [x] SonicWall generator (TZ/NSa series)
- [x] Ubiquiti UniFi generator (JSON-based)
- [x] Ubiquiti EdgeRouter generator (placeholder)
- [x] Vendor-specific examples (7 total)
- [x] Generator unit tests (11 tests, 38 total)

### Phase 3: Advanced Features ✅ (Completed November 2025)
- [x] Interactive configuration wizard (cli/wizard.py)
- [x] SSH deployment for MikroTik devices (vendors/mikrotik/deployer.py)
- [x] Automatic backup before deployment
- [x] Configuration verification and rollback
- [x] Dry-run mode for deployment preview
- [x] Security documentation (docs/SECURE_DEPLOYMENT.md)

### Phase 4: Enterprise Features (Planned 2026)
- [ ] SonicWall API deployment
- [ ] UniFi Controller API deployment
- [ ] Batch/multi-device deployment
- [ ] Multi-site management
- [ ] Configuration templates library
- [ ] Audit logging and compliance reporting
- [ ] Role-based access control (RBAC)
- [ ] Web UI dashboard
- [ ] Advanced verification (connectivity tests)

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Write tests for new functionality
4. Ensure all tests pass: `pytest tests/ -v`
5. Submit a pull request

## Testing

Current test coverage:

- **55 unit tests** - All passing ✅ (2.15s execution time)

**Test Breakdown:**
- **Validator tests** (27 tests):
  - IPValidator: 6 tests
  - NetworkValidator: 8 tests
  - ConfigValidator: 11 tests
  - Integration: 2 tests
- **Generator tests** (11 tests):
  - MikroTik: 3 tests
  - SonicWall: 4 tests
  - UniFi: 3 tests
  - Integration: 1 test
- **Phase 3 tests** (17 tests):
  - MikroTik Deployer: 11 tests (connection, backup, deployment, rollback)
  - Deployment function: 3 tests
  - Interactive wizard: 2 tests
  - Integration: 1 test

**Run tests:**
```bash
# All tests
python -m pytest tests/ -v

# Specific test file
python -m pytest tests/test_phase3.py -v

# With coverage
python -m pytest tests/ --cov=core --cov=vendors --cov=cli
```

## License

Copyright © 2025 Obera Connect

## Support

For issues, questions, or contributions:
- Create an issue in the repository
- Contact: admin@acme.com

## Acknowledgments

Built with:
- Python 3.12
- Click (CLI framework)
- PyYAML (YAML parsing)
- Paramiko (SSH deployment)
- pytest (testing)
- ipaddress (IP validation)

Special thanks to the automation-script-builder.skill framework for validation patterns.

---

**Generated with ❤️ for network automation**
