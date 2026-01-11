#!/usr/bin/env python3
"""
DHCP and DNS Troubleshooting Script
Detects rogue DHCP servers, analyzes DNS configuration, and identifies issues
"""

import subprocess
import json
import socket
import struct
import random
from datetime import datetime
from typing import Dict, List
import argparse

class DHCPDNSTroubleshooter:
    def __init__(self, output_dir: str = "/tmp/network-scan"):
        self.output_dir = output_dir
        self.results = {
            "test_time": datetime.now().isoformat(),
            "dhcp": {},
            "dns": {}
        }
    
    def detect_dhcp_servers(self, interface: str = "eth0", timeout: int = 10) -> Dict:
        """Detect DHCP servers on the network"""
        print(f"[*] Scanning for DHCP servers on {interface}...")
        
        try:
            # Use dhcping or nmap to detect DHCP servers
            result = subprocess.run(
                ["nmap", "--script", "broadcast-dhcp-discover", "-e", interface],
                capture_output=True, text=True, timeout=30
            )
            
            dhcp_servers = []
            current_server = None
            
            for line in result.stdout.split('\n'):
                if 'Server Identifier' in line:
                    ip = line.split(':')[1].strip()
                    current_server = {"ip": ip, "details": {}}
                elif current_server and ':' in line and '|' in line:
                    key = line.split('|')[1].split(':')[0].strip()
                    value = line.split(':')[1].strip()
                    current_server["details"][key] = value
                elif current_server and line.strip() == '':
                    dhcp_servers.append(current_server)
                    current_server = None
            
            return {
                "status": "PASS" if len(dhcp_servers) == 1 else "WARNING" if len(dhcp_servers) > 1 else "NONE_FOUND",
                "server_count": len(dhcp_servers),
                "servers": dhcp_servers,
                "warning": "Multiple DHCP servers detected - possible rogue DHCP!" if len(dhcp_servers) > 1 else None
            }
            
        except Exception as e:
            return {
                "status": "ERROR",
                "error": str(e)
            }
    
    def check_dns_servers(self) -> Dict:
        """Check DNS server configuration"""
        print("[*] Checking DNS server configuration...")
        
        try:
            dns_servers = []
            search_domains = []
            
            # Read /etc/resolv.conf
            with open('/etc/resolv.conf', 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('nameserver'):
                        dns_servers.append(line.split()[1])
                    elif line.startswith('search'):
                        search_domains.extend(line.split()[1:])
            
            # Test each DNS server
            dns_tests = []
            for dns_server in dns_servers:
                test_result = self.test_dns_server(dns_server)
                dns_tests.append(test_result)
            
            working_servers = [t for t in dns_tests if t["status"] == "WORKING"]
            
            return {
                "status": "PASS" if working_servers else "FAIL",
                "configured_servers": dns_servers,
                "search_domains": search_domains,
                "server_tests": dns_tests,
                "working_servers": len(working_servers)
            }
            
        except Exception as e:
            return {
                "status": "ERROR",
                "error": str(e)
            }
    
    def test_dns_server(self, dns_server: str) -> Dict:
        """Test specific DNS server"""
        try:
            import dns.resolver
            
            resolver = dns.resolver.Resolver()
            resolver.nameservers = [dns_server]
            resolver.timeout = 5
            resolver.lifetime = 5
            
            # Test with common domain
            start_time = datetime.now()
            answers = resolver.resolve('google.com', 'A')
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return {
                "server": dns_server,
                "status": "WORKING",
                "response_time_ms": round(response_time, 2),
                "resolved_ips": [str(rdata) for rdata in answers]
            }
            
        except Exception as e:
            return {
                "server": dns_server,
                "status": "FAILED",
                "error": str(e)
            }
    
    def check_dns_zones(self, domains: List[str] = None) -> Dict:
        """Check DNS forward and reverse lookup"""
        print("[*] Checking DNS forward and reverse lookups...")
        
        if domains is None:
            domains = ["google.com", "cloudflare.com"]
        
        results = []
        
        for domain in domains:
            try:
                # Forward lookup
                forward_ips = socket.gethostbyname_ex(domain)[2]
                
                # Reverse lookup on first IP
                if forward_ips:
                    try:
                        reverse_name = socket.gethostbyaddr(forward_ips[0])[0]
                        reverse_match = domain in reverse_name
                    except:
                        reverse_name = None
                        reverse_match = False
                else:
                    reverse_name = None
                    reverse_match = False
                
                results.append({
                    "domain": domain,
                    "forward_lookup": forward_ips,
                    "reverse_lookup": reverse_name,
                    "reverse_match": reverse_match,
                    "status": "PASS"
                })
                
            except Exception as e:
                results.append({
                    "domain": domain,
                    "status": "FAIL",
                    "error": str(e)
                })
        
        return {
            "tests": results,
            "passed": sum(1 for r in results if r["status"] == "PASS")
        }
    
    def detect_split_dns(self) -> Dict:
        """Detect if split DNS is configured"""
        print("[*] Checking for split DNS configuration...")
        
        try:
            # Compare internal vs external DNS resolution
            internal_result = subprocess.run(
                ["host", "google.com"],
                capture_output=True, text=True
            )
            
            # Try using public DNS (8.8.8.8)
            external_result = subprocess.run(
                ["host", "google.com", "8.8.8.8"],
                capture_output=True, text=True
            )
            
            return {
                "internal_resolution": internal_result.stdout.strip(),
                "external_resolution": external_result.stdout.strip(),
                "split_dns_detected": internal_result.stdout != external_result.stdout
            }
            
        except Exception as e:
            return {
                "status": "ERROR",
                "error": str(e)
            }
    
    def check_static_ip_conflicts(self, network_range: str) -> Dict:
        """Check for potential static IP conflicts"""
        print(f"[*] Checking for static IP assignments in {network_range}...")
        
        # This would require comparing DHCP leases with active hosts
        # For now, return a placeholder
        return {
            "status": "NOT_IMPLEMENTED",
            "note": "Requires access to DHCP server lease database"
        }
    
    def run_all_checks(self, interface: str = "eth0") -> Dict:
        """Run all DHCP and DNS checks"""
        print("\n=== Starting DHCP/DNS Troubleshooting ===\n")
        
        self.results["dhcp"] = self.detect_dhcp_servers(interface)
        self.results["dns"]["servers"] = self.check_dns_servers()
        self.results["dns"]["zones"] = self.check_dns_zones()
        self.results["dns"]["split_dns"] = self.detect_split_dns()
        
        # Overall status
        issues = []
        if self.results["dhcp"].get("status") == "WARNING":
            issues.append("Multiple DHCP servers detected")
        if self.results["dns"]["servers"].get("status") == "FAIL":
            issues.append("DNS server issues")
        
        self.results["overall_status"] = "PASS" if not issues else "ISSUES_FOUND"
        self.results["issues"] = issues
        
        # Save results
        output_file = f"{self.output_dir}/dhcp_dns_results.json"
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n[+] Checks complete! Overall status: {self.results['overall_status']}")
        if issues:
            print("[!] Issues found:")
            for issue in issues:
                print(f"    - {issue}")
        print(f"[+] Results saved to {output_file}")
        
        return self.results

def main():
    parser = argparse.ArgumentParser(description='DHCP and DNS Troubleshooting Tool')
    parser.add_argument('-i', '--interface', default='eth0',
                        help='Network interface to use')
    parser.add_argument('-o', '--output', default='/tmp/network-scan',
                        help='Output directory')
    
    args = parser.parse_args()
    
    troubleshooter = DHCPDNSTroubleshooter(args.output)
    results = troubleshooter.run_all_checks(args.interface)
    
    return 0 if results["overall_status"] == "PASS" else 1

if __name__ == "__main__":
    exit(main())
