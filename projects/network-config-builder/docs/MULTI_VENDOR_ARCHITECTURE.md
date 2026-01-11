# Multi-Vendor Network Device Configuration Platform

## Executive Summary

Instead of building separate tools for MikroTik, SonicWall, and Ubiquiti, we should create a **unified platform** with:
- **Common core framework** - Shared validation, models, I/O, templating
- **Vendor-specific plugins** - Device-specific generators and templates
- **Unified configuration schema** - Single YAML/JSON format for all vendors
- **Automatic device detection** - Detect vendor and apply correct generator

This approach provides:
- ✅ **Single tool to learn and maintain**
- ✅ **Consistent customer experience across vendors**
- ✅ **80% code reuse** (validation, I/O, CLI shared)
- ✅ **Easier to add new vendors** (Cisco, Fortinet, pfSense, etc.)
- ✅ **Multi-vendor deployments** (e.g., MikroTik router + UniFi APs)

## Vendor Comparison

### MikroTik RouterOS
**Use Cases:** SMB routers, wireless APs, switches, carrier-grade equipment
**Configuration:** RouterOS scripts (.rsc files) via CLI/WinBox
**Strengths:** Extremely feature-rich, low cost, highly customizable
**API:** REST API, SSH, WinBox protocol

**Key Features:**
- Routing (static, OSPF, BGP)
- Firewall (stateful, mangle, NAT)
- VPN (IPsec, PPTP, L2TP, WireGuard, OpenVPN, SSTP)
- Wireless (legacy `/interface wireless` + modern `/interface wifi`)
- VLANs, bridges, bonding
- DHCP server/client/relay
- QoS, queues, traffic shaping
- Hotspot, captive portal

### SonicWall
**Use Cases:** Enterprise firewalls, UTM, SD-WAN, VPN concentrators
**Configuration:** Web GUI, CLI, SonicOS API, config import
**Strengths:** Enterprise security features, deep packet inspection, threat prevention
**API:** RESTful API, SSH

**Key Features:**
- Next-gen firewall (NGFW) with DPI
- Intrusion prevention (IPS)
- Anti-virus, anti-malware, content filtering
- Application control
- SSL/TLS decryption and inspection
- VPN (IPsec, SSL-VPN, site-to-site, client-to-site)
- SD-WAN and failover
- High availability (HA)
- Zone-based security
- User/group-based policies

### Ubiquiti (UniFi/EdgeRouter)
**Use Cases:** SMB networking, campus Wi-Fi, managed switches, security cameras
**Configuration:** UniFi Controller (web), EdgeOS CLI, mobile app
**Strengths:** Easy management, beautiful UI, cloud management, affordable
**API:** UniFi Controller API, EdgeOS CLI

**Key Features:**

#### UniFi (Controller-managed)
- Wireless access points (Wi-Fi 6, mesh)
- Switches (PoE, Layer 2/3)
- Security Gateway / Dream Machine
- Network management via controller
- VLANs, guest networks
- Firewall rules
- Port forwarding
- RADIUS integration

#### EdgeRouter (CLI-managed)
- Advanced routing (OSPF, BGP)
- VPN (IPsec, L2TP, OpenVPN, WireGuard)
- VLAN routing
- QoS
- DPI
- CLI similar to Vyatta/VyOS

## Unified Configuration Schema

### Common Fields (All Vendors)
```yaml
# Metadata
vendor: mikrotik  # or sonicwall, unifi, edgerouter
device_model: RB4011iGS+RM
customer:
  name: Acme Corp
  site: Main Office
  contact: admin@acme.com

# WAN Configuration (all vendors support)
wan:
  interface: ether1  # or X1, eth0, etc. (vendor-specific)
  mode: static  # or dhcp, pppoe
  ip: 203.0.113.10
  netmask: 29
  gateway: 203.0.113.9
  dns:
    - 8.8.8.8
    - 8.8.4.4

# LAN Configuration (all vendors support)
lan:
  interface: bridge-lan  # or X0, LAN1, etc.
  ip: 192.168.1.1
  netmask: 24
  dhcp:
    enabled: true
    pool_start: 192.168.1.100
    pool_end: 192.168.1.200
    lease_time: 12h
    dns_servers:
      - 8.8.8.8
      - 8.8.4.4

# VLANs (all vendors support)
vlans:
  - id: 10
    name: Management
    subnet: 192.168.10.0/24
    dhcp: true
  - id: 20
    name: Guest
    subnet: 192.168.20.0/24
    dhcp: true
    isolation: true  # Guest isolation

# Firewall (all vendors support, but syntax varies greatly)
firewall:
  preset: advanced_protection
  port_forwarding:
    - name: Web Server
      protocol: tcp
      external_port: 80
      internal_ip: 192.168.1.50
      internal_port: 80

# VPN (all vendors support, but config varies)
vpn:
  site_to_site:
    - name: Branch Office
      type: ipsec  # or wireguard, openvpn
      peer_ip: 198.51.100.50
      local_subnet: 192.168.1.0/24
      remote_subnet: 192.168.2.0/24
      preshared_key: "{{ vault.ipsec_key }}"

# Security/Admin (all vendors)
security:
  admin_username: admin
  admin_password: "{{ vault.admin_password }}"
  allowed_management_ips:
    - 10.0.0.0/8
    - 192.168.0.0/16

# Vendor-specific extensions
mikrotik:
  wireless:
    mode: wifi6  # or legacy
    ssid: AcmeWiFi
    password: "{{ vault.wifi_password }}"
  bandwidth_test: true

sonicwall:
  content_filtering: true
  intrusion_prevention: true
  ssl_inspection: false
  geoip_blocking:
    - CN
    - RU

unifi:
  controller_url: https://controller.acme.com:8443
  site_name: default
  wifi_networks:
    - ssid: AcmeWiFi
      password: "{{ vault.wifi_password }}"
      vlan: 10
    - ssid: AcmeGuest
      password: "{{ vault.guest_password }}"
      vlan: 20
      guest_mode: true
```

## Project Structure (Multi-Vendor)

```
network-config-builder/
├── core/
│   ├── __init__.py
│   ├── models.py              # Base configuration models
│   ├── validators.py          # Vendor-agnostic validation
│   ├── exceptions.py          # Custom exceptions
│   ├── template_engine.py     # Jinja2 wrapper
│   └── device_detector.py     # Auto-detect vendor/model
│
├── vendors/
│   ├── __init__.py
│   ├── base.py               # Abstract base vendor class
│   │
│   ├── mikrotik/
│   │   ├── __init__.py
│   │   ├── models.py         # MikroTik-specific models
│   │   ├── validators.py     # RouterOS-specific validation
│   │   ├── generator.py      # RouterOS script generator
│   │   ├── api_client.py     # MikroTik API integration
│   │   └── device_capabilities.yaml  # Feature matrix per model
│   │
│   ├── sonicwall/
│   │   ├── __init__.py
│   │   ├── models.py         # SonicWall-specific models
│   │   ├── validators.py     # SonicOS validation
│   │   ├── generator.py      # SonicOS config generator
│   │   ├── api_client.py     # SonicWall API integration
│   │   └── device_capabilities.yaml
│   │
│   └── ubiquiti/
│       ├── __init__.py
│       ├── unifi/
│       │   ├── models.py
│       │   ├── validators.py
│       │   ├── generator.py  # UniFi JSON config generator
│       │   └── api_client.py # UniFi Controller API
│       ├── edgerouter/
│       │   ├── models.py
│       │   ├── validators.py
│       │   ├── generator.py  # EdgeOS commands generator
│       │   └── api_client.py
│       └── device_capabilities.yaml
│
├── templates/
│   ├── mikrotik/
│   │   ├── router/
│   │   │   ├── wan.j2
│   │   │   ├── lan.j2
│   │   │   ├── firewall.j2
│   │   │   └── vpn_ipsec.j2
│   │   └── wireless/
│   │       ├── legacy.j2
│   │       └── wifi6.j2
│   │
│   ├── sonicwall/
│   │   ├── zones.j2
│   │   ├── firewall_rules.j2
│   │   ├── nat.j2
│   │   ├── vpn_ipsec.j2
│   │   └── content_filtering.j2
│   │
│   └── ubiquiti/
│       ├── unifi/
│       │   ├── network_config.j2
│       │   ├── wireless.j2
│       │   └── firewall.j2
│       └── edgerouter/
│           ├── interfaces.j2
│           ├── firewall.j2
│           └── vpn.j2
│
├── io/
│   ├── __init__.py
│   ├── readers/
│   │   ├── csv_reader.py
│   │   ├── yaml_reader.py
│   │   ├── json_reader.py
│   │   └── excel_reader.py
│   └── writers/
│       ├── file_writer.py
│       ├── api_deployer.py
│       └── backup_manager.py
│
├── cli/
│   ├── __init__.py
│   ├── commands.py           # Click CLI commands
│   ├── interactive.py        # Interactive wizard
│   └── device_wizard.py      # Per-vendor wizards
│
├── web/
│   ├── __init__.py
│   ├── app.py               # FastAPI/Flask app
│   ├── api/
│   │   ├── routes.py
│   │   └── schemas.py
│   └── templates/
│       └── index.html
│
├── tests/
│   ├── core/
│   ├── vendors/
│   │   ├── test_mikrotik.py
│   │   ├── test_sonicwall.py
│   │   └── test_ubiquiti.py
│   └── fixtures/
│       ├── mikrotik_configs.yaml
│       ├── sonicwall_configs.yaml
│       └── ubiquiti_configs.yaml
│
├── examples/
│   ├── mikrotik/
│   │   ├── basic_router.yaml
│   │   ├── router_plus_ap.yaml
│   │   └── multi_vlan.yaml
│   ├── sonicwall/
│   │   ├── basic_firewall.yaml
│   │   └── site_to_site_vpn.yaml
│   └── ubiquiti/
│       ├── unifi_campus.yaml
│       └── edgerouter_advanced.yaml
│
├── docs/
│   ├── ARCHITECTURE.md
│   ├── VENDOR_COMPARISON.md
│   ├── API_REFERENCE.md
│   └── vendors/
│       ├── mikrotik_guide.md
│       ├── sonicwall_guide.md
│       └── ubiquiti_guide.md
│
├── legacy/                   # Original single-vendor scripts
│   └── mikrotik/
│       └── config_builder_original.py
│
├── config_builder.py         # Main entry point
├── pyproject.toml           # Modern Python packaging
├── requirements.txt
├── README.md
└── LICENSE
```

## Core Architecture

### Base Vendor Class
```python
# vendors/base.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from core.models import NetworkConfig

class VendorGenerator(ABC):
    """Abstract base class for vendor-specific generators"""

    vendor_name: str
    supported_features: List[str]

    @abstractmethod
    def validate_config(self, config: NetworkConfig) -> List[str]:
        """Validate configuration for this vendor"""
        pass

    @abstractmethod
    def generate_config(self, config: NetworkConfig) -> Dict[str, str]:
        """Generate vendor-specific configuration files"""
        pass

    @abstractmethod
    def deploy_config(self, config: NetworkConfig, device_ip: str, credentials: Dict) -> bool:
        """Deploy configuration to device via API"""
        pass

    def get_capabilities(self, model: str) -> Dict[str, Any]:
        """Get device capabilities from YAML database"""
        pass
```

### MikroTik Implementation
```python
# vendors/mikrotik/generator.py
from vendors.base import VendorGenerator
from core.models import NetworkConfig

class MikroTikGenerator(VendorGenerator):
    vendor_name = "mikrotik"
    supported_features = [
        "routing", "firewall", "nat", "vpn_ipsec", "vpn_wireguard",
        "wireless_legacy", "wireless_wifi6", "vlan", "dhcp", "qos"
    ]

    def validate_config(self, config: NetworkConfig) -> List[str]:
        errors = []
        # MikroTik-specific validation
        if config.wireless and config.wireless.mode == "wifi6":
            if not self._supports_wifi6(config.device_model):
                errors.append(f"Model {config.device_model} doesn't support Wi-Fi 6")
        return errors

    def generate_config(self, config: NetworkConfig) -> Dict[str, str]:
        # Use Jinja2 templates from templates/mikrotik/
        templates = self.load_templates()
        scripts = {}

        # Generate router script
        if config.deployment_type in ["router_only", "router_and_ap"]:
            scripts["router.rsc"] = self.render_template(
                "mikrotik/router/main.j2",
                config=config
            )

        # Generate wireless script
        if config.wireless:
            if config.wireless.mode == "wifi6":
                scripts["wireless.rsc"] = self.render_template(
                    "mikrotik/wireless/wifi6.j2",
                    config=config
                )
            else:
                scripts["wireless.rsc"] = self.render_template(
                    "mikrotik/wireless/legacy.j2",
                    config=config
                )

        return scripts
```

### SonicWall Implementation
```python
# vendors/sonicwall/generator.py
from vendors.base import VendorGenerator

class SonicWallGenerator(VendorGenerator):
    vendor_name = "sonicwall"
    supported_features = [
        "firewall", "nat", "vpn_ipsec", "vpn_ssl", "ips", "av",
        "content_filtering", "app_control", "ssl_inspection", "sdwan"
    ]

    def validate_config(self, config: NetworkConfig) -> List[str]:
        errors = []
        # SonicWall-specific validation
        if config.sonicwall:
            if config.sonicwall.ssl_inspection and not config.has_license("ssl_dpi"):
                errors.append("SSL inspection requires DPI-SSL license")
        return errors

    def generate_config(self, config: NetworkConfig) -> Dict[str, str]:
        # SonicWall uses different export formats:
        # - .exp (settings export)
        # - CLI commands
        # - JSON via API

        scripts = {}

        # Generate CLI commands
        scripts["sonicwall_config.cli"] = self.render_template(
            "sonicwall/main.j2",
            config=config
        )

        # Generate JSON for API deployment
        scripts["sonicwall_config.json"] = self.generate_api_config(config)

        return scripts
```

### Ubiquiti UniFi Implementation
```python
# vendors/ubiquiti/unifi/generator.py
from vendors.base import VendorGenerator

class UniFiGenerator(VendorGenerator):
    vendor_name = "unifi"
    supported_features = [
        "wireless", "switching", "routing", "firewall",
        "port_forwarding", "vlan", "guest_network"
    ]

    def generate_config(self, config: NetworkConfig) -> Dict[str, str]:
        # UniFi uses JSON config via controller API
        scripts = {}

        # Generate site config JSON
        scripts["site_config.json"] = self.generate_site_config(config)

        # Generate network definitions
        scripts["networks.json"] = self.generate_networks(config)

        # Generate firewall rules
        scripts["firewall.json"] = self.generate_firewall(config)

        # Generate wireless networks
        if config.wireless:
            scripts["wireless.json"] = self.generate_wireless(config)

        return scripts

    def deploy_config(self, config: NetworkConfig, controller_url: str, credentials: Dict) -> bool:
        # Use UniFi Controller API
        from .api_client import UniFiController

        controller = UniFiController(controller_url, credentials)
        controller.login()

        # Create networks
        for network in config.networks:
            controller.create_network(network)

        # Create wireless networks
        for wlan in config.wireless_networks:
            controller.create_wlan(wlan)

        # Apply firewall rules
        for rule in config.firewall_rules:
            controller.create_firewall_rule(rule)

        return True
```

## CLI Usage Examples

### Generate MikroTik Config
```bash
# From YAML
network-config generate \
  --input customers/acme/config.yaml \
  --vendor mikrotik \
  --output ./configs/acme/

# Auto-detect vendor from YAML
network-config generate --input config.yaml

# Dry-run
network-config generate --input config.yaml --dry-run

# Validation only
network-config validate --input config.yaml
```

### Generate SonicWall Config
```bash
network-config generate \
  --input customers/acme/config.yaml \
  --vendor sonicwall \
  --format cli \
  --output ./configs/acme/
```

### Generate UniFi Config
```bash
# Generate JSON for controller
network-config generate \
  --input customers/acme/config.yaml \
  --vendor unifi \
  --output ./configs/acme/

# Deploy directly to controller
network-config deploy \
  --input customers/acme/config.yaml \
  --vendor unifi \
  --controller https://controller.acme.com:8443 \
  --username admin \
  --password-file ~/.unifi_pass
```

### Multi-Vendor Deployment
```yaml
# config.yaml - Deploy MikroTik router + UniFi APs
devices:
  - vendor: mikrotik
    model: RB4011iGS+RM
    role: router
    wan: { ... }
    lan: { ... }

  - vendor: unifi
    model: U6-LR
    role: ap
    controller: https://controller.acme.com:8443
    wireless:
      - ssid: AcmeWiFi
        password: "{{ vault.wifi_pass }}"
```

```bash
# Generate all device configs
network-config generate --input config.yaml --output ./configs/
# Creates:
#   ./configs/router.rsc (MikroTik)
#   ./configs/unifi_ap.json (UniFi)
```

## Implementation Phases

### Phase 0: Project Restructure (1 week)
- [ ] Rename project: `Mikrotik/` → `network-config-builder/`
- [ ] Move original script to `legacy/mikrotik/`
- [ ] Create new multi-vendor directory structure
- [ ] Update documentation

### Phase 1: Core Framework (2-3 weeks)
- [ ] Base vendor class and plugin system
- [ ] Common configuration models (dataclasses)
- [ ] Unified YAML/JSON schema
- [ ] Jinja2 template engine integration
- [ ] Vendor auto-detection
- [ ] CLI framework (Click)

### Phase 2: MikroTik Plugin (2 weeks)
- [ ] Port existing logic to new architecture
- [ ] Create Jinja2 templates for RouterOS
- [ ] Device capability database
- [ ] MikroTik API client
- [ ] Tests and examples

### Phase 3: SonicWall Plugin (2-3 weeks)
- [ ] SonicWall models and validators
- [ ] CLI command templates
- [ ] JSON API config generator
- [ ] SonicOS API client
- [ ] Tests and examples

### Phase 4: Ubiquiti Plugin (2-3 weeks)
- [ ] UniFi models and validators
- [ ] Controller API integration
- [ ] EdgeRouter support
- [ ] Tests and examples

### Phase 5: Advanced Features (ongoing)
- [ ] Web interface
- [ ] REST API
- [ ] Multi-device deployments
- [ ] Configuration versioning
- [ ] Backup/rollback
- [ ] Monitoring integration

## Advantages of Multi-Vendor Approach

### Code Reuse
- **80% shared code:** Validation, I/O, CLI, web interface
- **20% vendor-specific:** Generators and templates
- **Estimated effort savings:** 60-70% vs building 3 separate tools

### Consistency
- **Same commands** for all vendors
- **Same YAML schema** (with vendor extensions)
- **Same validation rules** where applicable
- **Same deployment workflow**

### Extensibility
- Add new vendors easily (Cisco, Fortinet, pfSense, OpnSense, VyOS)
- Add new features once, benefit all vendors
- Community contributions easier

### Real-World Scenarios
Many deployments use **multiple vendors:**
- MikroTik router + UniFi APs
- SonicWall firewall + Ubiquiti switches
- EdgeRouter + MikroTik wireless

A unified tool handles these naturally.

## Comparison: Single vs Multi-Vendor

| Aspect | 3 Separate Tools | Unified Platform |
|--------|------------------|------------------|
| **Development time** | 15-20 weeks | 8-12 weeks |
| **Code to maintain** | ~3000 lines | ~1500 lines |
| **Learning curve** | 3x commands/formats | 1x unified interface |
| **Adding features** | 3x effort | 1x effort + vendor adapters |
| **Multi-vendor setups** | Manual coordination | Native support |
| **Testing effort** | 3x test suites | Shared + vendor-specific |

## Recommendation

**Build the unified platform** because:

1. ✅ **You already use all 3 vendors** - this matches your real-world needs
2. ✅ **60-70% less total effort** - shared core vs 3 separate tools
3. ✅ **Future-proof** - easy to add Cisco, Fortinet, etc. later
4. ✅ **Better UX** - customers learn one tool, not three
5. ✅ **Multi-vendor deployments** - handles mixed environments naturally

## Next Steps

1. **Rename project:** `/home/mavrick/Projects/Mikrotik` → `/home/mavrick/Projects/network-config-builder`
2. **Create multi-vendor structure** as outlined above
3. **Start with Phase 1:** Core framework with MikroTik as first vendor
4. **Add SonicWall second:** Validate plugin architecture works
5. **Add Ubiquiti third:** Prove scalability

**Total timeline:** 8-12 weeks for all three vendors vs 15-20 weeks for separate tools.

**Should we proceed with the multi-vendor architecture?**
