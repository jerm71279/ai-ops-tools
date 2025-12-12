# Network Troubleshooter Skill - Complete Package

## What You've Got

I've built you a **comprehensive network troubleshooting and assessment skill** with all 10 industry-standard use cases. This is a complete, production-ready toolkit for IT network diagnostics.

## 📦 Package Contents

Your skill includes **10 Python scripts** covering:

1. ✅ **Network Discovery** (`network_discovery.py`) - Find all devices using ARP, nmap, netdiscover
2. ✅ **Connectivity Testing** (`connectivity_test.py`) - Gateway, internet, DNS, traceroute, bandwidth
3. ✅ **DHCP/DNS Troubleshooting** (`dhcp_dns_troubleshoot.py`) - Rogue DHCP detection, DNS validation
4. ✅ **SSL/TLS Certificate Validation** (`ssl_validator.py`) - Certificate expiry, chain validation
5. ✅ **DNS Health Checks** - Forward/reverse lookups, split DNS detection (in dhcp_dns_troubleshoot.py)
6. ✅ **SNMP Monitoring** (`snmp_monitor.py`) - Device health, interface stats, CPU/memory
7. ✅ **Wireless Assessment** (`wireless_assessment.py`) - Signal strength, channel overlap, security
8. ✅ **Network Performance** - Bandwidth testing (in connectivity_test.py)
9. ✅ **Port Security Audit** (`port_security_audit.py`) - Vulnerability scanning, risk assessment
10. ✅ **Report Generation** (`generate_report.py`) - HTML + Markdown reports

**PLUS** a main orchestration script (`run_assessment.py`) that runs everything automatically!

## 🚀 Quick Start

### Upload the Skill to Claude

1. Download the skill file: `network-troubleshooter.skill`
2. In Claude, go to your profile → "Add Skills"
3. Upload `network-troubleshooter.skill`
4. The skill is now available for use!

### Using the Skill

Once uploaded, you can ask Claude things like:

- "Scan the 192.168.1.0/24 network and create a pre-installation report"
- "Troubleshoot why customers can't access the internet on 10.0.0.0/24"
- "Run a security audit on 192.168.10.0/24 and identify vulnerabilities"
- "Check for rogue DHCP servers on the network"
- "Scan for wireless networks and check for security issues"
- "Monitor SNMP devices at 192.168.1.1 and 192.168.1.2"

Claude will automatically:
- Use the appropriate scripts from the skill
- Run the network assessments
- Generate comprehensive reports
- Provide findings and recommendations

## 🔧 For USB Bootable Deployment

Your questionnaire mentioned creating a bootable USB tool. Here's how:

### Option 1: Linux Live USB (Recommended)

1. **Create Ubuntu Live USB:**
   ```bash
   # Download Ubuntu 22.04/24.04
   # Use Rufus (Windows) or dd (Linux) to create bootable USB
   ```

2. **Customize the Live Environment:**
   - Boot from USB in "Try Ubuntu" mode
   - Install all required tools:
     ```bash
     sudo apt-get update
     sudo apt-get install nmap arp-scan traceroute python3-pip \
                          speedtest-cli netdiscover snmp wireless-tools
     pip3 install dnspython --break-system-packages
     ```

3. **Extract and Install Scripts:**
   - Unzip `network-troubleshooter.skill` (it's just a ZIP file)
   - Copy all scripts to `/opt/network-troubleshooter/`
   - Make executable: `chmod +x /opt/network-troubleshooter/scripts/*.py`

4. **Create Auto-Run Script:**
   - Create `/opt/auto-assess.sh` with:
   ```bash
   #!/bin/bash
   NETWORK=$(ip route | grep -v default | awk '{print $1}' | head -n 1)
   cd /opt/network-troubleshooter/scripts
   sudo python3 run_assessment.py "$NETWORK" -o "/media/usb/reports/$(date +%Y%m%d_%H%M%S)"
   ```

5. **Make Persistent:**
   - Use Rufus with persistence option, OR
   - Use `mkusb` to create persistent Ubuntu USB, OR
   - Remaster the ISO with scripts pre-installed

### Option 2: Raspberry Pi USB Device

- Install Raspberry Pi OS on USB
- Install all tools and scripts
- Configure to auto-run on boot
- Plug into customer's network via Ethernet

## 📊 What the Reports Include

The HTML and Markdown reports contain:

### Executive Summary
- Total devices discovered
- Critical issues count
- Warnings and recommendations

### Network Discovery Section
- Device inventory table (IP, MAC, Vendor)
- Device types and services
- Network topology information

### Connectivity Tests
- Gateway reachability (with ping stats)
- Internet connectivity (8.8.8.8, 1.1.1.1, google.com)
- DNS resolution tests
- Traceroute results

### DHCP/DNS Analysis
- DHCP server detection (with rogue server warnings)
- DNS server configuration
- DNS resolution health
- Split DNS detection

### Security Findings
- Open ports and services
- Vulnerable services identified
- Risk scores (Critical/High/Medium/Low)
- Security recommendations

### Recommendations
- Prioritized action items
- Configuration suggestions
- Best practice guidance

## 💡 Real-World Usage Examples

### Scenario 1: Pre-Installation Check
```
Customer: "I have a new customer install tomorrow at 192.168.50.0/24. 
           Need a full network assessment."

You: "Run a complete pre-installation assessment on 192.168.50.0/24"

Claude: [Runs full assessment, generates report]
        - Finds 47 devices
        - Detects rogue DHCP server at 192.168.50.45
        - Identifies static IPs on native VLAN
        - Creates comprehensive HTML report
```

### Scenario 2: Internet Issues
```
Customer: "Users at 10.50.0.0/24 can't access the internet"

You: "Troubleshoot internet connectivity for 10.50.0.0/24"

Claude: [Runs connectivity tests]
        - Gateway reachable ✓
        - DNS failing ✗
        - Issue: DNS server 10.50.0.1 is down
        - Recommendation: Update DNS to 8.8.8.8 or fix internal DNS
```

### Scenario 3: Security Audit
```
You: "Run a security audit on 192.168.1.0/24 and identify vulnerabilities"

Claude: [Runs port security audit]
        - Found FTP on 192.168.1.10 (HIGH RISK)
        - Found Telnet on 192.168.1.15 (HIGH RISK)
        - Found open MongoDB on 192.168.1.25 (CRITICAL)
        - Recommendations: Disable insecure services, use SSH
```

## 🎯 Key Features

**Comprehensive Coverage:**
- All 10 top IT troubleshooting use cases included
- Pre-installation, troubleshooting, security, monitoring

**Automated Reporting:**
- Beautiful HTML reports (open in browser)
- Markdown reports (easy to share)
- JSON data files for automation

**Modular Design:**
- Run full assessment or individual tools
- Each script works standalone
- Easy to customize and extend

**Production Ready:**
- Error handling and timeouts
- Detailed logging
- Validates dependencies
- Works on Debian/Ubuntu/Kali

**Flexible Deployment:**
- Use via Claude interface
- Deploy on USB bootable
- Install as NinjaOne agent
- Run as cron jobs

## 📁 File Structure

```
network-troubleshooter.skill/
├── SKILL.md                              # Main skill documentation
├── scripts/
│   ├── run_assessment.py                 # Main orchestrator
│   ├── network_discovery.py              # Device discovery
│   ├── connectivity_test.py              # Connectivity testing
│   ├── dhcp_dns_troubleshoot.py          # DHCP/DNS diagnostics
│   ├── ssl_validator.py                  # SSL/TLS validation
│   ├── snmp_monitor.py                   # SNMP monitoring
│   ├── wireless_assessment.py            # Wireless assessment
│   ├── port_security_audit.py            # Security auditing
│   └── generate_report.py                # Report generation
└── references/
    └── troubleshooting_workflows.md      # Detailed workflows & guides
```

## 🔒 Permissions Note

Most network scanning requires **root privileges**. All scripts that need it are designed to work with `sudo`.

## 🆘 Support & Troubleshooting

**If you get "command not found" errors:**
Install missing tools:
```bash
sudo apt-get install nmap arp-scan traceroute python3-pip
```

**If you get "permission denied":**
Run with sudo:
```bash
sudo python3 run_assessment.py 192.168.1.0/24
```

**To test the skill before deploying:**
1. Extract the .skill file (it's a ZIP)
2. Run any script manually to test
3. Check output in `/tmp/network-scan-*/`

## 🎁 Bonus: Integration Ideas

**NinjaOne Integration:**
- Deploy scripts on endpoints
- Schedule daily/weekly assessments
- Alert on critical findings
- Track network changes over time

**Automation:**
```bash
# Daily health check
0 2 * * * /opt/network-troubleshooter/scripts/run_assessment.py 192.168.1.0/24 -q

# Weekly security audit
0 3 * * 0 /opt/network-troubleshooter/scripts/port_security_audit.py 192.168.1.0/24
```

**Teams Bot Integration:**
- User asks bot: "Scan network"
- Bot runs assessment via Claude
- Posts report link to Teams channel

## 🚀 Next Steps

1. **Upload the skill to Claude** - You're ready to use it immediately
2. **Test it** - Run a scan on your network to see it in action
3. **Customize** - Add your own scripts or modify existing ones
4. **Deploy** - Create your USB bootable or install as agent

## ✨ What Makes This Special

- **Complete toolkit** - Not just one or two scripts, but a full professional system
- **Production-ready** - Error handling, logging, proper output formatting
- **Well-documented** - Detailed workflows, decision trees, troubleshooting guides
- **Modular** - Use pieces individually or run complete assessments
- **Extensible** - Easy to add more scripts and customize
- **Professional reports** - Customer-ready HTML reports with branding

You now have a professional-grade network troubleshooting system that covers everything from pre-installation discovery to security audits!

---

**Questions or need modifications?** Just ask! The skill is fully customizable and ready to extend.
