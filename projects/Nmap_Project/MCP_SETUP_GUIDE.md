# Nmap MCP Server Setup Guide

This setup allows Claude to run nmap network discovery commands remotely on your customer's network through the Model Context Protocol (MCP).

## Architecture

```
Customer Network → Kali Docker Container → MCP Server → Claude Desktop/API
```

Claude can now interact with nmap through natural language, making network discovery much easier!

## Prerequisites

1. Docker and Docker Compose installed
2. Claude Desktop app (or API access with MCP support)
3. Network access to customer's network from the container

## Installation Steps

### 1. Build and Deploy the Container

```bash
# Build the container with MCP server
docker-compose build

# Start the container
docker-compose up -d

# Verify it's running
docker ps | grep kali-network-discovery
```

### 2. Configure Claude Desktop

Add the MCP server to your Claude Desktop configuration:

**Location of config file:**
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

**Add this to your config:**

```json
{
  "mcpServers": {
    "nmap-network-discovery": {
      "command": "docker",
      "args": [
        "exec",
        "-i",
        "kali-network-discovery",
        "python3",
        "/usr/local/bin/mcp-nmap-server"
      ]
    }
  }
}
```

### 3. Restart Claude Desktop

Close and reopen Claude Desktop app. You should see the MCP server connected in the status bar or settings.

## Available Tools

Once connected, Claude can use these nmap tools:

### 1. **nmap_ping_sweep**
Discover live hosts on the network
```
Example: "Run a ping sweep on 192.168.1.0/24"
```

### 2. **nmap_port_scan**
Scan ports on target hosts
```
Example: "Scan ports 80,443,22 on 192.168.1.0/24"
Example: "Do a fast port scan on 10.0.0.5"
```

### 3. **nmap_service_detection**
Detect services and versions
```
Example: "Detect services running on 192.168.1.10"
```

### 4. **nmap_os_detection**
Identify operating systems
```
Example: "What OS is running on 192.168.1.1?"
```

### 5. **nmap_comprehensive_scan**
Full infrastructure analysis
```
Example: "Run a comprehensive scan on 192.168.1.0/24"
```

### 6. **nmap_custom_command**
Advanced custom nmap commands
```
Example: "Run nmap with arguments: -sS -p- -T4 192.168.1.10"
```

### 7. **get_scan_results**
Retrieve previous scan results
```
Example: "Show me the results from scan ping_sweep_20241110_143022"
```

### 8. **list_scan_history**
View all previous scans
```
Example: "What scans have been run?"
```

## Usage Examples

Once configured, just talk to Claude naturally:

### Example 1: Basic Network Discovery
**You:** "I need to discover all live hosts on the 192.168.1.0/24 network"

**Claude will:**
1. Run nmap_ping_sweep tool
2. Parse and present the results
3. Show you which hosts are up

### Example 2: Infrastructure Planning
**You:** "I'm planning new infrastructure on 10.0.0.0/24. Can you help me understand what's already there?"

**Claude will:**
1. Run comprehensive scans
2. Identify existing services
3. Find available IP ranges
4. Suggest placement for new infrastructure

### Example 3: Service Inventory
**You:** "What web servers are running on the 172.16.0.0/16 network?"

**Claude will:**
1. Scan for ports 80, 443, 8080
2. Detect service versions
3. Provide a summary of findings

### Example 4: Follow-up Analysis
**You:** "Show me all the scans we've run today"

**Claude will:**
1. List scan history
2. Retrieve specific results
3. Help you analyze findings

## Remote Deployment Scenarios

### Scenario 1: On-Site Container
Deploy container directly on customer's network:
```bash
# On customer's network machine
docker-compose up -d

# From your machine with Claude Desktop
# MCP connects through Docker
```

### Scenario 2: SSH Tunnel
Run container on remote site, connect via SSH:
```bash
# SSH to customer network
ssh user@customer-network

# Start container
docker-compose up -d

# In your MCP config, use SSH:
{
  "command": "ssh",
  "args": [
    "user@customer-network",
    "docker", "exec", "-i", "kali-network-discovery",
    "python3", "/usr/local/bin/mcp-nmap-server"
  ]
}
```

### Scenario 3: VPN + Docker
Connect to customer VPN, then use Docker:
```bash
# Connect to customer VPN first
# Then use standard Docker MCP config
```

## Security Considerations

### 1. Authorization
- Always have written authorization before scanning
- Document the scope and timeframe
- Keep authorization documents with scan results

### 2. Exclusion Lists
Create `/scans/exclude.txt` with sensitive systems:
```
192.168.1.1      # Production router
192.168.1.10     # Database server
10.0.0.0/24      # Management network
```

### 3. Scan Timing
- Schedule during maintenance windows
- Use slower scan speeds (-T2 or -T3) during business hours
- Coordinate with customer's IT team

### 4. Data Handling
- All scan results stored in `/scans` directory
- Encrypted storage recommended
- Secure deletion after project completion

### 5. Network Impact
- Start with gentle scans (ping sweep)
- Gradually increase intensity
- Monitor for any network issues

## Troubleshooting

### MCP Server Not Connecting

**Check if container is running:**
```bash
docker ps | grep kali-network-discovery
```

**Check MCP server inside container:**
```bash
docker exec -it kali-network-discovery python3 /usr/local/bin/mcp-nmap-server
# Should wait for input (Ctrl+C to exit)
```

**Check Claude Desktop logs:**
- macOS: `~/Library/Logs/Claude/`
- Windows: `%APPDATA%\Claude\logs\`
- Linux: `~/.config/Claude/logs/`

### Permission Errors

Ensure container has necessary privileges:
```yaml
# In docker-compose.yml
privileged: true
cap_add:
  - NET_ADMIN
  - NET_RAW
```

### Nmap Not Found

Rebuild container:
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Scans Timing Out

Increase timeout in MCP server:
```python
# In mcp_nmap_server.py
timeout=7200  # 2 hours instead of 1
```

## Advanced Features

### Custom Scan Profiles

You can add custom scan profiles by modifying the MCP server. For example:

**Quick Infrastructure Assessment:**
```python
# Add to mcp_nmap_server.py
@server.list_tools()
async def handle_list_tools():
    tools.append(types.Tool(
        name="infrastructure_assessment",
        description="Quick assessment for infrastructure planning",
        # ... implementation
    ))
```

### Automated Reporting

Create automated reports from scan results:
```bash
# Inside container
docker exec kali-network-discovery /bin/bash -c "
  python3 << 'EOF'
import glob
import json

scans = glob.glob('/scans/*.gnmap')
# Parse and generate report
EOF
"
```

### Integration with IPAM

Export scan results to your IPAM system:
```bash
# Export to CSV
docker exec kali-network-discovery nmap 192.168.1.0/24 -oG - | \
  awk '/Up$/{print $2}' > active_hosts.csv
```

## Maintenance

### View Scan History
```bash
docker exec kali-network-discovery ls -lh /scans/
```

### Cleanup Old Scans
```bash
# Remove scans older than 30 days
docker exec kali-network-discovery find /scans -name "*.nmap" -mtime +30 -delete
```

### Backup Scan Results
```bash
# Copy scans to host
docker cp kali-network-discovery:/scans ./scan-backups/
```

### Update Container
```bash
docker-compose down
docker-compose pull
docker-compose build
docker-compose up -d
```

## Example Workflow

### Complete Network Discovery Process

1. **Initial Discovery**
   ```
   You: "I need to assess the 192.168.1.0/24 network for new infrastructure"
   Claude: [Runs ping sweep, presents live hosts]
   ```

2. **Service Identification**
   ```
   You: "What services are running on these hosts?"
   Claude: [Runs service detection, lists all services]
   ```

3. **Infrastructure Planning**
   ```
   You: "Based on these results, where should I place my new web server cluster?"
   Claude: [Analyzes results, suggests available IPs and configuration]
   ```

4. **Documentation**
   ```
   You: "Create a summary report of all findings"
   Claude: [Compiles scan results into comprehensive report]
   ```

## Benefits of MCP Integration

✅ **Natural Language Interface** - No need to remember nmap syntax
✅ **Automated Workflows** - Claude can chain multiple scans intelligently
✅ **Contextual Analysis** - Claude understands your infrastructure goals
✅ **Report Generation** - Automatic documentation of findings
✅ **Safety Features** - Claude helps avoid scanning sensitive systems
✅ **Remote Access** - Control scans from anywhere through Claude

## Next Steps

1. Build and start the container
2. Configure Claude Desktop with MCP server
3. Test connection with a simple ping sweep
4. Run your first network discovery
5. Review scan results and plan infrastructure

## Support and Documentation

- MCP Documentation: https://modelcontextprotocol.io
- Nmap Reference: https://nmap.org/book/man.html
- Docker Documentation: https://docs.docker.com

## License and Legal

- Always obtain written authorization before scanning networks
- Comply with all local laws and regulations
- Use responsibly and ethically
- Document all scanning activities

---

**Ready to start?** Build the container and configure Claude Desktop, then just start chatting with Claude about your network discovery needs!
