#!/usr/bin/env python3
"""
Wireless Network Assessment Script
Scans for wireless networks, analyzes signal strength, channel overlap, and security
"""

import subprocess
import json
import argparse
from datetime import datetime
from typing import Dict, List
import re

class WirelessAssessment:
    def __init__(self, output_dir: str = "/tmp/network-scan"):
        self.output_dir = output_dir
        self.results = {
            "scan_time": datetime.now().isoformat(),
            "networks": [],
            "channels": {},
            "issues": []
        }
    
    def scan_wireless_networks(self, interface: str = "wlan0") -> List[Dict]:
        """Scan for wireless networks"""
        print(f"[*] Scanning for wireless networks on {interface}...")
        
        try:
            # Use iwlist to scan
            result = subprocess.run(
                ["iwlist", interface, "scan"],
                capture_output=True, text=True, timeout=30
            )
            
            if result.returncode != 0:
                print(f"[!] Scan failed. Is {interface} a wireless interface?")
                return []
            
            networks = self._parse_iwlist_output(result.stdout)
            return networks
            
        except Exception as e:
            print(f"[!] Wireless scan failed: {e}")
            return []
    
    def _parse_iwlist_output(self, output: str) -> List[Dict]:
        """Parse iwlist scan output"""
        networks = []
        current_network = {}
        
        for line in output.split('\n'):
            line = line.strip()
            
            if 'Cell' in line and 'Address' in line:
                # New network found
                if current_network:
                    networks.append(current_network)
                
                # Extract BSSID
                bssid = line.split('Address:')[-1].strip()
                current_network = {"bssid": bssid}
            
            elif 'ESSID:' in line:
                essid = line.split('ESSID:')[-1].strip().strip('"')
                current_network["essid"] = essid
            
            elif 'Channel:' in line:
                channel = line.split('Channel:')[-1].strip()
                try:
                    current_network["channel"] = int(channel)
                except:
                    current_network["channel"] = channel
            
            elif 'Frequency:' in line:
                freq = line.split('Frequency:')[-1].split('GHz')[0].strip()
                current_network["frequency"] = freq
            
            elif 'Quality=' in line and 'Signal level=' in line:
                # Extract signal quality and level
                quality_match = re.search(r'Quality=(\d+)/(\d+)', line)
                signal_match = re.search(r'Signal level=(-?\d+)', line)
                
                if quality_match:
                    quality = int(quality_match.group(1))
                    max_quality = int(quality_match.group(2))
                    current_network["quality"] = f"{quality}/{max_quality}"
                    current_network["quality_percent"] = round((quality / max_quality) * 100, 2)
                
                if signal_match:
                    current_network["signal_level"] = int(signal_match.group(1))
            
            elif 'Encryption key:' in line:
                encryption = 'on' in line.lower()
                current_network["encryption"] = encryption
            
            elif 'WPA' in line or 'WPA2' in line or 'WPA3' in line:
                if 'security' not in current_network:
                    current_network["security"] = []
                
                if 'WPA3' in line:
                    current_network["security"].append("WPA3")
                elif 'WPA2' in line:
                    current_network["security"].append("WPA2")
                elif 'WPA' in line:
                    current_network["security"].append("WPA")
        
        # Add last network
        if current_network:
            networks.append(current_network)
        
        return networks
    
    def analyze_channels(self, networks: List[Dict]) -> Dict:
        """Analyze channel usage and overlap"""
        print("[*] Analyzing channel usage...")
        
        channel_usage = {}
        
        for network in networks:
            channel = network.get("channel")
            if channel:
                if channel not in channel_usage:
                    channel_usage[channel] = []
                channel_usage[channel].append({
                    "essid": network.get("essid", "Hidden"),
                    "bssid": network.get("bssid"),
                    "signal_level": network.get("signal_level")
                })
        
        # Find overlapping channels
        overlaps = []
        for channel, aps in channel_usage.items():
            if len(aps) > 1:
                overlaps.append({
                    "channel": channel,
                    "ap_count": len(aps),
                    "access_points": aps
                })
        
        return {
            "channel_usage": channel_usage,
            "overlapping_channels": overlaps,
            "total_channels_used": len(channel_usage)
        }
    
    def check_security_issues(self, networks: List[Dict]) -> List[Dict]:
        """Check for security issues in wireless networks"""
        print("[*] Checking for security issues...")
        
        issues = []
        
        for network in networks:
            essid = network.get("essid", "Hidden")
            
            # Check for open networks
            if not network.get("encryption", False):
                issues.append({
                    "severity": "HIGH",
                    "type": "OPEN_NETWORK",
                    "network": essid,
                    "description": f"Network '{essid}' is open (no encryption)"
                })
            
            # Check for weak security
            security = network.get("security", [])
            if "WPA" in security and "WPA2" not in security and "WPA3" not in security:
                issues.append({
                    "severity": "MEDIUM",
                    "type": "WEAK_ENCRYPTION",
                    "network": essid,
                    "description": f"Network '{essid}' uses outdated WPA encryption"
                })
            
            # Check for weak signal
            signal = network.get("signal_level", 0)
            if signal < -70:
                issues.append({
                    "severity": "LOW",
                    "type": "WEAK_SIGNAL",
                    "network": essid,
                    "description": f"Network '{essid}' has weak signal ({signal} dBm)"
                })
        
        return issues
    
    def assess_wireless(self, interface: str = "wlan0") -> Dict:
        """Complete wireless network assessment"""
        networks = self.scan_wireless_networks(interface)
        
        if not networks:
            print("[!] No wireless networks found")
            self.results["status"] = "NO_NETWORKS_FOUND"
            return self.results
        
        self.results["networks"] = networks
        self.results["network_count"] = len(networks)
        
        # Analyze channels
        channel_analysis = self.analyze_channels(networks)
        self.results["channel_analysis"] = channel_analysis
        
        # Check security
        security_issues = self.check_security_issues(networks)
        self.results["security_issues"] = security_issues
        
        # Overall assessment
        self.results["status"] = "ISSUES_FOUND" if security_issues else "HEALTHY"
        
        # Save results
        output_file = f"{self.output_dir}/wireless_assessment_results.json"
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n[+] Wireless assessment complete!")
        print(f"[+] Found {len(networks)} wireless networks")
        print(f"[+] Found {len(security_issues)} security issues")
        print(f"[+] Results saved to {output_file}")
        
        return self.results

def main():
    parser = argparse.ArgumentParser(description='Wireless Network Assessment Tool')
    parser.add_argument('-i', '--interface', default='wlan0',
                        help='Wireless interface (default: wlan0)')
    parser.add_argument('-o', '--output', default='/tmp/network-scan',
                        help='Output directory')
    
    args = parser.parse_args()
    
    # Check if running as root
    import os
    if os.geteuid() != 0:
        print("[!] This tool requires root privileges")
        print("[!] Run with: sudo python3 wireless_assessment.py")
        return 1
    
    assessor = WirelessAssessment(args.output)
    results = assessor.assess_wireless(args.interface)
    
    return 0 if results.get("status") != "NO_NETWORKS_FOUND" else 1

if __name__ == "__main__":
    exit(main())
