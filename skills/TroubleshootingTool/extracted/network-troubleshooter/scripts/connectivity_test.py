#!/usr/bin/env python3
"""
Connectivity Testing Script
Tests internet connectivity, DNS, gateway reachability, and network performance
"""

import subprocess
import json
import time
import socket
import dns.resolver
from datetime import datetime
from typing import Dict, List, Tuple
import argparse

class ConnectivityTester:
    def __init__(self, output_dir: str = "/tmp/network-scan"):
        self.output_dir = output_dir
        self.results = {
            "test_time": datetime.now().isoformat(),
            "tests": {}
        }
        
    def test_gateway_reachability(self) -> Dict:
        """Test connectivity to default gateway"""
        print("[*] Testing gateway reachability...")
        
        try:
            # Get default gateway
            result = subprocess.run(
                ["ip", "route", "show", "default"],
                capture_output=True, text=True
            )
            
            gateway = None
            for line in result.stdout.split('\n'):
                if 'default via' in line:
                    gateway = line.split()[2]
                    break
            
            if not gateway:
                return {"status": "FAIL", "error": "No default gateway found"}
            
            # Ping gateway
            ping_result = self.ping_host(gateway, count=5)
            
            return {
                "status": "PASS" if ping_result["success"] else "FAIL",
                "gateway": gateway,
                "ping_stats": ping_result
            }
            
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}
    
    def test_internet_connectivity(self) -> Dict:
        """Test internet connectivity using multiple methods"""
        print("[*] Testing internet connectivity...")
        
        results = {
            "google_dns": self.ping_host("8.8.8.8", count=5),
            "cloudflare_dns": self.ping_host("1.1.1.1", count=5),
            "google_http": self.test_http_connectivity("google.com"),
        }
        
        # Determine overall status
        success_count = sum(1 for r in results.values() if r.get("success", False))
        
        return {
            "status": "PASS" if success_count >= 2 else "FAIL",
            "tests": results,
            "success_rate": f"{success_count}/3"
        }
    
    def ping_host(self, host: str, count: int = 4) -> Dict:
        """Ping a host and return statistics"""
        try:
            result = subprocess.run(
                ["ping", "-c", str(count), "-W", "2", host],
                capture_output=True, text=True, timeout=30
            )
            
            stats = {
                "host": host,
                "success": result.returncode == 0,
                "packets_sent": count,
                "packets_received": 0,
                "packet_loss": "100%",
                "rtt_min": None,
                "rtt_avg": None,
                "rtt_max": None
            }
            
            # Parse output
            for line in result.stdout.split('\n'):
                if 'packets transmitted' in line:
                    parts = line.split(',')
                    stats["packets_received"] = int(parts[1].split()[0])
                    stats["packet_loss"] = parts[2].split()[0].strip()
                
                if 'rtt min/avg/max' in line or 'round-trip min/avg/max' in line:
                    times = line.split('=')[1].split()[0].split('/')
                    stats["rtt_min"] = float(times[0])
                    stats["rtt_avg"] = float(times[1])
                    stats["rtt_max"] = float(times[2])
            
            return stats
            
        except Exception as e:
            return {
                "host": host,
                "success": False,
                "error": str(e)
            }
    
    def test_dns_resolution(self, test_domains: List[str] = None) -> Dict:
        """Test DNS resolution"""
        print("[*] Testing DNS resolution...")
        
        if test_domains is None:
            test_domains = ["google.com", "cloudflare.com", "github.com"]
        
        results = []
        resolver = dns.resolver.Resolver()
        
        # Get system DNS servers
        with open('/etc/resolv.conf', 'r') as f:
            dns_servers = [line.split()[1] for line in f if line.strip().startswith('nameserver')]
        
        for domain in test_domains:
            try:
                start_time = time.time()
                answers = resolver.resolve(domain, 'A')
                resolution_time = (time.time() - start_time) * 1000  # ms
                
                results.append({
                    "domain": domain,
                    "status": "PASS",
                    "ip_addresses": [str(rdata) for rdata in answers],
                    "resolution_time_ms": round(resolution_time, 2)
                })
                
            except Exception as e:
                results.append({
                    "domain": domain,
                    "status": "FAIL",
                    "error": str(e)
                })
        
        success_count = sum(1 for r in results if r["status"] == "PASS")
        
        return {
            "status": "PASS" if success_count == len(test_domains) else "PARTIAL" if success_count > 0 else "FAIL",
            "dns_servers": dns_servers,
            "tests": results
        }
    
    def test_http_connectivity(self, url: str) -> Dict:
        """Test HTTP/HTTPS connectivity"""
        try:
            import urllib.request
            
            start_time = time.time()
            response = urllib.request.urlopen(f"https://{url}", timeout=10)
            response_time = (time.time() - start_time) * 1000  # ms
            
            return {
                "url": url,
                "success": True,
                "status_code": response.getcode(),
                "response_time_ms": round(response_time, 2)
            }
            
        except Exception as e:
            return {
                "url": url,
                "success": False,
                "error": str(e)
            }
    
    def run_traceroute(self, target: str = "8.8.8.8") -> Dict:
        """Run traceroute to identify network path"""
        print(f"[*] Running traceroute to {target}...")
        
        try:
            result = subprocess.run(
                ["traceroute", "-m", "20", "-w", "2", target],
                capture_output=True, text=True, timeout=60
            )
            
            hops = []
            for line in result.stdout.split('\n')[1:]:  # Skip header
                if line.strip():
                    hops.append(line.strip())
            
            return {
                "target": target,
                "status": "COMPLETE",
                "hops": hops,
                "hop_count": len(hops)
            }
            
        except Exception as e:
            return {
                "target": target,
                "status": "ERROR",
                "error": str(e)
            }
    
    def test_bandwidth(self) -> Dict:
        """Basic bandwidth test using speedtest-cli"""
        print("[*] Testing bandwidth (this may take a moment)...")
        
        try:
            result = subprocess.run(
                ["speedtest-cli", "--simple"],
                capture_output=True, text=True, timeout=60
            )
            
            stats = {}
            for line in result.stdout.split('\n'):
                if 'Ping:' in line:
                    stats["ping_ms"] = float(line.split(':')[1].strip().split()[0])
                elif 'Download:' in line:
                    stats["download_mbps"] = float(line.split(':')[1].strip().split()[0])
                elif 'Upload:' in line:
                    stats["upload_mbps"] = float(line.split(':')[1].strip().split()[0])
            
            return {
                "status": "PASS",
                "stats": stats
            }
            
        except Exception as e:
            return {
                "status": "ERROR",
                "error": str(e),
                "note": "speedtest-cli may not be installed"
            }
    
    def run_all_tests(self, include_bandwidth: bool = False) -> Dict:
        """Run all connectivity tests"""
        print("\n=== Starting Connectivity Tests ===\n")
        
        self.results["tests"]["gateway"] = self.test_gateway_reachability()
        self.results["tests"]["internet"] = self.test_internet_connectivity()
        self.results["tests"]["dns"] = self.test_dns_resolution()
        self.results["tests"]["traceroute"] = self.run_traceroute()
        
        if include_bandwidth:
            self.results["tests"]["bandwidth"] = self.test_bandwidth()
        
        # Overall status
        failed_tests = [k for k, v in self.results["tests"].items() 
                       if v.get("status") in ["FAIL", "ERROR"]]
        
        self.results["overall_status"] = "PASS" if not failed_tests else "ISSUES_FOUND"
        self.results["failed_tests"] = failed_tests
        
        # Save results
        output_file = f"{self.output_dir}/connectivity_results.json"
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n[+] Tests complete! Overall status: {self.results['overall_status']}")
        print(f"[+] Results saved to {output_file}")
        
        return self.results

def main():
    parser = argparse.ArgumentParser(description='Network Connectivity Testing Tool')
    parser.add_argument('-o', '--output', default='/tmp/network-scan',
                        help='Output directory')
    parser.add_argument('-b', '--bandwidth', action='store_true',
                        help='Include bandwidth test')
    
    args = parser.parse_args()
    
    tester = ConnectivityTester(args.output)
    results = tester.run_all_tests(include_bandwidth=args.bandwidth)
    
    return 0 if results["overall_status"] == "PASS" else 1

if __name__ == "__main__":
    exit(main())
