#!/usr/bin/env python3
"""
SNMP Monitoring Script
Queries network devices via SNMP for health, interface stats, and error rates
"""

import argparse
import json
from datetime import datetime
from typing import Dict, List
import subprocess

class SNMPMonitor:
    def __init__(self, output_dir: str = "/tmp/network-scan"):
        self.output_dir = output_dir
        self.results = {
            "test_time": datetime.now().isoformat(),
            "devices": []
        }
    
    def snmp_walk(self, host: str, community: str, oid: str) -> List[str]:
        """Perform SNMP walk"""
        try:
            cmd = ["snmpwalk", "-v2c", "-c", community, host, oid]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return result.stdout.strip().split('\n')
            return []
        except Exception as e:
            print(f"[!] SNMP walk failed for {host}: {e}")
            return []
    
    def snmp_get(self, host: str, community: str, oid: str) -> str:
        """Perform SNMP get"""
        try:
            cmd = ["snmpget", "-v2c", "-c", community, "-Oqv", host, oid]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                return result.stdout.strip().strip('"')
            return None
        except Exception as e:
            print(f"[!] SNMP get failed for {host}: {e}")
            return None
    
    def get_system_info(self, host: str, community: str = "public") -> Dict:
        """Get system information via SNMP"""
        print(f"[*] Getting system info for {host}...")
        
        oids = {
            "sysDescr": "1.3.6.1.2.1.1.1.0",
            "sysUpTime": "1.3.6.1.2.1.1.3.0",
            "sysContact": "1.3.6.1.2.1.1.4.0",
            "sysName": "1.3.6.1.2.1.1.5.0",
            "sysLocation": "1.3.6.1.2.1.1.6.0"
        }
        
        info = {"host": host, "status": "SUCCESS"}
        
        for name, oid in oids.items():
            value = self.snmp_get(host, community, oid)
            info[name] = value if value else "N/A"
        
        return info
    
    def get_interface_stats(self, host: str, community: str = "public") -> Dict:
        """Get interface statistics"""
        print(f"[*] Getting interface stats for {host}...")
        
        # Interface descriptions
        if_descr = self.snmp_walk(host, community, "1.3.6.1.2.1.2.2.1.2")
        
        # Interface status (1=up, 2=down)
        if_oper_status = self.snmp_walk(host, community, "1.3.6.1.2.1.2.2.1.8")
        
        # Interface errors
        if_in_errors = self.snmp_walk(host, community, "1.3.6.1.2.1.2.2.1.14")
        if_out_errors = self.snmp_walk(host, community, "1.3.6.1.2.1.2.2.1.20")
        
        # Interface octets (traffic)
        if_in_octets = self.snmp_walk(host, community, "1.3.6.1.2.1.2.2.1.10")
        if_out_octets = self.snmp_walk(host, community, "1.3.6.1.2.1.2.2.1.16")
        
        interfaces = []
        
        for i in range(len(if_descr)):
            try:
                interface = {
                    "index": i + 1,
                    "description": if_descr[i].split('=')[-1].strip() if i < len(if_descr) else "N/A",
                    "status": "UP" if "1" in if_oper_status[i] else "DOWN" if i < len(if_oper_status) else "UNKNOWN",
                    "in_errors": if_in_errors[i].split(':')[-1].strip() if i < len(if_in_errors) else "0",
                    "out_errors": if_out_errors[i].split(':')[-1].strip() if i < len(if_out_errors) else "0",
                    "in_octets": if_in_octets[i].split(':')[-1].strip() if i < len(if_in_octets) else "0",
                    "out_octets": if_out_octets[i].split(':')[-1].strip() if i < len(if_out_octets) else "0"
                }
                
                interfaces.append(interface)
            except Exception as e:
                print(f"[!] Error parsing interface {i}: {e}")
        
        return {
            "host": host,
            "interface_count": len(interfaces),
            "interfaces": interfaces
        }
    
    def get_cpu_memory(self, host: str, community: str = "public") -> Dict:
        """Get CPU and memory usage"""
        print(f"[*] Getting CPU/Memory stats for {host}...")
        
        # These OIDs may vary by vendor
        # HOST-RESOURCES-MIB
        cpu_oid = "1.3.6.1.2.1.25.3.3.1.2"  # hrProcessorLoad
        mem_total_oid = "1.3.6.1.2.1.25.2.3.1.5.1"  # hrStorageSize
        mem_used_oid = "1.3.6.1.2.1.25.2.3.1.6.1"  # hrStorageUsed
        
        cpu_loads = self.snmp_walk(host, community, cpu_oid)
        
        result = {
            "host": host,
            "cpu_cores": len(cpu_loads),
            "cpu_loads": []
        }
        
        for load in cpu_loads:
            try:
                value = load.split(':')[-1].strip()
                result["cpu_loads"].append(value)
            except:
                pass
        
        # Memory
        mem_total = self.snmp_get(host, community, mem_total_oid)
        mem_used = self.snmp_get(host, community, mem_used_oid)
        
        if mem_total and mem_used:
            try:
                total = int(mem_total)
                used = int(mem_used)
                percent = (used / total * 100) if total > 0 else 0
                result["memory"] = {
                    "total": total,
                    "used": used,
                    "percent": round(percent, 2)
                }
            except:
                result["memory"] = "N/A"
        
        return result
    
    def monitor_device(self, host: str, community: str = "public") -> Dict:
        """Comprehensive device monitoring"""
        device_data = {
            "host": host,
            "timestamp": datetime.now().isoformat()
        }
        
        # Get all information
        device_data["system_info"] = self.get_system_info(host, community)
        device_data["interfaces"] = self.get_interface_stats(host, community)
        device_data["performance"] = self.get_cpu_memory(host, community)
        
        # Check for issues
        issues = []
        
        # Check for interface errors
        for iface in device_data["interfaces"].get("interfaces", []):
            try:
                in_errors = int(iface.get("in_errors", 0))
                out_errors = int(iface.get("out_errors", 0))
                
                if in_errors > 1000 or out_errors > 1000:
                    issues.append(f"High error rate on {iface['description']}: IN={in_errors}, OUT={out_errors}")
            except:
                pass
        
        # Check CPU
        if device_data["performance"].get("cpu_loads"):
            try:
                avg_cpu = sum(float(l) for l in device_data["performance"]["cpu_loads"]) / len(device_data["performance"]["cpu_loads"])
                if avg_cpu > 80:
                    issues.append(f"High CPU usage: {avg_cpu:.1f}%")
            except:
                pass
        
        # Check memory
        if isinstance(device_data["performance"].get("memory"), dict):
            mem_percent = device_data["performance"]["memory"].get("percent", 0)
            if mem_percent > 85:
                issues.append(f"High memory usage: {mem_percent:.1f}%")
        
        device_data["issues"] = issues
        device_data["status"] = "WARNING" if issues else "HEALTHY"
        
        return device_data
    
    def monitor_multiple_devices(self, hosts: List[str], community: str = "public"):
        """Monitor multiple devices"""
        for host in hosts:
            device_data = self.monitor_device(host, community)
            self.results["devices"].append(device_data)
        
        # Save results
        output_file = f"{self.output_dir}/snmp_monitoring_results.json"
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n[+] SNMP monitoring complete!")
        print(f"[+] Monitored {len(hosts)} devices")
        print(f"[+] Results saved to {output_file}")
        
        return self.results

def main():
    parser = argparse.ArgumentParser(description='SNMP Network Device Monitoring Tool')
    parser.add_argument('-H', '--host', help='Single host to monitor')
    parser.add_argument('-f', '--file', help='File with list of hosts (one per line)')
    parser.add_argument('-c', '--community', default='public',
                        help='SNMP community string (default: public)')
    parser.add_argument('-o', '--output', default='/tmp/network-scan',
                        help='Output directory')
    
    args = parser.parse_args()
    
    monitor = SNMPMonitor(args.output)
    
    hosts = []
    
    if args.host:
        hosts = [args.host]
    elif args.file:
        with open(args.file, 'r') as f:
            hosts = [line.strip() for line in f if line.strip()]
    else:
        print("[!] Specify either --host or --file")
        return 1
    
    monitor.monitor_multiple_devices(hosts, args.community)
    
    return 0

if __name__ == "__main__":
    exit(main())
