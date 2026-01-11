#!/usr/bin/env python3
"""
Network Troubleshooter - Main Orchestration Script
Runs complete network assessment: discovery, connectivity tests, DHCP/DNS checks, and generates reports
"""

import os
import sys
import argparse
import subprocess
from datetime import datetime
import json

class NetworkTroubleshooter:
    def __init__(self, network: str, output_dir: str = None, interface: str = "eth0"):
        self.network = network
        self.interface = interface
        
        # Set output directory
        if output_dir is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.output_dir = f"/tmp/network-scan-{timestamp}"
        else:
            self.output_dir = output_dir
        
        # Get script directory
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        
        self.results_summary = {
            "start_time": datetime.now().isoformat(),
            "network": network,
            "output_dir": self.output_dir,
            "steps": []
        }
    
    def setup(self):
        """Create output directory and check dependencies"""
        print(f"\n{'='*60}")
        print(f"  Network Troubleshooter")
        print(f"  Target: {self.network}")
        print(f"  Output: {self.output_dir}")
        print(f"{'='*60}\n")
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"[+] Output directory created: {self.output_dir}")
        
        # Check for required tools
        required_tools = ["nmap", "arp-scan", "ping", "traceroute"]
        optional_tools = ["speedtest-cli", "netdiscover"]
        
        print("\n[*] Checking dependencies...")
        missing_required = []
        missing_optional = []
        
        for tool in required_tools:
            if subprocess.run(["which", tool], capture_output=True).returncode != 0:
                missing_required.append(tool)
        
        for tool in optional_tools:
            if subprocess.run(["which", tool], capture_output=True).returncode != 0:
                missing_optional.append(tool)
        
        if missing_required:
            print(f"[!] ERROR: Missing required tools: {', '.join(missing_required)}")
            print(f"[!] Install with: sudo apt-get install {' '.join(missing_required)}")
            return False
        
        if missing_optional:
            print(f"[!] Warning: Missing optional tools: {', '.join(missing_optional)}")
            print(f"    Some features may not work. Install with: sudo apt-get install {' '.join(missing_optional)}")
        
        print("[+] All required dependencies found")
        return True
    
    def run_step(self, name: str, script: str, args: list) -> bool:
        """Run a troubleshooting step"""
        print(f"\n{'='*60}")
        print(f"  Step: {name}")
        print(f"{'='*60}")
        
        script_path = os.path.join(self.script_dir, script)
        cmd = ["python3", script_path] + args
        
        step_result = {
            "name": name,
            "script": script,
            "start_time": datetime.now().isoformat()
        }
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            step_result["end_time"] = datetime.now().isoformat()
            step_result["returncode"] = result.returncode
            step_result["success"] = result.returncode == 0
            
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(f"[!] Errors: {result.stderr}", file=sys.stderr)
            
            self.results_summary["steps"].append(step_result)
            return result.returncode == 0
            
        except subprocess.TimeoutExpired:
            print(f"[!] Step timed out: {name}")
            step_result["success"] = False
            step_result["error"] = "Timeout"
            self.results_summary["steps"].append(step_result)
            return False
        
        except Exception as e:
            print(f"[!] Step failed: {name} - {e}")
            step_result["success"] = False
            step_result["error"] = str(e)
            self.results_summary["steps"].append(step_result)
            return False
    
    def run_network_discovery(self, quick: bool = False):
        """Run network discovery"""
        args = [self.network, "-o", self.output_dir]
        if quick:
            args.append("-q")
        
        return self.run_step(
            "Network Discovery",
            "network_discovery.py",
            args
        )
    
    def run_connectivity_tests(self, include_bandwidth: bool = False):
        """Run connectivity tests"""
        args = ["-o", self.output_dir]
        if include_bandwidth:
            args.append("-b")
        
        return self.run_step(
            "Connectivity Tests",
            "connectivity_test.py",
            args
        )
    
    def run_dhcp_dns_checks(self):
        """Run DHCP/DNS troubleshooting"""
        args = ["-i", self.interface, "-o", self.output_dir]
        
        return self.run_step(
            "DHCP/DNS Troubleshooting",
            "dhcp_dns_troubleshoot.py",
            args
        )
    
    def generate_reports(self):
        """Generate HTML and Markdown reports"""
        return self.run_step(
            "Report Generation",
            "generate_report.py",
            [self.output_dir]
        )
    
    def run_full_assessment(self, quick: bool = False, include_bandwidth: bool = False):
        """Run complete network assessment"""
        if not self.setup():
            print("\n[!] Setup failed. Cannot continue.")
            return False
        
        # Run all steps
        steps = [
            ("Discovery", lambda: self.run_network_discovery(quick)),
            ("Connectivity", lambda: self.run_connectivity_tests(include_bandwidth)),
            ("DHCP/DNS", self.run_dhcp_dns_checks),
            ("Reports", self.generate_reports)
        ]
        
        for step_name, step_func in steps:
            success = step_func()
            if not success:
                print(f"\n[!] Warning: {step_name} step had issues, but continuing...")
        
        # Save summary
        self.results_summary["end_time"] = datetime.now().isoformat()
        summary_file = os.path.join(self.output_dir, "assessment_summary.json")
        with open(summary_file, 'w') as f:
            json.dump(self.results_summary, f, indent=2)
        
        # Print final summary
        print(f"\n{'='*60}")
        print(f"  Assessment Complete!")
        print(f"{'='*60}")
        print(f"\nResults saved to: {self.output_dir}")
        print(f"\nReports:")
        print(f"  - HTML: {self.output_dir}/network_report.html")
        print(f"  - Markdown: {self.output_dir}/network_report.md")
        print(f"\nRaw Data:")
        print(f"  - Discovery: {self.output_dir}/discovery_results.json")
        print(f"  - Connectivity: {self.output_dir}/connectivity_results.json")
        print(f"  - DHCP/DNS: {self.output_dir}/dhcp_dns_results.json")
        print(f"\nTo view HTML report:")
        print(f"  firefox {self.output_dir}/network_report.html")
        print()
        
        return True

def main():
    parser = argparse.ArgumentParser(
        description='Network Troubleshooter - Complete Network Assessment Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full assessment of 192.168.1.0/24 network
  %(prog)s 192.168.1.0/24
  
  # Quick scan without intensive checks
  %(prog)s 192.168.1.0/24 -q
  
  # Include bandwidth testing
  %(prog)s 192.168.1.0/24 -b
  
  # Custom output directory
  %(prog)s 192.168.1.0/24 -o /opt/network-reports/customer1
  
  # Specify network interface
  %(prog)s 192.168.1.0/24 -i enp0s3
        """
    )
    
    parser.add_argument('network', 
                        help='Target network in CIDR notation (e.g., 192.168.1.0/24)')
    parser.add_argument('-o', '--output', 
                        help='Output directory (default: /tmp/network-scan-TIMESTAMP)')
    parser.add_argument('-i', '--interface', default='eth0',
                        help='Network interface to use (default: eth0)')
    parser.add_argument('-q', '--quick', action='store_true',
                        help='Quick scan (skip intensive checks)')
    parser.add_argument('-b', '--bandwidth', action='store_true',
                        help='Include bandwidth testing (requires speedtest-cli)')
    
    args = parser.parse_args()
    
    # Check for root privileges
    if os.geteuid() != 0:
        print("[!] Warning: Some scans require root privileges")
        print("[!] Run with sudo for complete results\n")
    
    troubleshooter = NetworkTroubleshooter(
        args.network,
        args.output,
        args.interface
    )
    
    success = troubleshooter.run_full_assessment(
        quick=args.quick,
        include_bandwidth=args.bandwidth
    )
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
