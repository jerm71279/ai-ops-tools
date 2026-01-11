#!/usr/bin/env python3
"""
Network Discovery Script
Performs comprehensive network scanning and device discovery
"""

import subprocess
import json
import ipaddress
import argparse
from datetime import datetime
from typing import Dict, List, Any
import xml.etree.ElementTree as ET

class NetworkDiscovery:
    def __init__(self, target_network: str, output_dir: str = "/tmp/network-scan"):
        self.target = target_network
        self.output_dir = output_dir
        self.results = {
            "scan_time": datetime.now().isoformat(),
            "target_network": target_network,
            "devices": [],
            "summary": {}
        }
        
    def validate_network(self) -> bool:
        """Validate the network address"""
        try:
            ipaddress.ip_network(self.target)
            return True
        except ValueError:
            return False
    
    def run_arp_scan(self) -> List[Dict]:
        """Quick ARP scan for live hosts"""
        print(f"[*] Running ARP scan on {self.target}...")
        devices = []
        
        try:
            cmd = ["arp-scan", "-l", "-I", "eth0", self.target]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            for line in result.stdout.split('\n'):
                if '\t' in line and not line.startswith('Interface'):
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        devices.append({
                            "ip": parts[0].strip(),
                            "mac": parts[1].strip(),
                            "vendor": parts[2].strip() if len(parts) > 2 else "Unknown"
                        })
        except Exception as e:
            print(f"[!] ARP scan failed: {e}")
            
        return devices
    
    def run_nmap_discovery(self, aggressive: bool = False) -> str:
        """Run nmap network discovery"""
        print(f"[*] Running nmap discovery on {self.target}...")
        
        output_file = f"{self.output_dir}/nmap_scan.xml"
        
        # Build nmap command
        cmd = ["nmap", "-sn", "-PE", "-PA21,23,80,443,3389", self.target, 
               "-oX", output_file, "-oN", f"{self.output_dir}/nmap_scan.txt"]
        
        if aggressive:
            cmd = ["nmap", "-A", "-T4", self.target, 
                   "-oX", output_file, "-oN", f"{self.output_dir}/nmap_scan.txt"]
        
        try:
            subprocess.run(cmd, capture_output=True, timeout=600)
            return output_file
        except Exception as e:
            print(f"[!] Nmap scan failed: {e}")
            return None
    
    def run_nmap_port_scan(self, target_ip: str) -> Dict:
        """Detailed port scan on specific host"""
        print(f"[*] Port scanning {target_ip}...")
        
        output_file = f"{self.output_dir}/nmap_{target_ip.replace('.', '_')}.xml"
        
        cmd = ["nmap", "-sV", "-sC", "-O", target_ip, 
               "-oX", output_file, "--version-intensity", "5"]
        
        try:
            subprocess.run(cmd, capture_output=True, timeout=300)
            return self.parse_nmap_xml(output_file)
        except Exception as e:
            print(f"[!] Port scan failed for {target_ip}: {e}")
            return {}
    
    def parse_nmap_xml(self, xml_file: str) -> Dict:
        """Parse nmap XML output"""
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            devices = []
            for host in root.findall('host'):
                device = {
                    "status": host.find('status').get('state'),
                    "addresses": [],
                    "hostnames": [],
                    "ports": [],
                    "os": []
                }
                
                # Get addresses
                for addr in host.findall('address'):
                    device["addresses"].append({
                        "addr": addr.get('addr'),
                        "type": addr.get('addrtype'),
                        "vendor": addr.get('vendor', 'Unknown')
                    })
                
                # Get hostnames
                hostnames_elem = host.find('hostnames')
                if hostnames_elem is not None:
                    for hostname in hostnames_elem.findall('hostname'):
                        device["hostnames"].append(hostname.get('name'))
                
                # Get ports
                ports_elem = host.find('ports')
                if ports_elem is not None:
                    for port in ports_elem.findall('port'):
                        state = port.find('state')
                        service = port.find('service')
                        
                        port_info = {
                            "port": port.get('portid'),
                            "protocol": port.get('protocol'),
                            "state": state.get('state') if state is not None else 'unknown'
                        }
                        
                        if service is not None:
                            port_info.update({
                                "service": service.get('name', 'unknown'),
                                "product": service.get('product', ''),
                                "version": service.get('version', '')
                            })
                        
                        device["ports"].append(port_info)
                
                # Get OS detection
                os_elem = host.find('os')
                if os_elem is not None:
                    for osmatch in os_elem.findall('osmatch'):
                        device["os"].append({
                            "name": osmatch.get('name'),
                            "accuracy": osmatch.get('accuracy')
                        })
                
                devices.append(device)
            
            return {"hosts": devices}
            
        except Exception as e:
            print(f"[!] Failed to parse nmap XML: {e}")
            return {}
    
    def run_netdiscover(self) -> List[Dict]:
        """Run netdiscover for additional discovery"""
        print(f"[*] Running netdiscover on {self.target}...")
        devices = []
        
        try:
            cmd = ["netdiscover", "-r", self.target, "-P", "-N"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            # Parse netdiscover output
            lines = result.stdout.split('\n')
            for line in lines:
                if line.strip() and not line.startswith('_') and not line.startswith('Currently'):
                    parts = line.split()
                    if len(parts) >= 3:
                        devices.append({
                            "ip": parts[0],
                            "mac": parts[1],
                            "vendor": ' '.join(parts[2:])
                        })
        except Exception as e:
            print(f"[!] Netdiscover failed: {e}")
        
        return devices
    
    def discover(self, quick: bool = False) -> Dict:
        """Run full discovery process"""
        # Create output directory
        subprocess.run(["mkdir", "-p", self.output_dir], check=True)
        
        # Run different discovery methods
        arp_devices = self.run_arp_scan()
        self.run_nmap_discovery(aggressive=not quick)
        
        if not quick:
            netdiscover_devices = self.run_netdiscover()
        
        # Combine results
        self.results["arp_scan"] = arp_devices
        self.results["summary"]["total_devices"] = len(arp_devices)
        
        # Save results
        output_file = f"{self.output_dir}/discovery_results.json"
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n[+] Discovery complete! Found {len(arp_devices)} devices")
        print(f"[+] Results saved to {output_file}")
        
        return self.results

def main():
    parser = argparse.ArgumentParser(description='Network Discovery Tool')
    parser.add_argument('network', help='Target network (e.g., 192.168.1.0/24)')
    parser.add_argument('-o', '--output', default='/tmp/network-scan', 
                        help='Output directory')
    parser.add_argument('-q', '--quick', action='store_true', 
                        help='Quick scan (skip intensive scans)')
    
    args = parser.parse_args()
    
    scanner = NetworkDiscovery(args.network, args.output)
    
    if not scanner.validate_network():
        print(f"[!] Invalid network address: {args.network}")
        return 1
    
    results = scanner.discover(quick=args.quick)
    
    return 0

if __name__ == "__main__":
    exit(main())
