"""
UniFi-Specific Validation Checkers

Implements OberaConnect best practices for UniFi operations:
- WiFi signal minimum: -65dBm
- 2.4GHz channels: 1, 6, 11 only
- VLAN 1 and 4095 reserved
- Open SSIDs blocked
- Permit-any firewall rules blocked
"""

import re
from typing import List

from common.maker_checker import (
    BaseChecker, CheckerResponse, CheckResult,
    ValidationContext, RiskLevel
)


class SSIDChecker(BaseChecker):
    """
    Validates SSID configurations per OberaConnect rules.
    
    Rules:
    - Open SSIDs (no security) are blocked
    - SSID names must be valid
    - Hidden SSIDs flagged for review
    """
    
    name = "ssid_checker"
    description = "Validates SSID configuration for security compliance"
    risk_level = RiskLevel.HIGH
    
    def validate(self, ctx: ValidationContext) -> CheckerResponse:
        issues = []
        suggestions = []
        risk_flags = []
        
        plan = ctx.plan or {}
        
        # Check for open SSID
        security = plan.get('security', '').lower()
        if security in ('none', 'open', ''):
            if not plan.get('allow_open_ssid'):
                issues.append("Open SSID (no security) is blocked per OberaConnect policy")
                suggestions.append("Use WPA2/WPA3 security or set allow_open_ssid=true with justification")
                risk_flags.append("OPEN_SSID")
        
        # Check SSID name
        ssid = plan.get('ssid', '')
        if ssid:
            if len(ssid) > 32:
                issues.append(f"SSID '{ssid}' exceeds 32 character limit")
            
            if ssid != ssid.strip():
                issues.append("SSID has leading/trailing whitespace")
            
            # Check for potentially confusing names
            confusing_patterns = ['test', 'default', 'setup', 'linksys', 'netgear']
            for pattern in confusing_patterns:
                if pattern in ssid.lower():
                    suggestions.append(f"Consider using a more descriptive SSID name (contains '{pattern}')")
                    break
        
        # Check for hidden SSID
        if plan.get('hide_ssid') or plan.get('broadcast_ssid') is False:
            suggestions.append("Hidden SSIDs may cause connectivity issues with some devices")
            risk_flags.append("HIDDEN_SSID")
        
        if issues:
            return CheckerResponse(
                result=CheckResult.REJECTED,
                message=f"SSID validation failed: {len(issues)} issue(s)",
                issues=issues,
                suggestions=suggestions,
                risk_flags=risk_flags
            )
        
        return CheckerResponse(
            result=CheckResult.APPROVED,
            message="SSID configuration validated",
            suggestions=suggestions
        )


class VLANChecker(BaseChecker):
    """
    Validates VLAN configurations per OberaConnect rules.
    
    Rules:
    - VLAN 1 reserved (native)
    - VLAN 4095 reserved (system)
    - VLANs must be tagged properly through path to gateway
    """
    
    name = "vlan_checker"
    description = "Validates VLAN configuration for network integrity"
    risk_level = RiskLevel.HIGH
    
    RESERVED_VLANS = {1, 4095}
    
    def validate(self, ctx: ValidationContext) -> CheckerResponse:
        issues = []
        suggestions = []
        risk_flags = []
        
        plan = ctx.plan or {}
        
        vlan_id = plan.get('vlan_id') or plan.get('vlan')
        
        if vlan_id is not None:
            try:
                vlan = int(vlan_id)
                
                # Check reserved VLANs
                if vlan in self.RESERVED_VLANS:
                    issues.append(f"VLAN {vlan} is reserved and cannot be used")
                    risk_flags.append("RESERVED_VLAN")
                
                # Check valid range
                if vlan < 1 or vlan > 4094:
                    issues.append(f"VLAN {vlan} is outside valid range (1-4094)")
                
            except (ValueError, TypeError):
                issues.append(f"Invalid VLAN ID: {vlan_id}")
        
        # Check for VLAN tagging path
        if plan.get('network_type') == 'vlan' and not plan.get('tagged_ports'):
            suggestions.append("Verify VLAN tagging path to gateway for inter-VLAN routing")
        
        # Inter-VLAN isolation check
        if plan.get('purpose') == 'guest' and not plan.get('isolate'):
            issues.append("Guest networks should have inter-VLAN isolation enabled")
            suggestions.append("Enable 'isolate' option or configure Zone-Based Firewall rules")
        
        if issues:
            return CheckerResponse(
                result=CheckResult.REJECTED,
                message=f"VLAN validation failed: {len(issues)} issue(s)",
                issues=issues,
                suggestions=suggestions,
                risk_flags=risk_flags
            )
        
        return CheckerResponse(
            result=CheckResult.APPROVED,
            message="VLAN configuration validated",
            suggestions=suggestions
        )


class WiFiChannelChecker(BaseChecker):
    """
    Validates WiFi channel configurations per OberaConnect rules.
    
    Rules:
    - 2.4GHz: Only channels 1, 6, 11 (non-overlapping)
    - Signal minimum: -65dBm (warning), -70dBm (critical)
    """
    
    name = "wifi_channel_checker"
    description = "Validates WiFi channel and signal configuration"
    risk_level = RiskLevel.MEDIUM
    
    ALLOWED_24GHZ_CHANNELS = {1, 6, 11}
    SIGNAL_MIN_WARN = -65
    SIGNAL_MIN_CRITICAL = -70
    
    def validate(self, ctx: ValidationContext) -> CheckerResponse:
        issues = []
        suggestions = []
        
        plan = ctx.plan or {}
        
        # Check 2.4GHz channel
        channel_24 = plan.get('channel_2g') or plan.get('channel_24')
        if channel_24 is not None:
            try:
                ch = int(channel_24)
                if ch not in self.ALLOWED_24GHZ_CHANNELS:
                    issues.append(f"2.4GHz channel {ch} is not recommended")
                    suggestions.append(f"Use only channels {self.ALLOWED_24GHZ_CHANNELS} to avoid overlap")
            except (ValueError, TypeError):
                if str(channel_24).lower() != 'auto':
                    issues.append(f"Invalid 2.4GHz channel: {channel_24}")
        
        # Check minimum RSSI setting
        min_rssi = plan.get('min_rssi') or plan.get('minimum_rssi')
        if min_rssi is not None:
            try:
                rssi = int(min_rssi)
                if rssi < self.SIGNAL_MIN_CRITICAL:
                    issues.append(f"Min RSSI {rssi}dBm is below critical threshold ({self.SIGNAL_MIN_CRITICAL}dBm)")
                elif rssi < self.SIGNAL_MIN_WARN:
                    suggestions.append(f"Min RSSI {rssi}dBm is below recommended ({self.SIGNAL_MIN_WARN}dBm)")
            except (ValueError, TypeError):
                pass
        
        # Check roaming settings
        if plan.get('roaming_enabled'):
            # BSS Transition should be used before Minimum RSSI
            if plan.get('min_rssi') and not plan.get('bss_transition'):
                suggestions.append("Enable BSS Transition for smoother roaming before falling back to Min RSSI")
        
        if issues:
            return CheckerResponse(
                result=CheckResult.REJECTED,
                message=f"WiFi channel validation failed: {len(issues)} issue(s)",
                issues=issues,
                suggestions=suggestions
            )
        
        return CheckerResponse(
            result=CheckResult.APPROVED,
            message="WiFi channel configuration validated",
            suggestions=suggestions
        )


class FirewallChecker(BaseChecker):
    """
    Validates firewall rules per OberaConnect rules.
    
    Rules:
    - Permit-any rules are blocked
    - Zone-Based Firewall for inter-VLAN
    - ACLs for intra-VLAN isolation
    """
    
    name = "firewall_checker"
    description = "Validates firewall rules for security compliance"
    risk_level = RiskLevel.CRITICAL
    
    def validate(self, ctx: ValidationContext) -> CheckerResponse:
        issues = []
        suggestions = []
        risk_flags = []
        
        plan = ctx.plan or {}
        
        # Check for permit-any rules
        action = plan.get('action', '').lower()
        source = plan.get('source', '').lower()
        destination = plan.get('destination', '').lower()
        
        if action in ('allow', 'accept', 'permit'):
            if source in ('any', '*', '0.0.0.0/0') and destination in ('any', '*', '0.0.0.0/0'):
                if not plan.get('allow_permit_any'):
                    issues.append("Permit-any firewall rules are blocked per OberaConnect policy")
                    suggestions.append("Define specific source/destination addresses")
                    risk_flags.append("PERMIT_ANY")
        
        # Check for proper zone-based firewall for inter-VLAN
        rule_type = plan.get('type', '').lower()
        if 'inter-vlan' in rule_type or plan.get('inter_vlan'):
            if not plan.get('zone_based'):
                suggestions.append("Use Zone-Based Firewall for inter-VLAN traffic control")
        
        # Check for intra-VLAN isolation
        if 'intra-vlan' in rule_type or plan.get('intra_vlan'):
            suggestions.append("Use ACLs for intra-VLAN device isolation")
        
        # Check for logging
        if not plan.get('logging') and action in ('deny', 'drop', 'reject'):
            suggestions.append("Consider enabling logging for deny rules")
        
        if issues:
            return CheckerResponse(
                result=CheckResult.REJECTED,
                message=f"Firewall validation failed: {len(issues)} issue(s)",
                issues=issues,
                suggestions=suggestions,
                risk_flags=risk_flags
            )
        
        return CheckerResponse(
            result=CheckResult.APPROVED,
            message="Firewall rule validated",
            suggestions=suggestions
        )


class DeviceOperationChecker(BaseChecker):
    """
    Validates device operations for safety.
    
    Rules:
    - Critical device types (gateways) require extra caution
    - Factory resets require explicit confirmation
    - Firmware upgrades require maintenance window
    """
    
    name = "device_operation_checker"
    description = "Validates device operations for safety"
    risk_level = RiskLevel.HIGH
    
    # Critical device types that need extra caution
    CRITICAL_TYPES = {'ugw', 'udm', 'udr', 'uxg'}  # Gateways/routers
    
    def validate(self, ctx: ValidationContext) -> CheckerResponse:
        issues = []
        suggestions = []
        risk_flags = []
        
        plan = ctx.plan or {}
        
        # Check device type
        device_type = plan.get('device_type') or plan.get('type', '').lower()
        
        # Critical device operations
        if device_type in self.CRITICAL_TYPES:
            risk_flags.append("CRITICAL_DEVICE")
            
            action = ctx.action_name.lower()
            if 'restart' in action or 'reboot' in action:
                issues.append(f"Restarting {device_type} device will cause network outage")
                if not plan.get('maintenance_window'):
                    suggestions.append("Schedule during maintenance window")
            
            if 'firmware' in action or 'upgrade' in action:
                issues.append(f"Firmware update on {device_type} is high-risk")
                risk_flags.append("FIRMWARE_CHANGE")
                if not plan.get('rollback_plan'):
                    suggestions.append("Include rollback plan for firmware operations")
        
        # Adoption checks
        if 'adopt' in ctx.action_name.lower():
            if not plan.get('site_id'):
                issues.append("Device adoption requires target site_id")
            
            mac = plan.get('mac')
            if mac and not re.match(r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$', mac):
                issues.append(f"Invalid MAC address format: {mac}")
        
        # Factory reset protection
        if 'factory' in ctx.action_name.lower() or 'reset' in ctx.action_name.lower():
            issues.append("Factory reset requires explicit confirmation")
            risk_flags.append("DESTRUCTIVE_ACTION")
            if not plan.get('confirm_destructive'):
                suggestions.append("Set confirm_destructive=true to proceed")
        
        result = CheckResult.APPROVED
        if issues and risk_flags:
            result = CheckResult.ESCALATE
        elif issues:
            result = CheckResult.NEEDS_REVIEW
        
        return CheckerResponse(
            result=result,
            message=f"Device operation check: {len(issues)} concern(s)" if issues else "Device operation validated",
            issues=issues,
            suggestions=suggestions,
            risk_flags=risk_flags
        )


class GuestNetworkChecker(BaseChecker):
    """
    Validates guest network configurations.
    
    Rules:
    - Guest networks need all three isolation layers:
      1. Network Isolation (inter-VLAN block)
      2. Device Isolation ACL (intra-VLAN)
      3. Client Isolation (per-AP WiFi)
    - Proxy ARP recommended
    """
    
    name = "guest_network_checker"
    description = "Validates guest network security isolation"
    risk_level = RiskLevel.HIGH
    
    def validate(self, ctx: ValidationContext) -> CheckerResponse:
        issues = []
        suggestions = []
        
        plan = ctx.plan or {}
        
        # Check if this is a guest network
        purpose = plan.get('purpose', '').lower()
        name = plan.get('name', '').lower()
        
        is_guest = purpose == 'guest' or 'guest' in name
        
        if not is_guest:
            return CheckerResponse(
                result=CheckResult.APPROVED,
                message="Not a guest network, skipping guest-specific checks"
            )
        
        # Check isolation layers
        isolation_layers = []
        
        # Layer 1: Network Isolation (inter-VLAN)
        if plan.get('network_isolation') or plan.get('inter_vlan_block'):
            isolation_layers.append("Network Isolation")
        else:
            issues.append("Missing Layer 1: Network Isolation (inter-VLAN block)")
        
        # Layer 2: Device Isolation ACL (intra-VLAN)
        if plan.get('device_isolation_acl') or plan.get('intra_vlan_isolation'):
            isolation_layers.append("Device Isolation ACL")
        else:
            issues.append("Missing Layer 2: Device Isolation ACL (intra-VLAN)")
        
        # Layer 3: Client Isolation (per-AP WiFi)
        if plan.get('client_isolation') or plan.get('l2_isolation'):
            isolation_layers.append("Client Isolation")
        else:
            issues.append("Missing Layer 3: Client Isolation (per-AP WiFi)")
        
        # Proxy ARP recommendation
        if not plan.get('proxy_arp'):
            suggestions.append("Enable Proxy ARP for guest networks to prevent ARP-based attacks")
        
        if issues:
            return CheckerResponse(
                result=CheckResult.REJECTED,
                message=f"Guest network missing {len(issues)} isolation layer(s)",
                issues=issues,
                suggestions=suggestions,
                risk_flags=["GUEST_SECURITY"],
                data={"enabled_layers": isolation_layers}
            )
        
        return CheckerResponse(
            result=CheckResult.APPROVED,
            message="Guest network has all required isolation layers",
            data={"enabled_layers": isolation_layers}
        )


# Factory function to get all UniFi checkers
def get_unifi_checkers() -> List[BaseChecker]:
    """Get all UniFi-specific validation checkers."""
    return [
        SSIDChecker(),
        VLANChecker(),
        WiFiChannelChecker(),
        FirewallChecker(),
        DeviceOperationChecker(),
        GuestNetworkChecker()
    ]


__all__ = [
    'SSIDChecker',
    'VLANChecker',
    'WiFiChannelChecker',
    'FirewallChecker',
    'DeviceOperationChecker',
    'GuestNetworkChecker',
    'get_unifi_checkers'
]
