# Example Workflow: Basic Network Troubleshooting

**Document Information:**
- Department: IT
- Created: 2025-01-15
- Last Updated: 2025-01-15
- Owner: Network Team
- Related Docs: [[network-discovery]], [[connectivity-testing]]

## Overview
This workflow demonstrates the basic structure for documenting troubleshooting procedures. Use this as a template for creating your own workflow documentation.

## Prerequisites
- Network access to target device
- Administrative credentials
- Basic understanding of TCP/IP networking
- Tools: ping, traceroute, nslookup

## Steps

### Step 1: Verify Physical Connectivity
![Check physical connection](../screenshots/example-workflow/step1-physical.png)

**What to do:**
1. Check that network cables are properly connected
2. Verify link lights are active on network interface
3. Check that device is powered on
4. Confirm no obvious physical damage to cables

**Notes:**
- Green link light = good connection
- Amber/orange light may indicate speed/duplex mismatch
- No light = check cable, port, or power

### Step 2: Test Local Network Connectivity
![Ping local gateway](../screenshots/example-workflow/step2-ping-gateway.png)

**What to do:**
1. Open command prompt or terminal
2. Identify default gateway: `ip route` (Linux) or `ipconfig` (Windows)
3. Ping the gateway: `ping 192.168.1.1`
4. Verify successful responses with low latency (<5ms typical)

**Notes:**
- 100% packet loss = no local connectivity
- High latency (>50ms) may indicate network congestion
- "Destination Host Unreachable" = routing issue

### Step 3: Test Internet Connectivity
![Test external connectivity](../screenshots/example-workflow/step3-internet.png)

**What to do:**
1. Ping reliable external host: `ping 8.8.8.8`
2. Verify DNS resolution: `nslookup google.com`
3. Test HTTP/HTTPS: Open web browser and navigate to https://google.com

**Notes:**
- Can ping IP but not resolve names = DNS issue
- Can't ping external IPs = gateway/firewall issue
- Can resolve DNS but web doesn't load = proxy/firewall blocking HTTP/HTTPS

### Step 4: Perform Traceroute Analysis
![Traceroute to destination](../screenshots/example-workflow/step4-traceroute.png)

**What to do:**
1. Run traceroute to problem destination: `traceroute google.com`
2. Identify where packets are failing (timeout or high latency)
3. Note the last successful hop
4. Check if failure is internal network or ISP

**Notes:**
- Failure at hop 1-3 = local network issue
- Failure after ISP gateway = provider issue
- Gradual latency increase = congestion

## Verification

Successful troubleshooting results in:
- ✅ Physical connectivity confirmed (link lights active)
- ✅ Local gateway pingable with <5ms latency
- ✅ External IPs reachable (8.8.8.8, 1.1.1.1)
- ✅ DNS resolution working
- ✅ Web browsing functional

## Troubleshooting

**Issue: Can't ping gateway**
- Check IP configuration: `ip addr` or `ipconfig`
- Verify correct subnet
- Check for DHCP issues (no IP address assigned)
- Test with static IP configuration

**Issue: Can reach gateway but not internet**
- Verify gateway configuration
- Check firewall rules
- Confirm ISP connection active
- Test from different device to isolate problem

**Issue: DNS not resolving**
- Check DNS server configuration: `cat /etc/resolv.conf`
- Try alternate DNS: `nslookup google.com 8.8.8.8`
- Flush DNS cache: `ipconfig /flushdns` (Windows)
- Verify firewall allows DNS (port 53)

## Related Resources
- [[network-discovery]] - Full network discovery procedures
- [[connectivity-test]] - Advanced connectivity testing
- [TCP/IP Fundamentals](https://example.com)
- [Network Troubleshooting Guide](https://example.com)

---

## About This Example

This is a demonstration workflow showing the standard documentation format. When you use the workflow recorder:

1. **Screenshots** are automatically captured and numbered
2. **Directory structure** is created automatically
3. **Markdown template** is generated with your steps

You'll then:
1. Edit the generated Markdown to add descriptions
2. Fill in the Overview, Prerequisites, and Troubleshooting sections
3. Export to PDF/HTML for distribution

### To Create Your Own Workflow:

```bash
# Start the recorder
cd tools
python3 workflow-recorder.py --name "your-workflow-name" --department "IT"

# During your process:
# - Press F9 when you complete each step
# - Add step title and description when prompted
# - Press F10 to add notes
# - Press ESC when done

# Edit the generated file
vim documentation/workflows/your-workflow-name.md

# Export to PDF
python3 export-workflow.py --input documentation/workflows/your-workflow-name.md --format pdf
```

**Note:** Since this is an example, the screenshot paths reference non-existent images. When you record a real workflow, the recorder will create actual screenshots in the correct locations.
