"""
Unit tests for vendor-specific generators.

Tests SonicWall, UniFi, and other vendor generators.
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.models import (
    NetworkConfig, VendorType, DeploymentType, CustomerInfo,
    WANConfig, LANConfig, DHCPConfig, VLANConfig, WirelessConfig,
    SecurityConfig
)
from vendors.mikrotik.generator import MikroTikGenerator
from vendors.sonicwall.generator import SonicWallGenerator
from vendors.ubiquiti.unifi_generator import UniFiGenerator


# ===== Test Fixtures =====

@pytest.fixture
def basic_router_config():
    """Basic router configuration for testing"""
    return NetworkConfig(
        vendor=VendorType.MIKROTIK,
        device_model="hEX S",
        customer=CustomerInfo(
            name="Test Customer",
            site="Test Site",
            contact="test@test.com"
        ),
        deployment_type=DeploymentType.ROUTER_ONLY,
        wan=WANConfig(
            interface="ether1",
            mode="static",
            ip="203.0.113.10",
            netmask=28,
            gateway="203.0.113.1",
            dns=["8.8.8.8", "8.8.4.4"]
        ),
        lan=LANConfig(
            interface="bridge-lan",
            ip="192.168.1.1",
            netmask=24,
            dhcp=DHCPConfig(
                enabled=True,
                pool_start="192.168.1.100",
                pool_end="192.168.1.200",
                lease_time="24h",
                dns_servers=["8.8.8.8"]
            )
        )
    )


@pytest.fixture
def firewall_config():
    """SonicWall firewall configuration for testing"""
    return NetworkConfig(
        vendor=VendorType.SONICWALL,
        device_model="TZ370",
        customer=CustomerInfo(
            name="Firewall Customer",
            site="Corporate Office",
            contact="admin@corp.com"
        ),
        deployment_type=DeploymentType.FIREWALL,
        wan=WANConfig(
            interface="X0",
            mode="static",
            ip="198.51.100.10",
            netmask=28,
            gateway="198.51.100.1",
            dns=["8.8.8.8"]
        ),
        lan=LANConfig(
            interface="X1",
            ip="192.168.10.1",
            netmask=24,
            dhcp=DHCPConfig(
                enabled=True,
                pool_start="192.168.10.100",
                pool_end="192.168.10.200",
                lease_time="24h"
            )
        )
    )


# ===== MikroTik Generator Tests =====

class TestMikroTikGenerator:
    """Test suite for MikroTik generator"""
    
    def test_generator_creation(self):
        """Test MikroTik generator can be created"""
        generator = MikroTikGenerator()
        assert generator.vendor_name == "mikrotik"
        assert "routing" in generator.supported_features
    
    def test_generate_basic_config(self, basic_router_config):
        """Test generation of basic MikroTik configuration"""
        generator = MikroTikGenerator()
        scripts = generator.generate_config(basic_router_config)
        
        assert isinstance(scripts, dict)
        assert "router.rsc" in scripts
        assert len(scripts["router.rsc"]) > 0
        
        # Check for key configuration elements
        config_text = scripts["router.rsc"]
        assert "Test Customer" in config_text
        assert "203.0.113.10" in config_text
        assert "192.168.1.1" in config_text
    
    def test_generate_with_vlans(self, basic_router_config):
        """Test MikroTik generation with VLANs"""
        basic_router_config.vlans = [
            VLANConfig(
                id=10,
                name="Office",
                subnet="192.168.10.0/24",
                dhcp=True,
                dhcp_config=DHCPConfig(
                    enabled=True,
                    pool_start="192.168.10.100",
                    pool_end="192.168.10.200",
                    lease_time="12h"
                )
            )
        ]
        
        generator = MikroTikGenerator()
        scripts = generator.generate_config(basic_router_config)
        
        config_text = scripts["router.rsc"]
        assert "vlan10" in config_text
        assert "192.168.10.0/24" in config_text


# ===== SonicWall Generator Tests =====

class TestSonicWallGenerator:
    """Test suite for SonicWall generator"""
    
    def test_generator_creation(self):
        """Test SonicWall generator can be created"""
        generator = SonicWallGenerator()
        assert generator.vendor_name == "sonicwall"
        assert "firewall" in generator.supported_features
        assert "vpn_ipsec" in generator.supported_features
    
    def test_generate_basic_firewall(self, firewall_config):
        """Test generation of basic SonicWall configuration"""
        generator = SonicWallGenerator()
        scripts = generator.generate_config(firewall_config)
        
        assert isinstance(scripts, dict)
        assert "sonicwall_config.cli" in scripts
        assert len(scripts["sonicwall_config.cli"]) > 0
        
        # Check for key configuration elements
        config_text = scripts["sonicwall_config.cli"]
        assert "Firewall Customer" in config_text
        assert "interface X0" in config_text
        assert "interface X1" in config_text
        assert "198.51.100.10" in config_text
    
    def test_generate_with_vlans(self, firewall_config):
        """Test SonicWall generation with VLANs"""
        firewall_config.vlans = [
            VLANConfig(
                id=10,
                name="Management",
                subnet="10.0.10.0/24",
                dhcp=True,
                dhcp_config=DHCPConfig(
                    enabled=True,
                    pool_start="10.0.10.100",
                    pool_end="10.0.10.200",
                    lease_time="24h"
                )
            )
        ]
        
        generator = SonicWallGenerator()
        scripts = generator.generate_config(firewall_config)
        
        config_text = scripts["sonicwall_config.cli"]
        assert "VLAN 10" in config_text
        assert "interface X1:10" in config_text
        assert "zone MANAGEMENT" in config_text
    
    def test_generate_nat_policies(self, firewall_config):
        """Test NAT policy generation"""
        generator = SonicWallGenerator()
        scripts = generator.generate_config(firewall_config)
        
        config_text = scripts["sonicwall_config.cli"]
        assert "nat-policy" in config_text
        assert "NAT_LAN_to_WAN" in config_text


# ===== UniFi Generator Tests =====

class TestUniFiGenerator:
    """Test suite for UniFi generator"""
    
    def test_generator_creation(self):
        """Test UniFi generator can be created"""
        generator = UniFiGenerator()
        assert generator.vendor_name == "unifi"
        assert "wireless" in generator.supported_features
        assert "vlan" in generator.supported_features
    
    def test_generate_basic_network(self):
        """Test generation of basic UniFi network configuration"""
        config = NetworkConfig(
            vendor=VendorType.UNIFI,
            device_model="UDM Pro",
            customer=CustomerInfo(
                name="UniFi Customer",
                site="Main Office",
                contact="admin@unifi.com"
            ),
            deployment_type=DeploymentType.ROUTER_AND_AP,
            wan=WANConfig(
                interface="eth0",
                mode="dhcp"
            ),
            lan=LANConfig(
                interface="eth1",
                ip="192.168.1.1",
                netmask=24,
                dhcp=DHCPConfig(
                    enabled=True,
                    pool_start="192.168.1.100",
                    pool_end="192.168.1.200",
                    lease_time="24h"
                )
            )
        )
        
        generator = UniFiGenerator()
        scripts = generator.generate_config(config)
        
        assert isinstance(scripts, dict)
        assert "unifi_networks.json" in scripts
        assert "unifi_firewall.json" in scripts
        assert "UNIFI_README.md" in scripts
        
        # Check JSON validity
        import json
        network_config = json.loads(scripts["unifi_networks.json"])
        assert "networks" in network_config
        assert len(network_config["networks"]) >= 2  # WAN + LAN
    
    def test_generate_wireless_config(self):
        """Test wireless configuration generation"""
        config = NetworkConfig(
            vendor=VendorType.UNIFI,
            device_model="UDM",
            customer=CustomerInfo(
                name="WiFi Test",
                site="Test Site",
                contact="test@test.com"
            ),
            deployment_type=DeploymentType.AP_ONLY,
            wireless=[
                WirelessConfig(
                    ssid="TestWiFi",
                    password="TestPassword123",
                    mode="wifi6",
                    band="both",
                    channel_width="40mhz",
                    country="us",
                    guest_mode=False
                )
            ]
        )
        
        generator = UniFiGenerator()
        scripts = generator.generate_config(config)
        
        assert "unifi_wireless.json" in scripts
        
        # Check JSON validity
        import json
        wireless_config = json.loads(scripts["unifi_wireless.json"])
        assert "wlans" in wireless_config
        assert len(wireless_config["wlans"]) == 1
        assert wireless_config["wlans"][0]["name"] == "TestWiFi"


# ===== Integration Tests =====

class TestGeneratorIntegration:
    """Integration tests across multiple generators"""
    
    def test_all_generators_produce_output(self, basic_router_config, firewall_config):
        """Test that all generators can produce output"""
        # MikroTik
        mt_generator = MikroTikGenerator()
        mt_scripts = mt_generator.generate_config(basic_router_config)
        assert len(mt_scripts) > 0
        
        # SonicWall
        sw_generator = SonicWallGenerator()
        sw_scripts = sw_generator.generate_config(firewall_config)
        assert len(sw_scripts) > 0
        
        # UniFi
        unifi_config = basic_router_config
        unifi_config.vendor = VendorType.UNIFI
        unifi_generator = UniFiGenerator()
        unifi_scripts = unifi_generator.generate_config(unifi_config)
        assert len(unifi_scripts) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
