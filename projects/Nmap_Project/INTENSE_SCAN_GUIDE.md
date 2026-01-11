# Zenmap Intense Scan - Quick Reference

## What is the Intense Scan?

The **Intense Scan** is Zenmap's most comprehensive scan profile. It runs:

```bash
nmap -T4 -A -v <target>
```

### What Each Flag Does:

- **-T4**: Aggressive timing (faster scans, assumes good network)
- **-A**: Enables multiple advanced features:
  - OS detection (`-O`)
  - Version detection (`-sV`)
  - Script scanning (`-sC` - runs default NSE scripts)
  - Traceroute (`--traceroute`)
- **-v**: Verbose output (shows progress and extra details)

This is the most thorough single scan for understanding a network.

---

## 3 Ways to Run Intense Scan

### Option 1: Through Claude (Easiest)

Once your MCP server is running, just talk to Claude:

```
You: "Run an intense scan on 192.168.1.0/24"
Claude: [Executes nmap -T4 -A -v and shows results]
```

Or more specifically:
```
You: "Run a Zenmap intense scan on 192.168.1.0/24, exclude 192.168.1.1"
```

### Option 2: Standalone Script

```bash
# Inside the container
docker exec -it kali-network-discovery /bin/bash
cd /scans
./intense-scan.sh 192.168.1.0/24

# With exclusions
./intense-scan.sh 192.168.1.0/24 exclude.txt
```

### Option 3: Direct Command

```bash
# From your host
docker exec kali-network-discovery nmap -T4 -A -v 192.168.1.0/24 -oA /scans/intense_scan
```

---

## What You'll Get

The intense scan provides:

### 1. **Live Hosts**
All active devices on the network

### 2. **Open Ports**
Every open TCP port on each host

### 3. **Service Versions**
Exact versions of running services:
- "Apache httpd 2.4.41"
- "OpenSSH 8.2p1"
- "Microsoft Windows RPC"

### 4. **Operating Systems**
OS fingerprinting:
- "Linux 3.10 - 4.11"
- "Microsoft Windows 10"
- "Cisco IOS 12.4"

### 5. **Script Results**
Default NSE scripts provide:
- SSL/TLS certificate details
- SMB information
- HTTP titles and headers
- DNS information
- And much more...

### 6. **Traceroute**
Network path to each host

---

## Example Output

```
Starting Nmap 7.94 ( https://nmap.org )
Nmap scan report for 192.168.1.1
Host is up (0.0010s latency).
Not shown: 995 closed ports
PORT     STATE SERVICE    VERSION
22/tcp   open  ssh        OpenSSH 8.2p1 Ubuntu 4ubuntu0.5
80/tcp   open  http       Apache httpd 2.4.41
443/tcp  open  ssl/http   Apache httpd 2.4.41
3306/tcp open  mysql      MySQL 5.7.40
8080/tcp open  http-proxy Squid http proxy 4.10

OS details: Linux 3.10 - 4.11
Network Distance: 1 hop

TRACEROUTE
HOP RTT     ADDRESS
1   1.00 ms 192.168.1.1

Nmap done: 1 IP address (1 host up) scanned in 45.23 seconds
```

---

## Best Practices

### ✅ DO:
- Get written authorization before scanning
- Run during maintenance windows
- Start with smaller subnets to test
- Review exclude.txt before scanning
- Document all findings

### ⚠️ DON'T:
- Scan without permission
- Scan production systems during peak hours
- Ignore warnings or errors
- Share scan results insecurely

---

## Timing Considerations

The intense scan is **thorough but time-consuming**:

- **Single host**: 1-5 minutes
- **/24 subnet** (254 hosts): 30 minutes - 2 hours
- **/16 subnet** (65,534 hosts): Many hours to days

For large networks, consider:
1. Start with ping sweep to find live hosts
2. Then run intense scan only on live hosts
3. Or break into smaller chunks

---

## Excluding Sensitive Systems

Always exclude critical production systems:

**Create exclude.txt:**
```
192.168.1.1      # Production router
192.168.1.10     # Database server
192.168.1.50     # Domain controller
10.0.0.0/24      # Management network
```

**Use it:**
```bash
./intense-scan.sh 192.168.1.0/24 /scans/exclude.txt
```

Or tell Claude:
```
"Run intense scan on 192.168.1.0/24, but exclude 192.168.1.1 and 192.168.1.10"
```

---

## Understanding Results

### Port States:
- **open** - Service is accepting connections
- **closed** - Port is accessible but no service listening
- **filtered** - Port blocked by firewall

### Service Detection Confidence:
Look for numbers like `(95%)` - higher is more confident

### OS Detection:
May show multiple possibilities with confidence percentages

---

## Comparison to Other Scans

| Scan Type | Speed | Detail | Use Case |
|-----------|-------|--------|----------|
| Ping Sweep | ⚡⚡⚡ | ⭐ | Quick host discovery |
| Fast Scan (-F) | ⚡⚡ | ⭐⭐ | Top 1000 ports |
| **Intense Scan** | ⚡ | ⭐⭐⭐⭐⭐ | Complete analysis |
| Comprehensive | ⚡ | ⭐⭐⭐⭐⭐ | All ports + scripts |

---

## Common Questions

**Q: How long will it take?**
A: Depends on network size. A /24 usually takes 30-60 minutes.

**Q: Will it be detected?**
A: Yes, -T4 is fairly aggressive. Use -T2 for stealth if needed.

**Q: Can I run it on larger networks?**
A: Yes, but consider breaking into chunks or using faster discovery first.

**Q: What if it gets stuck?**
A: Press Ctrl+C to stop. Check firewall rules and network connectivity.

---

## Advanced Options

### Adjust Timing:
```bash
# Slower, stealthier
nmap -T2 -A -v 192.168.1.0/24

# Even faster (not recommended)
nmap -T5 -A -v 192.168.1.0/24
```

### Limit to Specific Hosts:
```bash
# Only scan specific IPs
nmap -T4 -A -v 192.168.1.10,192.168.1.20,192.168.1.30
```

### Save to Specific File:
```bash
nmap -T4 -A -v 192.168.1.0/24 -oA /scans/customer_intense_scan
```

---

## Getting Help

- **Nmap docs**: https://nmap.org/book/man.html
- **NSE scripts**: https://nmap.org/nsedoc/
- **Inside container**: `man nmap`

---

**Ready to scan?** Just tell Claude: "Run an intense scan on [your network]" 🚀
