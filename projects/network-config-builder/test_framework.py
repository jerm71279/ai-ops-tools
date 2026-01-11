#!/usr/bin/env python3
"""
Test the core framework - Demonstrates working configuration generation

This script creates a sample network configuration and generates
MikroTik RouterOS scripts to prove the framework works.
"""

from core.models import (
    NetworkConfig, VendorType, DeploymentType,
    CustomerInfo, WANConfig, LANConfig, DHCPConfig,
    VLANConfig, WirelessConfig, SecurityConfig
)
from core.validators import ConfigValidator
from vendors.mikrotik.generator import MikroTikGenerator
from pathlib import Path


def create_sample_config() -> NetworkConfig:
    """Create a sample network configuration"""

    print("📋 Creating sample network configuration...")

    # Customer information
    customer = CustomerInfo(
        name="Acme Corp",
        site="Main Office",
        contact="admin@acme.com"
    )

    # WAN configuration
    wan = WANConfig(
        interface="ether1",
        mode="static",
        ip="203.0.113.10",
        netmask=29,
        gateway="203.0.113.9",
        dns=["8.8.8.8", "8.8.4.4"]
    )

    # LAN configuration with DHCP
    lan = LANConfig(
        interface="bridge-lan",
        ip="192.168.1.1",
        netmask=24,
        dhcp=DHCPConfig(
            enabled=True,
            pool_start="192.168.1.100",
            pool_end="192.168.1.200",
            lease_time="12h",
            dns_servers=["8.8.8.8", "8.8.4.4"]
        )
    )

    # VLANs
    vlans = [
        VLANConfig(
            id=10,
            name="Management",
            subnet="192.168.10.0/24",
            dhcp=True,
            dhcp_config=DHCPConfig(
                pool_start="192.168.10.100",
                pool_end="192.168.10.200",
                lease_time="12h"
            )
        ),
        VLANConfig(
            id=20,
            name="Guest",
            subnet="192.168.20.0/24",
            dhcp=True,
            isolation=True,
            dhcp_config=DHCPConfig(
                pool_start="192.168.20.100",
                pool_end="192.168.20.200",
                lease_time="2h"
            )
        )
    ]

    # Wireless networks
    wireless = [
        WirelessConfig(
            ssid="AcmeWiFi",
            password="SecurePass123",
            mode="wifi6",
            band="2ghz-b/g/n",
            channel_width="20mhz",
            country="us",
            vlan=10
        ),
        WirelessConfig(
            ssid="AcmeGuest",
            password="GuestPass456",
            mode="wifi6",
            band="2ghz-b/g/n",
            channel_width="20mhz",
            country="us",
            vlan=20,
            guest_mode=True
        )
    ]

    # Security configuration
    security = SecurityConfig(
        admin_username="acmeadmin",
        admin_password="SuperSecure123!",
        allowed_management_ips=["192.168.1.0/24", "10.0.0.0/8"],
        disable_unused_services=True
    )

    # MikroTik-specific configuration
    mikrotik_config = {
        "enable_winbox": True,
        "enable_ssh": True,
        "bandwidth_test": True,
        "stun_port": False
    }

    # Create the complete configuration
    config = NetworkConfig(
        vendor=VendorType.MIKROTIK,
        device_model="RB4011iGS+RM",
        customer=customer,
        deployment_type=DeploymentType.ROUTER_AND_AP,
        wan=wan,
        lan=lan,
        vlans=vlans,
        wireless=wireless,
        security=security,
        mikrotik_config=mikrotik_config
    )

    print(f"   ✅ Customer: {customer.name} - {customer.site}")
    print(f"   ✅ Vendor: {config.vendor.value}")
    print(f"   ✅ Device: {config.device_model}")
    print(f"   ✅ Deployment: {config.deployment_type.value}")
    print()

    return config


def validate_configuration(config: NetworkConfig) -> bool:
    """Validate the configuration"""

    print("🔍 Validating configuration...")

    validator = ConfigValidator()
    errors = validator.validate(config)

    if errors:
        print("   ❌ Validation failed:")
        for error in errors:
            print(f"      • {error}")
        return False
    else:
        print("   ✅ Configuration is valid!")
        print()
        return True


def generate_configurations(config: NetworkConfig) -> None:
    """Generate vendor-specific configurations"""

    print(f"🔨 Generating {config.vendor.value} configuration...")

    # Create generator
    generator = MikroTikGenerator()

    # Generate scripts
    scripts = generator.generate_config(config)

    print(f"   ✅ Generated {len(scripts)} configuration files:")
    for filename in scripts.keys():
        print(f"      • {filename}")
    print()

    # Save to output directory
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)

    for filename, content in scripts.items():
        file_path = output_dir / filename
        file_path.write_text(content)
        print(f"💾 Saved: {file_path}")

    print()

    # Display generated router script
    if "router.rsc" in scripts:
        print("=" * 80)
        print("Generated Router Configuration (router.rsc):")
        print("=" * 80)
        print(scripts["router.rsc"])
        print("=" * 80)
        print()

    # Display wireless script if exists
    if "wireless.rsc" in scripts:
        print("=" * 80)
        print("Generated Wireless Configuration (wireless.rsc):")
        print("=" * 80)
        print(scripts["wireless.rsc"])
        print("=" * 80)
        print()


def main():
    """Main test flow"""

    print()
    print("=" * 80)
    print("🌐 Multi-Vendor Network Config Builder - Framework Test")
    print("=" * 80)
    print()

    # Step 1: Create sample configuration
    config = create_sample_config()

    # Step 2: Validate configuration
    if not validate_configuration(config):
        print("❌ Validation failed. Exiting.")
        return 1

    # Step 3: Generate configurations
    generate_configurations(config)

    # Summary
    print("=" * 80)
    print("✅ Framework Test Complete!")
    print("=" * 80)
    print()
    print("📋 What just happened:")
    print("   1. Created a NetworkConfig object with customer data")
    print("   2. Validated IP addresses, DHCP pools, VLANs, and security")
    print("   3. Generated MikroTik RouterOS .rsc scripts")
    print("   4. Saved configurations to outputs/ directory")
    print()
    print("📂 Check the generated files:")
    print("   • outputs/router.rsc - Main router configuration")
    print("   • outputs/wireless.rsc - Wireless AP configuration")
    print()
    print("🎯 Next steps:")
    print("   • Copy these .rsc files to your MikroTik device")
    print("   • Import via WinBox, SSH, or WebFig")
    print("   • Adjust as needed for your specific environment")
    print()
    print("🚀 The core framework is working!")
    print()

    return 0


if __name__ == "__main__":
    exit(main())
