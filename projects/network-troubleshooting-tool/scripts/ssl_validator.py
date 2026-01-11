#!/usr/bin/env python3
"""
SSL/TLS Certificate Validation Script
Checks SSL certificates for expiry, chain validation, and security issues
"""

import ssl
import socket
import argparse
import json
from datetime import datetime, timedelta
from typing import Dict, List
import subprocess

class SSLValidator:
    def __init__(self, output_dir: str = "/tmp/network-scan"):
        self.output_dir = output_dir
        self.results = {
            "test_time": datetime.now().isoformat(),
            "certificates": []
        }
    
    def check_certificate(self, hostname: str, port: int = 443) -> Dict:
        """Check SSL certificate for a given host"""
        print(f"[*] Checking SSL certificate for {hostname}:{port}...")
        
        try:
            context = ssl.create_default_context()
            
            with socket.create_connection((hostname, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    
                    # Parse certificate details
                    not_before = datetime.strptime(cert['notBefore'], '%b %d %H:%M:%S %Y %Z')
                    not_after = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                    days_until_expiry = (not_after - datetime.now()).days
                    
                    # Determine status
                    if days_until_expiry < 0:
                        status = "EXPIRED"
                    elif days_until_expiry < 30:
                        status = "EXPIRING_SOON"
                    else:
                        status = "VALID"
                    
                    # Get issuer info
                    issuer = dict(x[0] for x in cert['issuer'])
                    subject = dict(x[0] for x in cert['subject'])
                    
                    result = {
                        "hostname": hostname,
                        "port": port,
                        "status": status,
                        "valid_from": not_before.isoformat(),
                        "valid_until": not_after.isoformat(),
                        "days_until_expiry": days_until_expiry,
                        "issuer": issuer.get('organizationName', 'Unknown'),
                        "subject_cn": subject.get('commonName', 'Unknown'),
                        "san": cert.get('subjectAltName', []),
                        "version": cert.get('version', 'Unknown'),
                        "serial_number": cert.get('serialNumber', 'Unknown')
                    }
                    
                    return result
                    
        except ssl.SSLError as e:
            return {
                "hostname": hostname,
                "port": port,
                "status": "SSL_ERROR",
                "error": str(e)
            }
        except socket.timeout:
            return {
                "hostname": hostname,
                "port": port,
                "status": "TIMEOUT",
                "error": "Connection timed out"
            }
        except Exception as e:
            return {
                "hostname": hostname,
                "port": port,
                "status": "ERROR",
                "error": str(e)
            }
    
    def check_tls_versions(self, hostname: str, port: int = 443) -> Dict:
        """Check which TLS versions are supported"""
        print(f"[*] Checking TLS versions for {hostname}:{port}...")
        
        tls_versions = {
            'TLSv1': ssl.PROTOCOL_TLSv1,
            'TLSv1.1': ssl.PROTOCOL_TLSv1_1,
            'TLSv1.2': ssl.PROTOCOL_TLSv1_2,
        }
        
        # Try TLSv1.3 if available
        if hasattr(ssl, 'PROTOCOL_TLSv1_3'):
            tls_versions['TLSv1.3'] = ssl.PROTOCOL_TLSv1_3
        
        supported = []
        
        for version_name, protocol in tls_versions.items():
            try:
                context = ssl.SSLContext(protocol)
                with socket.create_connection((hostname, port), timeout=5) as sock:
                    with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                        supported.append(version_name)
            except:
                pass
        
        # Check for insecure versions
        insecure = [v for v in supported if v in ['TLSv1', 'TLSv1.1']]
        
        return {
            "supported_versions": supported,
            "insecure_versions": insecure,
            "status": "INSECURE" if insecure else "SECURE"
        }
    
    def scan_network_for_ssl(self, network: str) -> List[Dict]:
        """Scan network for SSL/TLS services"""
        print(f"[*] Scanning {network} for SSL/TLS services...")
        
        try:
            # Use nmap to find SSL services
            result = subprocess.run(
                ["nmap", "-p", "443,8443,8080,3389", "--open", network],
                capture_output=True, text=True, timeout=300
            )
            
            # Parse nmap output to find hosts with open SSL ports
            hosts = []
            current_host = None
            
            for line in result.stdout.split('\n'):
                if 'Nmap scan report for' in line:
                    current_host = line.split()[-1].strip('()')
                elif '/tcp' in line and 'open' in line and current_host:
                    port = int(line.split('/')[0])
                    hosts.append((current_host, port))
            
            return hosts
            
        except Exception as e:
            print(f"[!] Network scan failed: {e}")
            return []
    
    def validate_multiple_hosts(self, hosts: List[tuple]) -> Dict:
        """Validate SSL certificates for multiple hosts"""
        results = []
        
        for hostname, port in hosts:
            cert_result = self.check_certificate(hostname, port)
            tls_result = self.check_tls_versions(hostname, port)
            
            combined = {**cert_result, **tls_result}
            results.append(combined)
            self.results["certificates"].append(combined)
        
        # Save results
        output_file = f"{self.output_dir}/ssl_validation_results.json"
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n[+] SSL validation complete!")
        print(f"[+] Results saved to {output_file}")
        
        return self.results

def main():
    parser = argparse.ArgumentParser(description='SSL/TLS Certificate Validation Tool')
    parser.add_argument('-H', '--host', help='Single host to check')
    parser.add_argument('-p', '--port', type=int, default=443, help='Port (default: 443)')
    parser.add_argument('-n', '--network', help='Network to scan for SSL services')
    parser.add_argument('-o', '--output', default='/tmp/network-scan',
                        help='Output directory')
    
    args = parser.parse_args()
    
    validator = SSLValidator(args.output)
    
    if args.host:
        # Single host check
        result = validator.check_certificate(args.host, args.port)
        tls_result = validator.check_tls_versions(args.host, args.port)
        
        print(f"\nCertificate Status: {result.get('status')}")
        print(f"Days Until Expiry: {result.get('days_until_expiry', 'N/A')}")
        print(f"TLS Status: {tls_result.get('status')}")
        
    elif args.network:
        # Network scan
        hosts = validator.scan_network_for_ssl(args.network)
        if hosts:
            validator.validate_multiple_hosts(hosts)
        else:
            print("[!] No SSL services found")
    else:
        print("[!] Specify either --host or --network")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
