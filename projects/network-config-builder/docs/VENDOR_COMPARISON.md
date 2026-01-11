# Vendor Comparison: MikroTik vs SonicWall vs Ubiquiti

## Quick Reference

| Feature | MikroTik | SonicWall | Ubiquiti |
|---------|----------|-----------|----------|
| **Primary Use** | SMB Router/AP | Enterprise Firewall | SMB/Enterprise Networking |
| **Price Point** | $-$$ | $$$-$$$$ | $$-$$$ |
| **Management** | CLI/WinBox/WebFig | Web GUI/CLI | Controller/App/CLI |
| **Configuration** | .rsc scripts | CLI/GUI/Import | JSON API/GUI |
| **API** | REST/SSH | REST/SSH | Controller REST |
| **Complexity** | High learning curve | Medium | Low-Medium |
| **Best For** | Power users, ISPs | Enterprise security | Ease of use, WiFi |

## Detailed Comparison

### Configuration Methods

#### MikroTik RouterOS
```routeros
# CLI-based scripting (.rsc files)
/ip address add address=192.168.1.1/24 interface=bridge-lan
/ip pool add name=dhcp-pool ranges=192.168.1.100-192.168.1.200
/ip dhcp-server add interface=bridge-lan address-pool=dhcp-pool
```

**Pros:**
- Extremely scriptable
- Text-based = version control friendly
- Can be generated programmatically
- Powerful automation

**Cons:**
- Complex syntax
- Many ways to do the same thing
- Easy to make mistakes
- Poor error messages

#### SonicWall SonicOS
```bash
# CLI commands
config
  interface X1
    ip 203.0.113.1 netmask 255.255.255.0
  exit
  route default gateway 203.0.113.254
commit

# Or import .exp file (GUI export)
# Or use JSON via REST API
```

**Pros:**
- Familiar Cisco-like CLI
- GUI for complex features
- Export/import configs
- REST API for automation

**Cons:**
- License-dependent features
- GUI-first design (CLI limited)
- Proprietary formats
- Expensive

#### Ubiquiti UniFi
```json
// Controller API - JSON payloads
{
  "name": "LAN",
  "purpose": "corporate",
  "ip_subnet": "192.168.1.0/24",
  "dhcpd_enabled": true,
  "dhcpd_start": "192.168.1.100",
  "dhcpd_stop": "192.168.1.200"
}
```

**Pros:**
- Clean JSON API
- Controller manages everything
- Modern web UI
- Mobile app

**Cons:**
- Requires controller (software/hardware)
- Less scriptable than MikroTik
- Limited CLI (EdgeRouter better)
- Some features GUI-only

#### Ubiquiti EdgeRouter
```bash
# EdgeOS - VyOS/Vyatta-based
configure
set interfaces ethernet eth0 address 192.168.1.1/24
set service dhcp-server shared-network-name LAN subnet 192.168.1.0/24 start 192.168.1.100 stop 192.168.1.200
commit
save
```

**Pros:**
- VyOS-based (standard Linux)
- Powerful CLI
- Scriptable
- No controller needed

**Cons:**
- Being phased out for UniFi
- Separate ecosystem from UniFi
- Less polish than UniFi

## Feature Matrix

### Routing

| Feature | MikroTik | SonicWall | Ubiquiti UniFi | EdgeRouter |
|---------|----------|-----------|----------------|------------|
| Static Routes | ✅ | ✅ | ✅ | ✅ |
| OSPF | ✅ | ✅ | ❌ | ✅ |
| BGP | ✅ | ✅ | ❌ | ✅ |
| Policy Routing | ✅ | ✅ | Limited | ✅ |
| Multi-WAN | ✅ | ✅ | ✅ | ✅ |
| SD-WAN | Limited | ✅ | ✅ | ❌ |

### Firewall & Security

| Feature | MikroTik | SonicWall | Ubiquiti UniFi | EdgeRouter |
|---------|----------|-----------|----------------|------------|
| Stateful Firewall | ✅ | ✅ | ✅ | ✅ |
| NAT | ✅ | ✅ | ✅ | ✅ |
| DPI | Limited | ✅ | ✅ | ✅ |
| IPS/IDS | ❌ | ✅ | ✅ (UDM) | ❌ |
| Anti-Virus | ❌ | ✅ | ✅ (Gateway) | ❌ |
| Content Filter | Basic | ✅ | ✅ (Gateway) | Basic |
| SSL Inspection | ❌ | ✅ | ❌ | ❌ |
| App Control | ❌ | ✅ | ✅ (UDM) | ❌ |
| GeoIP Blocking | ✅ | ✅ | ✅ | ✅ |

### VPN

| Feature | MikroTik | SonicWall | Ubiquiti UniFi | EdgeRouter |
|---------|----------|-----------|----------------|------------|
| IPsec | ✅ | ✅ | ✅ | ✅ |
| WireGuard | ✅ | ❌ | Limited | ✅ |
| OpenVPN | ✅ | ❌ | ✅ | ✅ |
| L2TP/IPsec | ✅ | ✅ | ✅ | ✅ |
| SSL-VPN | ❌ | ✅ | ❌ | ❌ |
| PPTP | ✅ | ✅ | ✅ | ✅ |
| Site-to-Site | ✅ | ✅ | ✅ | ✅ |
| Client VPN | ✅ | ✅ | ✅ | ✅ |

### Wireless

| Feature | MikroTik | SonicWall | Ubiquiti UniFi | EdgeRouter |
|---------|----------|-----------|----------------|------------|
| Built-in WiFi | Some models | ❌ | UniFi AP only | ❌ |
| WiFi 6 (802.11ax) | ✅ | N/A | ✅ | N/A |
| Controller Managed | CAPsMAN | N/A | ✅ | N/A |
| Mesh | ✅ | N/A | ✅ | N/A |
| Guest Networks | ✅ | N/A | ✅ | N/A |
| Captive Portal | ✅ | N/A | ✅ | N/A |
| RADIUS | ✅ | N/A | ✅ | N/A |

### VLANs & Switching

| Feature | MikroTik | SonicWall | Ubiquiti UniFi | EdgeRouter |
|---------|----------|-----------|----------------|------------|
| VLAN Support | ✅ | ✅ | ✅ | ✅ |
| VLAN Routing | ✅ | ✅ | ✅ | ✅ |
| Bridge VLANs | ✅ | N/A | ✅ | ✅ |
| Port-based VLAN | ✅ | N/A | ✅ | ✅ |
| Switch Chip Offload | ✅ | N/A | ✅ | ❌ |
| PoE | Some models | N/A | ✅ | Some models |

### QoS & Traffic Shaping

| Feature | MikroTik | SonicWall | Ubiquiti UniFi | EdgeRouter |
|---------|----------|-----------|----------------|------------|
| Queue Trees | ✅ | ✅ | ✅ | ✅ |
| Simple Queues | ✅ | ✅ | ✅ | ✅ |
| HTB | ✅ | ❌ | ❌ | ✅ |
| DSCP Marking | ✅ | ✅ | ✅ | ✅ |
| Bandwidth Limits | ✅ | ✅ | ✅ | ✅ |
| Per-IP Limits | ✅ | ✅ | ✅ | ✅ |

## Automation & APIs

### MikroTik
```python
# REST API (RouterOS v7+)
import requests

response = requests.get(
    "https://router.example.com/rest/ip/address",
    auth=("admin", "password"),
    verify=False
)
addresses = response.json()

# Or SSH with librouteros
from librouteros import connect
api = connect(host='router.example.com', username='admin', password='password')
addresses = api('/ip/address/print')
```

**Automation Options:**
- REST API (v7+)
- SSH + CLI
- librouteros (Python)
- Ansible modules
- Terraform provider

### SonicWall
```python
# REST API
import requests

headers = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

# Login
response = requests.post(
    "https://firewall.example.com/api/sonicos/auth",
    json={"username": "admin", "password": "password"},
    headers=headers,
    verify=False
)
token = response.headers["X-Auth-Token"]

# Get config
headers["X-Auth-Token"] = token
config = requests.get(
    "https://firewall.example.com/api/sonicos/config/current",
    headers=headers
)
```

**Automation Options:**
- REST API (SonicOS 7.0+)
- SSH + CLI
- Export/Import .exp files
- Ansible (limited)
- Python SDK (community)

### Ubiquiti UniFi
```python
# Controller API
from pyunifi.controller import Controller

controller = Controller(
    host='controller.example.com',
    username='admin',
    password='password',
    port=8443,
    version='v6',
    site_id='default'
)

# Get clients
clients = controller.get_clients()

# Create network
controller.create_network(
    purpose='corporate',
    name='LAN',
    subnet='192.168.1.0/24',
    dhcp_start='192.168.1.100',
    dhcp_stop='192.168.1.200'
)
```

**Automation Options:**
- Controller REST API
- pyunifi (Python library)
- Ansible modules (excellent)
- Terraform provider
- Mobile app API

### Ubiquiti EdgeRouter
```bash
# SSH + CLI (standard Linux)
ssh admin@router.example.com

# Or API wrapper
curl -k -X POST https://router.example.com/api/edge/batch.json \
  -d 'username=admin&password=password' \
  -d 'data=[{"SET":{"interfaces":{"ethernet":{"eth0":{"address":["192.168.1.1/24"]}}}}}]'
```

**Automation Options:**
- SSH + EdgeOS CLI
- JSON-RPC API (limited)
- Ansible (via SSH)
- Python wrappers (community)

## Configuration Generation Complexity

### MikroTik - Medium Complexity
**Why:** RouterOS syntax is powerful but verbose

```python
# Template variables needed
wan_ip, wan_netmask, wan_gateway
lan_ip, lan_netmask
dhcp_start, dhcp_end, dhcp_lease
dns_servers
admin_allowed_ips
wireless_ssid, wireless_password
firewall_rules

# Template size: ~100-200 lines for basic config
```

### SonicWall - High Complexity
**Why:** Zone-based, many interdependent settings, license features

```python
# Template variables needed
wan_zone, lan_zone
wan_interface, wan_ip, wan_netmask
lan_interface, lan_ip, lan_netmask
address_objects
service_objects
firewall_rules (with zones)
nat_policies
vpn_policies
content_filtering_settings
ips_settings
ssl_inspection_settings

# Template size: ~300-500 lines for basic config
# Many features require specific licenses
```

### Ubiquiti UniFi - Low Complexity
**Why:** Clean JSON structure, controller handles complexity

```python
# Template variables needed (JSON payloads)
site_name
networks = [
    {name, purpose, subnet, dhcp_enabled, dhcp_range},
    ...
]
wireless_networks = [
    {ssid, password, vlan, security},
    ...
]
firewall_rules = [
    {action, protocol, src, dst, port},
    ...
]

# Template size: ~50-100 lines JSON for basic config
```

### EdgeRouter - Medium Complexity
**Why:** VyOS-style, hierarchical but clear

```python
# Template variables needed
interfaces = {
    'eth0': {address, description},
    'eth1': {address, description}
}
dhcp_servers = [
    {name, subnet, range, dns},
    ...
]
firewall_rulesets = [
    {name, rules},
    ...
]

# Template size: ~100-150 lines for basic config
```

## Licensing Considerations

### MikroTik
- **License:** Included with hardware (perpetual)
- **Cost:** One-time hardware purchase ($50-$2000)
- **Features:** All features included, no upsells
- **Support:** Community forum, paid support available

### SonicWall
- **License:** Annual subscriptions required for most features
- **Cost:** Hardware + subscriptions ($500-$50,000+/year)
- **Tiers:**
  - Base (firewall only)
  - TotalSecure (IPS, AV, content filter, app control)
  - Advanced (+ SSL inspection, sandboxing)
  - Elite (+ 24/7 support)
- **Features:** Many locked behind licenses (IPS, AV, filtering, etc.)

### Ubiquiti UniFi
- **License:** No licenses required
- **Cost:** One-time hardware ($100-$3000)
- **Controller:** Free software or Cloud Key
- **Features:** All included
- **Support:** Community forum, UniFi Design Center

### EdgeRouter
- **License:** Included with hardware
- **Cost:** One-time ($50-$500)
- **Features:** All included
- **Note:** Being phased out in favor of UniFi

## Recommendation by Use Case

### Small Office (1-10 users)
**Best:** Ubiquiti UniFi
- Easy to manage
- Good WiFi
- Affordable
- No licensing

**Alternative:** MikroTik (if technical staff available)

### Medium Business (10-100 users)
**Best:** Ubiquiti UniFi or MikroTik
- UniFi: If ease of use priority
- MikroTik: If advanced features/customization needed

**Consider:** SonicWall if security is paramount (IPS/AV required)

### Enterprise (100+ users)
**Best:** SonicWall
- Enterprise security features
- Compliance requirements
- Support contracts

**Alternative:**
- MikroTik for carrier-grade routing
- UniFi for WiFi/switching (with SonicWall firewall)

### ISP / Carrier
**Best:** MikroTik
- Carrier-grade features
- Extremely cost-effective
- Powerful routing (OSPF, BGP)
- CAPsMAN for WiFi management

### Multi-Site with VPN
**Best:**
- SonicWall (enterprise)
- MikroTik (cost-conscious)
- UniFi (if existing UniFi infrastructure)

### Heavy WiFi Focus
**Best:** Ubiquiti UniFi
- Industry-leading WiFi
- Easy controller management
- Mesh support
- Guest networks

## Config Generation Tool Priority

Based on automation-friendliness:

1. **MikroTik** - Best for code generation (text scripts, very automatable)
2. **Ubiquiti UniFi** - Good for API deployment (clean JSON, well-documented API)
3. **EdgeRouter** - Good for code generation (VyOS-like CLI)
4. **SonicWall** - Harder but doable (CLI + API, license complexity)

**Recommendation:** Start with MikroTik (current), add UniFi next (easiest API), then SonicWall (most complex).
