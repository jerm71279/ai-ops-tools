#!/usr/bin/env python3
"""
Port Security Audit Script
Identifies unnecessary open ports, vulnerable services, and security risks
"""

import subprocess
import json
import argparse
from datetime import datetime
from typing import Dict, List
import xml.etree.ElementTree as ET

class PortSecurityAuditor:
    def __init__(self, output_dir: str = "/tmp/network-scan"):
        self.output_dir = output_dir
        self.results = {
            "scan_time": datetime.now().isoformat(),
            "hosts": []
        }
        
        # Common vulnerable services
        self.vulnerable_services = {
            21: {"name": "FTP", "risk": "HIGH", "reason": "Unencrypted file transfer"},
            23: {"name": "Telnet", "risk": "HIGH", "reason": "Unencrypted remote access"},
            25: {"name": "SMTP", "risk": "MEDIUM", "reason": "Potential relay abuse"},
            53: {"name": "DNS", "risk": "LOW", "reason": "May allow zone transfers"},
            69: {"name": "TFTP", "risk": "HIGH", "reason": "Unencrypted, no authentication"},
            110: {"name": "POP3", "risk": "MEDIUM", "reason": "Unencrypted email"},
            135: {"name": "MS-RPC", "risk": "HIGH", "reason": "Windows RPC vulnerabilities"},
            139: {"name": "NetBIOS", "risk": "HIGH", "reason": "SMBv1 vulnerabilities"},
            143: {"name": "IMAP", "risk": "MEDIUM", "reason": "Unencrypted email"},
            445: {"name": "SMB", "risk": "HIGH", "reason": "File sharing vulnerabilities"},
            512: {"name": "rexec", "risk": "HIGH", "reason": "Unencrypted remote execution"},
            513: {"name": "rlogin", "risk": "HIGH", "reason": "Unencrypted remote login"},
            514: {"name": "rsh", "risk": "HIGH", "reason": "Unencrypted remote shell"},
            1433: {"name": "MS-SQL", "risk": "MEDIUM", "reason": "Database exposure"},
            1521: {"name": "Oracle", "risk": "MEDIUM", "reason": "Database exposure"},
            3306: {"name": "MySQL", "risk": "MEDIUM", "reason": "Database exposure"},
            3389: {"name": "RDP", "risk": "MEDIUM", "reason": "Remote desktop attacks"},
            5432: {"name": "PostgreSQL", "risk": "MEDIUM", "reason": "Database exposure"},
            5900: {"name": "VNC", "risk": "HIGH", "reason": "Often weak/no password"},
            8080: {"name": "HTTP-Proxy", "risk": "MEDIUM", "reason": "Alternative HTTP"},
            27017: {"name": "MongoDB", "risk": "HIGH", "reason": "Often misconfigured"},
        }
    
    def scan_ports(self, target: str, port_range: str = "1-65535") -> str:
        """Comprehensive port scan"""
        print(f"[*] Scanning ports on {target} (this may take a while)...")
        
        output_file = f"{self.output_dir}/portscan_{target.replace('.', '_').replace('/', '_')}.xml"
        
        cmd = [
            "nmap",
            "-sV",  # Version detection
            "-sC",  # Default scripts
            "-O",   # OS detection
            "-p", port_range,
            "--open",  # Only show open ports
            target,
            "-oX", output_file,
            "-T4"  # Faster timing
        ]
        
        try:
            subprocess.run(cmd, capture_output=True, timeout=1800)
            return output_file
        except subprocess.TimeoutExpired:
            print("[!] Port scan timed out after 30 minutes")
            return None
        except Exception as e:
            print(f"[!] Port scan failed: {e}")
            return None
    
    def parse_nmap_results(self, xml_file: str) -> List[Dict]:
        """Parse nmap XML results"""
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            hosts = []
            
            for host in root.findall('host'):
                host_data = {
                    "status": host.find('status').get('state'),
                    "addresses": [],
                    "ports": [],
                    "os": [],
                    "risk_score": 0,
                    "vulnerabilities": []
                }
                
                # Get IP address
                for addr in host.findall('address'):
                    if addr.get('addrtype') == 'ipv4':
                        host_data["ip"] = addr.get('addr')
                    host_data["addresses"].append({
                        "addr": addr.get('addr'),
                        "type": addr.get('addrtype')
                    })
                
                # Parse ports
                ports_elem = host.find('ports')
                if ports_elem is not None:
                    for port in ports_elem.findall('port'):
                        port_num = int(port.get('portid'))
                        protocol = port.get('protocol')
                        
                        state = port.find('state')
                        service = port.find('service')
                        
                        port_data = {
                            "port": port_num,
                            "protocol": protocol,
                            "state": state.get('state') if state is not None else 'unknown'
                        }
                        
                        if service is not None:
                            port_data["service"] = service.get('name', 'unknown')
                            port_data["product"] = service.get('product', '')
                            port_data["version"] = service.get('version', '')
                        
                        # Check if this is a vulnerable service
                        if port_num in self.vulnerable_services:
                            vuln = self.vulnerable_services[port_num]
                            port_data["vulnerability"] = vuln
                            
                            # Add to vulnerabilities list
                            host_data["vulnerabilities"].append({
                                "port": port_num,
                                "service": vuln["name"],
                                "risk": vuln["risk"],
                                "reason": vuln["reason"]
                            })
                            
                            # Calculate risk score
                            risk_values = {"HIGH": 10, "MEDIUM": 5, "LOW": 2}
                            host_data["risk_score"] += risk_values.get(vuln["risk"], 0)
                        
                        host_data["ports"].append(port_data)
                
                # Get OS information
                os_elem = host.find('os')
                if os_elem is not None:
                    for osmatch in os_elem.findall('osmatch'):
                        host_data["os"].append({
                            "name": osmatch.get('name'),
                            "accuracy": osmatch.get('accuracy')
                        })
                
                # Determine overall security posture
                if host_data["risk_score"] >= 20:
                    host_data["security_posture"] = "CRITICAL"
                elif host_data["risk_score"] >= 10:
                    host_data["security_posture"] = "HIGH_RISK"
                elif host_data["risk_score"] >= 5:
                    host_data["security_posture"] = "MEDIUM_RISK"
                else:
                    host_data["security_posture"] = "LOW_RISK"
                
                hosts.append(host_data)
            
            return hosts
            
        except Exception as e:
            print(f"[!] Failed to parse nmap results: {e}")
            return []
    
    def generate_recommendations(self, host_data: Dict) -> List[str]:
        """Generate security recommendations"""
        recommendations = []
        
        for vuln in host_data.get("vulnerabilities", []):
            port = vuln["port"]
            service = vuln["service"]
            risk = vuln["risk"]
            
            if risk == "HIGH":
                if service in ["FTP", "Telnet", "rexec", "rlogin", "rsh"]:
                    recommendations.append(
                        f"CRITICAL: Disable {service} on port {port}. Use SSH instead for secure remote access."
                    )
                elif service == "NetBIOS" or service == "SMB":
                    recommendations.append(
                        f"CRITICAL: Secure or disable {service} on port {port}. Enable SMB signing and disable SMBv1."
                    )
                elif service == "TFTP":
                    recommendations.append(
                        f"CRITICAL: Disable TFTP on port {port} or restrict to trusted networks only."
                    )
                elif service == "VNC":
                    recommendations.append(
                        f"CRITICAL: Secure VNC on port {port} with strong password and consider using SSH tunnel."
                    )
                elif service == "MongoDB":
                    recommendations.append(
                        f"CRITICAL: Secure MongoDB on port {port}. Enable authentication and bind to localhost."
                    )
            
            elif risk == "MEDIUM":
                if service in ["MySQL", "PostgreSQL", "MS-SQL", "Oracle"]:
                    recommendations.append(
                        f"WARNING: Database {service} on port {port} should not be exposed. Use firewall rules or VPN."
                    )
                elif service == "RDP":
                    recommendations.append(
                        f"WARNING: RDP on port {port} should use Network Level Authentication and strong passwords."
                    )
                elif service in ["POP3", "IMAP", "SMTP"]:
                    recommendations.append(
                        f"INFO: Consider using encrypted alternatives (POP3S, IMAPS, SMTPS) instead of {service}."
                    )
        
        # Check for excessive open ports
        open_ports = len([p for p in host_data.get("ports", []) if p["state"] == "open"])
        if open_ports > 20:
            recommendations.append(
                f"INFO: {open_ports} open ports detected. Review and close unnecessary services."
            )
        
        return recommendations
    
    def audit_security(self, target: str, port_range: str = "1-1000") -> Dict:
        """Perform complete security audit"""
        # Scan ports
        xml_file = self.scan_ports(target, port_range)
        
        if not xml_file:
            self.results["status"] = "SCAN_FAILED"
            return self.results
        
        # Parse results
        hosts = self.parse_nmap_results(xml_file)
        
        # Generate recommendations for each host
        for host in hosts:
            host["recommendations"] = self.generate_recommendations(host)
        
        self.results["hosts"] = hosts
        self.results["total_hosts"] = len(hosts)
        self.results["high_risk_hosts"] = len([h for h in hosts if h["security_posture"] in ["CRITICAL", "HIGH_RISK"]])
        
        # Save results
        output_file = f"{self.output_dir}/port_security_audit.json"
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n[+] Security audit complete!")
        print(f"[+] Scanned {len(hosts)} hosts")
        print(f"[+] Found {self.results['high_risk_hosts']} high-risk hosts")
        print(f"[+] Results saved to {output_file}")
        
        return self.results

def main():
    parser = argparse.ArgumentParser(description='Port Security Audit Tool')
    parser.add_argument('target', help='Target IP or network (e.g., 192.168.1.1 or 192.168.1.0/24)')
    parser.add_argument('-p', '--ports', default='1-1000',
                        help='Port range to scan (default: 1-1000)')
    parser.add_argument('-o', '--output', default='/tmp/network-scan',
                        help='Output directory')
    
    args = parser.parse_args()
    
    auditor = PortSecurityAuditor(args.output)
    auditor.audit_security(args.target, args.ports)
    
    return 0

if __name__ == "__main__":
    exit(main())
