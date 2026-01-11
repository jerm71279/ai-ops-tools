# Common Network Troubleshooting Workflows

This document provides step-by-step workflows for common network troubleshooting scenarios.

## Workflow 1: Pre-Installation Network Discovery

**Goal:** Complete network assessment before customer installation

**Steps:**
1. Run full network discovery to identify all devices
2. Test connectivity to gateway and internet
3. Check for rogue DHCP servers
4. Validate DNS configuration
5. Identify static IP assignments
6. Check for VLAN configuration
7. Generate comprehensive report

**Script Sequence:**
```bash
# Complete assessment
sudo python3 run_assessment.py 192.168.1.0/24 -o /tmp/customer-precheck

# Or individual steps:
sudo python3 network_discovery.py 192.168.1.0/24 -o /tmp/scan
python3 connectivity_test.py -o /tmp/scan -b
sudo python3 dhcp_dns_troubleshoot.py -i eth0 -o /tmp/scan
python3 generate_report.py /tmp/scan
```

**Expected Outputs:**
- network_report.html (comprehensive HTML report)
- network_report.md (markdown summary)
- discovery_results.json (raw device data)
- connectivity_results.json (test results)
- dhcp_dns_results.json (DHCP/DNS analysis)

---

## Workflow 2: Internet Connectivity Troubleshooting

**Goal:** Diagnose why customers cannot access the internet

**Steps:**
1. Test gateway reachability
2. Test DNS resolution
3. Ping external IPs (8.8.8.8, 1.1.1.1)
4. Run traceroute to identify bottlenecks
5. Check for firewall/proxy issues

**Script:**
```bash
python3 connectivity_test.py -o /tmp/connectivity-check
```

**Common Issues & Solutions:**
- **Gateway unreachable:** Check physical connection, verify gateway IP, check routing table
- **DNS fails but IP works:** DNS server misconfiguration, update /etc/resolv.conf
- **Traceroute stops at router:** Firewall blocking, routing issue, ISP problem
- **High latency:** Network congestion, bandwidth limitation, check with bandwidth test

---

## Workflow 3: DHCP Problems

**Goal:** Identify and fix DHCP issues

**Steps:**
1. Detect all DHCP servers on network
2. Identify rogue DHCP servers
3. Check DHCP lease conflicts
4. Validate DHCP server configuration

**Script:**
```bash
sudo python3 dhcp_dns_troubleshoot.py -i eth0 -o /tmp/dhcp-check
```

**Common Issues:**
- **Multiple DHCP servers:** Disable rogue server, isolate device
- **No DHCP server:** Check DHCP service status, verify server reachability
- **IP conflicts:** Clear DHCP leases, check for static IPs in DHCP range
- **Wrong gateway/DNS from DHCP:** Update DHCP server configuration

---

## Workflow 4: DNS Troubleshooting

**Goal:** Fix DNS resolution issues

**Steps:**
1. Check DNS server configuration
2. Test each configured DNS server
3. Verify forward/reverse lookups
4. Check for split DNS
5. Test with alternative DNS (8.8.8.8, 1.1.1.1)

**Script:**
```bash
python3 dhcp_dns_troubleshoot.py -i eth0 -o /tmp/dns-check

# Manual DNS tests
nslookup google.com
dig google.com @8.8.8.8
host google.com
```

**Common Issues:**
- **DNS timeout:** DNS server down, firewall blocking port 53
- **Wrong DNS results:** DNS cache poisoning, incorrect DNS server
- **Intermittent failures:** DNS server overloaded, network instability

---

## Workflow 5: Wireless Network Assessment

**Goal:** Analyze wireless network health and security

**Steps:**
1. Scan for all wireless networks
2. Identify channel overlap
3. Check signal strength
4. Verify encryption/security
5. Identify rogue access points

**Script:**
```bash
sudo python3 wireless_assessment.py -i wlan0 -o /tmp/wireless-check
```

**Best Practices:**
- Use channels 1, 6, 11 for 2.4GHz (non-overlapping)
- Enable WPA2/WPA3 encryption
- Hidden SSIDs don't improve security
- Disable WPS if not needed
- Regular security audits

---

## Workflow 6: Port Security Audit

**Goal:** Identify security vulnerabilities and unnecessary open ports

**Steps:**
1. Scan all ports on critical hosts
2. Identify vulnerable services
3. Check service versions
4. Generate security recommendations

**Script:**
```bash
# Quick scan (common ports)
sudo python3 port_security_audit.py 192.168.1.0/24 -p 1-1000 -o /tmp/security-audit

# Full scan (all ports - takes longer)
sudo python3 port_security_audit.py 192.168.1.1 -p 1-65535 -o /tmp/full-scan
```

**High-Risk Services to Look For:**
- FTP (21), Telnet (23) - Replace with SSH
- SMB (445), NetBIOS (139) - Restrict access
- VNC (5900) - Use strong passwords, SSH tunnel
- Databases (3306, 5432, 27017) - Bind to localhost
- RDP (3389) - Use NLA, restrict access

---

## Workflow 7: SSL/TLS Certificate Validation

**Goal:** Ensure SSL certificates are valid and not expiring

**Steps:**
1. Scan network for SSL services
2. Check certificate validity
3. Verify expiration dates
4. Test TLS versions
5. Alert on expiring certificates

**Script:**
```bash
# Single host
python3 ssl_validator.py -H example.com -o /tmp/ssl-check

# Network scan
sudo python3 ssl_validator.py -n 192.168.1.0/24 -o /tmp/ssl-scan
```

**Common Issues:**
- **Expired certificates:** Renew immediately
- **Self-signed certificates:** Replace with valid CA-signed cert
- **Weak TLS versions:** Disable TLSv1.0, TLSv1.1
- **Certificate name mismatch:** Update certificate SAN

---

## Workflow 8: SNMP Device Monitoring

**Goal:** Monitor network device health and performance

**Steps:**
1. Identify SNMP-enabled devices
2. Query system information
3. Check interface statistics
4. Monitor CPU/memory usage
5. Alert on high error rates

**Script:**
```bash
# Single device
python3 snmp_monitor.py -H 192.168.1.1 -c public -o /tmp/snmp-check

# Multiple devices
python3 snmp_monitor.py -f devices.txt -c public -o /tmp/snmp-monitor
```

**What to Monitor:**
- Interface errors (>1000 = investigate)
- CPU usage (>80% = performance issue)
- Memory usage (>85% = memory pressure)
- Interface status (up/down)
- System uptime

---

## Workflow 9: Network Performance Testing

**Goal:** Measure and troubleshoot network performance

**Steps:**
1. Test bandwidth (upload/download)
2. Measure latency to key destinations
3. Check for packet loss
4. Identify bottlenecks with traceroute

**Script:**
```bash
python3 connectivity_test.py -b -o /tmp/performance-test

# Additional tools
speedtest-cli --simple
iperf3 -c server_ip
ping -c 100 8.8.8.8 | tail -n 5
```

**Performance Benchmarks:**
- **Latency:** <50ms good, >100ms investigate
- **Packet loss:** 0% ideal, >2% problematic
- **Jitter:** <10ms good for VoIP
- **Bandwidth:** Should match ISP plan

---

## Workflow 10: Topology Mapping

**Goal:** Create accurate network topology map

**Steps:**
1. Discover all devices
2. Identify device types (router, switch, AP, etc.)
3. Map connections between devices
4. Document VLANs and subnets
5. Generate topology diagram

**Script:**
```bash
sudo python3 network_discovery.py 192.168.1.0/24 -o /tmp/topology
sudo python3 snmp_monitor.py -f discovered_devices.txt -o /tmp/topology

# Generate visual diagram (requires additional tools)
# Use nmap output with zenmap or network topology mapper
```

**Documentation to Capture:**
- IP addressing scheme
- VLAN assignments
- Gateway/router locations
- Switch port mappings
- Wireless AP placement

---

## Quick Reference: Common Commands

### Network Discovery
```bash
# ARP scan (fast, local subnet only)
sudo arp-scan -l

# Nmap ping sweep
nmap -sn 192.168.1.0/24

# Netdiscover
sudo netdiscover -r 192.168.1.0/24
```

### Connectivity Testing
```bash
# Ping gateway
ping -c 5 192.168.1.1

# Ping DNS
ping -c 5 8.8.8.8

# Traceroute
traceroute 8.8.8.8

# DNS lookup
nslookup google.com
dig google.com
```

### Interface Information
```bash
# Show interfaces
ip addr show
ifconfig

# Show routing table
ip route show
route -n

# Show DNS configuration
cat /etc/resolv.conf
```

### Port Scanning
```bash
# Quick scan
nmap -F 192.168.1.1

# Service detection
nmap -sV 192.168.1.1

# OS detection
sudo nmap -O 192.168.1.1
```

### Wireless
```bash
# Show wireless interfaces
iwconfig

# Scan networks
sudo iwlist wlan0 scan

# Show current connection
nmcli device show wlan0
```

---

## Troubleshooting Decision Tree

```
Can't access internet?
├─ Can ping gateway? (ping 192.168.1.1)
│  ├─ YES: Gateway is reachable
│  │  └─ Can ping 8.8.8.8?
│  │     ├─ YES: DNS issue, check /etc/resolv.conf
│  │     └─ NO: Routing/firewall issue, check routing table
│  └─ NO: Gateway unreachable
│     └─ Check: physical connection, IP configuration, gateway IP
│
Slow network performance?
├─ Run bandwidth test
├─ Check for packet loss (ping)
├─ Run traceroute to find bottleneck
└─ Check interface errors (SNMP or ifconfig)
│
DHCP not working?
├─ Run DHCP server detection
├─ Check for multiple DHCP servers
└─ Verify DHCP service is running
│
DNS not resolving?
├─ Test with alternative DNS (8.8.8.8)
├─ Check /etc/resolv.conf
└─ Verify DNS server reachability
```

---

## Emergency Troubleshooting Checklist

**Network Down (Critical)**
- [ ] Check physical connections
- [ ] Verify power to network devices
- [ ] Check gateway reachability
- [ ] Verify DHCP service
- [ ] Check for IP conflicts
- [ ] Review recent changes

**Internet Access Issues**
- [ ] Ping gateway
- [ ] Ping external IP (8.8.8.8)
- [ ] Test DNS resolution
- [ ] Run traceroute
- [ ] Check ISP status
- [ ] Verify firewall rules

**Performance Issues**
- [ ] Run bandwidth test
- [ ] Check for packet loss
- [ ] Monitor interface errors
- [ ] Check CPU/memory on network devices
- [ ] Look for broadcast storms
- [ ] Check for network loops

**Security Incident**
- [ ] Isolate affected systems
- [ ] Run port security audit
- [ ] Check for rogue DHCP
- [ ] Scan for unknown devices
- [ ] Review firewall logs
- [ ] Change passwords

---

This reference guide provides the foundation for systematic network troubleshooting. Combine with the automation scripts for efficient problem resolution.
