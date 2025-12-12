---
name: network-troubleshooter
description: Comprehensive IT network troubleshooting and assessment toolkit for network discovery, connectivity testing, DHCP/DNS diagnostics, wireless assessment, security auditing, and automated report generation. Use when (1) Performing pre-installation network discovery and assessment, (2) Troubleshooting network connectivity issues (internet access, gateway, DNS, DHCP), (3) Creating network documentation and topology maps, (4) Auditing network security and identifying vulnerabilities, (5) Monitoring network device health via SNMP, (6) Assessing wireless networks, (7) Validating SSL/TLS certificates, (8) Generating network assessment reports, (9) Diagnosing slow network performance, (10) Identifying rogue devices or DHCP servers
---

# Network Troubleshooter Skill

Comprehensive network troubleshooting and assessment toolkit designed for IT professionals performing network discovery, pre-installation checks, security audits, and troubleshooting tasks.

## Overview

This skill provides automated tools covering the top 10 IT network troubleshooting use cases:

1. **Network Discovery** - Discover all devices on a network using ARP, nmap, netdiscover
2. **Connectivity Testing** - Test internet access, gateway reachability, DNS resolution, traceroute
3. **DHCP/DNS Troubleshooting** - Detect rogue DHCP servers, validate DNS configuration
4. **SSL/TLS Certificate Validation** - Check certificate expiry, chain validation, security
5. **DNS Health Checks** - Forward/reverse lookup validation, server testing
6. **SNMP Monitoring** - Device health, interface stats, error rates
7. **Wireless Network Assessment** - Signal strength, channel overlap, AP discovery, security
8. **Network Performance Testing** - Bandwidth tests, latency, throughput
9. **Port Security Audit** - Identify unnecessary open ports, vulnerable services
10. **Automated Report Generation** - HTML and Markdown reports with findings and recommendations

## Core Scripts

### Main Orchestration

**`run_assessment.py`** - Complete network assessment workflow. Runs full pre-installation assessment including discovery, connectivity tests, DHCP/DNS checks, and report generation.

Usage:
```bash
sudo python3 run_assessment.py 192.168.1.0/24
sudo python3 run_assessment.py 192.168.1.0/24 -o /opt/reports/customer1 -b
```

### Individual Tools

**`network_discovery.py`** - Network discovery and device enumeration using ARP scan, nmap, and netdiscover

**`connectivity_test.py`** - Internet and gateway connectivity testing, DNS resolution, traceroute

**`dhcp_dns_troubleshoot.py`** - DHCP server detection and DNS troubleshooting

**`ssl_validator.py`** - SSL/TLS certificate validation and security checking

**`snmp_monitor.py`** - SNMP device monitoring for health and performance metrics

**`wireless_assessment.py`** - Wireless network scanning and security assessment

**`port_security_audit.py`** - Comprehensive port scanning and security vulnerability identification

**`generate_report.py`** - Report generation combining all scan results

## Typical Workflows

### Pre-Installation Assessment
```bash
sudo python3 run_assessment.py 192.168.1.0/24 -o /opt/customer-reports/site1
```

### Internet Troubleshooting
```bash
python3 connectivity_test.py -o /tmp/troubleshoot
```

### Security Audit
```bash
sudo python3 port_security_audit.py 192.168.1.0/24 -p 1-1000 -o /tmp/security
```

### DHCP Issues
```bash
sudo python3 dhcp_dns_troubleshoot.py -i eth0 -o /tmp/dhcp-check
```

## Reference Documentation

See `references/troubleshooting_workflows.md` for:
- Step-by-step troubleshooting workflows
- Emergency troubleshooting checklists
- Common command reference
- Troubleshooting decision trees

## Requirements

**Required:** nmap, arp-scan, ping, traceroute, Python 3.6+, dnspython
**Optional:** speedtest-cli, netdiscover, snmp tools, wireless-tools

Installation:
```bash
sudo apt-get install nmap arp-scan traceroute python3-pip
pip3 install dnspython --break-system-packages
```

Most tools require root privileges (`sudo`).

## Output Files

- `network_report.html` - Comprehensive HTML report
- `network_report.md` - Markdown summary
- `*_results.json` - Raw JSON data files
- `nmap_scan.xml` - Nmap scan data

## USB Bootable Deployment

Create portable troubleshooting USB by installing Linux Live environment with all tools and scripts pre-configured to auto-run on network detection.

See SKILL.md for complete documentation, troubleshooting tips, and integration with monitoring systems like NinjaOne.
