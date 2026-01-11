"""
Ubiquiti UniFi Configuration Generator

Generates JSON-based configurations for UniFi Network Application (Controller).
Supports UniFi Dream Machine, USG, and Cloud Key-based deployments.
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.models import NetworkConfig, VLANConfig, WirelessConfig
from vendors.base import VendorGenerator


class UniFiGenerator(VendorGenerator):
    """
    Configuration generator for Ubiquiti UniFi systems.
    
    Generates JSON configurations for UniFi Controller that can be:
    - Imported via the UniFi Controller UI
    - Applied via UniFi API
    - Used as provisioning templates
    """
    
    vendor_name = "unifi"
    supported_features = [
        "routing",
        "firewall",
        "nat",
        "wireless",
        "vlan",
        "dhcp",
        "port_forwarding",
        "guest_network"
    ]
    
    def __init__(self):
        super().__init__()
    
    def validate_config(self, config: NetworkConfig) -> bool:
        """Validate UniFi-specific configuration requirements"""
        super().validate_config(config)
        
        if config.vendor.value not in ['unifi', 'ubiquiti']:
            raise ValueError("Configuration is not for UniFi vendor")
        
        return True
    
    def generate_config(self, config: NetworkConfig) -> Dict[str, str]:
        """
        Generate UniFi configuration files.
        
        Returns dict of {filename: content}
        """
        self.validate_config(config)
        
        scripts = {}
        
        # Network configuration (JSON)
        network_config = self._generate_network_config(config)
        scripts['unifi_networks.json'] = json.dumps(network_config, indent=2)
        
        # Wireless configuration (JSON)
        if config.wireless:
            wireless_config = self._generate_wireless_config(config)
            scripts['unifi_wireless.json'] = json.dumps(wireless_config, indent=2)
        
        # Firewall rules (JSON)
        firewall_config = self._generate_firewall_config(config)
        scripts['unifi_firewall.json'] = json.dumps(firewall_config, indent=2)
        
        # Port forwarding (if configured)
        if config.port_forwards:
            pf_config = self._generate_port_forward_config(config)
            scripts['unifi_port_forwards.json'] = json.dumps(pf_config, indent=2)
        
        # README with instructions
        scripts['UNIFI_README.md'] = self._generate_readme(config)
        
        return scripts
    
    def _generate_network_config(self, config: NetworkConfig) -> Dict[str, Any]:
        """Generate network configuration JSON"""
        networks = []
        
        # WAN configuration
        if config.wan:
            wan_network = {
                "name": "WAN",
                "purpose": "wan",
                "wan_networkgroup": "WAN",
                "wan_type": config.wan.mode,
                "wan_smartq_enabled": True
            }
            
            if config.wan.mode == "static":
                wan_network.update({
                    "wan_ip": config.wan.ip,
                    "wan_netmask": self._prefix_to_netmask(config.wan.netmask),
                    "wan_gateway": config.wan.gateway
                })
                
                if config.wan.dns:
                    wan_network["wan_dns1"] = config.wan.dns[0]
                    if len(config.wan.dns) > 1:
                        wan_network["wan_dns2"] = config.wan.dns[1]
            
            networks.append(wan_network)
        
        # LAN configuration
        if config.lan:
            lan_network = {
                "name": "LAN",
                "purpose": "corporate",
                "ip_subnet": f"{config.lan.ip}/{config.lan.netmask}",
                "domain_name": f"{config.customer.name.lower().replace(' ', '-')}.local",
                "dhcpd_enabled": config.lan.dhcp.enabled if config.lan.dhcp else False,
                "dhcp_relay_enabled": False,
                "igmp_snooping": True
            }
            
            if config.lan.dhcp and config.lan.dhcp.enabled:
                lan_network.update({
                    "dhcpd_start": config.lan.dhcp.pool_start.split('.')[-1],
                    "dhcpd_stop": config.lan.dhcp.pool_end.split('.')[-1],
                    "dhcpd_leasetime": self._convert_lease_time(config.lan.dhcp.lease_time)
                })
                
                if config.lan.dhcp.dns_servers:
                    lan_network["dhcpd_dns_1"] = config.lan.dhcp.dns_servers[0]
                    if len(config.lan.dhcp.dns_servers) > 1:
                        lan_network["dhcpd_dns_2"] = config.lan.dhcp.dns_servers[1]
            
            networks.append(lan_network)
        
        # VLAN networks
        for vlan in config.vlans:
            vlan_network = {
                "name": vlan.name,
                "purpose": "guest" if vlan.isolation else "corporate",
                "vlan": vlan.id,
                "ip_subnet": vlan.subnet,
                "dhcpd_enabled": vlan.dhcp,
                "igmp_snooping": True
            }
            
            if vlan.dhcp and vlan.dhcp_config:
                vlan_network.update({
                    "dhcpd_start": vlan.dhcp_config.pool_start.split('.')[-1],
                    "dhcpd_stop": vlan.dhcp_config.pool_end.split('.')[-1],
                    "dhcpd_leasetime": self._convert_lease_time(vlan.dhcp_config.lease_time)
                })
                
                if vlan.dhcp_config.dns_servers:
                    vlan_network["dhcpd_dns_1"] = vlan.dhcp_config.dns_servers[0]
            
            # Guest network settings
            if vlan.isolation:
                vlan_network.update({
                    "is_guest": True,
                    "guest_network": True,
                    "networkgroup": "LAN"
                })
            
            networks.append(vlan_network)
        
        return {
            "meta": {
                "generator": "Multi-Vendor Network Config Builder",
                "customer": config.customer.name,
                "site": config.customer.site,
                "version": "1.0"
            },
            "networks": networks
        }
    
    def _generate_wireless_config(self, config: NetworkConfig) -> Dict[str, Any]:
        """Generate wireless network configuration JSON"""
        wlans = []
        
        for idx, wifi in enumerate(config.wireless):
            wlan = {
                "name": wifi.ssid,
                "enabled": True,
                "security": "wpapsk",  # WPA2-Personal
                "wpa_mode": "wpa2",
                "x_passphrase": wifi.password,
                "wpa_enc": "ccmp"
            }
            
            # Band configuration
            if 'band' in wifi.__dict__ and wifi.band:
                if '5ghz' in wifi.band.lower():
                    wlan["wlan_band"] = "5g"
                elif '2ghz' in wifi.band.lower():
                    wlan["wlan_band"] = "2g"
                else:
                    wlan["wlan_band"] = "both"
            else:
                wlan["wlan_band"] = "both"
            
            # VLAN assignment
            if hasattr(wifi, 'vlan') and wifi.vlan:
                wlan["vlan_enabled"] = True
                wlan["vlan"] = wifi.vlan
            
            # Guest mode
            if hasattr(wifi, 'guest_mode') and wifi.guest_mode:
                wlan["is_guest"] = True
                wlan["guest_network"] = True
                wlan["guest_allow_wan_access"] = True
                wlan["guest_allow_lan_access"] = False
            
            # WiFi 6 (802.11ax) support
            if 'mode' in wifi.__dict__ and 'wifi6' in wifi.mode.lower():
                wlan["he_enabled"] = True  # High Efficiency (WiFi 6)
            
            wlans.append(wlan)
        
        return {
            "meta": {
                "generator": "Multi-Vendor Network Config Builder",
                "customer": config.customer.name
            },
            "wlans": wlans
        }
    
    def _generate_firewall_config(self, config: NetworkConfig) -> Dict[str, Any]:
        """Generate firewall rules configuration JSON"""
        firewall_rules = []
        
        # Default LAN to WAN allow
        firewall_rules.append({
            "name": "Allow LAN to WAN",
            "enabled": True,
            "action": "accept",
            "protocol_match_excepted": False,
            "src_networkconf_id": "LAN",
            "dst_networkconf_id": "WAN",
            "logging": False,
            "state_new": True,
            "state_established": True,
            "state_related": True
        })
        
        # Guest network isolation rules
        for vlan in config.vlans:
            if vlan.isolation:
                # Allow guest to WAN
                firewall_rules.append({
                    "name": f"Allow {vlan.name} to WAN",
                    "enabled": True,
                    "action": "accept",
                    "src_networkconf_id": vlan.name,
                    "dst_networkconf_id": "WAN"
                })
                
                # Deny guest to LAN
                firewall_rules.append({
                    "name": f"Deny {vlan.name} to LAN",
                    "enabled": True,
                    "action": "drop",
                    "src_networkconf_id": vlan.name,
                    "dst_networkconf_id": "LAN",
                    "logging": True
                })
        
        return {
            "meta": {
                "generator": "Multi-Vendor Network Config Builder"
            },
            "firewall_rules": firewall_rules
        }
    
    def _generate_port_forward_config(self, config: NetworkConfig) -> Dict[str, Any]:
        """Generate port forwarding rules"""
        port_forwards = []
        
        for pf in config.port_forwards:
            port_forwards.append({
                "name": pf.name,
                "enabled": True,
                "src": "any",
                "dst_port": str(pf.external_port),
                "fwd": pf.internal_ip,
                "fwd_port": str(pf.internal_port),
                "proto": pf.protocol.lower(),
                "log": False
            })
        
        return {
            "meta": {
                "generator": "Multi-Vendor Network Config Builder"
            },
            "port_forwards": port_forwards
        }
    
    def _generate_readme(self, config: NetworkConfig) -> str:
        """Generate README with import instructions"""
        return f"""# UniFi Configuration Import Guide

**Customer:** {config.customer.name}
**Site:** {config.customer.site}
**Generated:** Multi-Vendor Network Config Builder

## Files Generated

- `unifi_networks.json` - Network and VLAN configuration
- `unifi_wireless.json` - Wireless network (WLAN) configuration
- `unifi_firewall.json` - Firewall rules
{f"- `unifi_port_forwards.json` - Port forwarding rules" if config.port_forwards else ""}

## Import Instructions

### Method 1: UniFi Controller Web UI

1. Log into your UniFi Controller (https://your-controller:8443)
2. Go to **Settings** → **Networks**
3. Click **Import** and select `unifi_networks.json`
4. Go to **Settings** → **Wireless Networks**
5. Click **Import** and select `unifi_wireless.json`
6. Go to **Settings** → **Firewall & Security** → **Firewall Rules**
7. Import `unifi_firewall.json`

### Method 2: UniFi API

Use the UniFi API to programmatically apply these configurations:

```bash
# Example using curl
curl -X POST https://your-controller:8443/api/s/default/rest/networkconf \\
  -H "Content-Type: application/json" \\
  -d @unifi_networks.json
```

### Method 3: Manual Configuration

Open each JSON file and manually create the configurations in the UniFi Controller UI.

## Post-Import Steps

1. **Verify Networks**: Check that all networks and VLANs are created correctly
2. **Verify Wireless**: Ensure all SSIDs are broadcasting
3. **Test Firewall Rules**: Verify guest isolation is working
4. **Adopt Devices**: Adopt your UniFi devices (APs, switches, gateways)
5. **Assign Networks**: Assign VLANs to switch ports as needed
6. **Test Connectivity**: Verify client connectivity and internet access

## Important Notes

- Review all settings before applying to production
- These configurations are templates - adjust as needed
- Backup your existing configuration before importing
- Test in a lab environment first if possible

## Support

For issues with this configuration:
- Contact: {config.customer.contact}
- Vendor Support: https://help.ui.com/

---
Generated by Multi-Vendor Network Config Builder
"""
    
    def _prefix_to_netmask(self, prefix: int) -> str:
        """Convert prefix length to dotted decimal netmask"""
        mask = (0xffffffff >> (32 - prefix)) << (32 - prefix)
        return f"{(mask >> 24) & 0xff}.{(mask >> 16) & 0xff}.{(mask >> 8) & 0xff}.{mask & 0xff}"
    
    def _convert_lease_time(self, lease_time: str) -> int:
        """Convert lease time to seconds"""
        if not lease_time:
            return 86400  # 24 hours default
        
        value = int(''.join(filter(str.isdigit, lease_time)))
        unit = ''.join(filter(str.isalpha, lease_time)).lower()
        
        if unit == 'h':
            return value * 3600
        elif unit == 'd':
            return value * 86400
        elif unit == 'm':
            return value * 60
        else:
            return value  # Assume seconds
    
    def deploy_config(self, config: NetworkConfig, device_ip: str, 
                     credentials: Dict[str, str]) -> bool:
        """
        Deploy configuration to UniFi Controller via API.
        
        Not yet implemented - requires UniFi API client.
        """
        raise NotImplementedError(
            "UniFi deployment via API not yet implemented. "
            "Please import generated JSON files via the UniFi Controller web interface."
        )
