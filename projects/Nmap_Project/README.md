# Kali Linux Network Discovery Container

Docker container with Kali Linux and nmap for network discovery before standing up new infrastructure.

## Prerequisites

- Docker installed
- Docker Compose installed (optional, but recommended)
- Proper authorization to scan the target networks

## Quick Start

### Build and Run with Docker Compose (Recommended)

```bash
# Build the container
docker-compose build

# Start the container
docker-compose up -d

# Access the container shell
docker-compose exec kali-nmap /bin/bash
```

### Build and Run with Docker

```bash
# Build the image
docker build -t kali-nmap .

# Run the container
docker run -it --rm --network host --privileged --cap-add=NET_ADMIN --cap-add=NET_RAW -v $(pwd)/scans:/scans kali-nmap
```

## Usage

### Option 1: Use the Automated Discovery Script

```bash
# Inside the container
chmod +x /scans/network-discovery.sh
/scans/network-discovery.sh 192.168.1.0/24
```

### Option 2: Manual nmap Commands

#### Quick Host Discovery
```bash
# Ping sweep - find live hosts
nmap -sn 192.168.1.0/24

# With output file
nmap -sn 192.168.1.0/24 -oA /scans/host-discovery
```

#### Port Scanning
```bash
# Fast scan - top 1000 ports
nmap -F 192.168.1.0/24

# Specific ports
nmap -p 80,443,22,3389 192.168.1.0/24

# All TCP ports (slower)
nmap -p- 192.168.1.0/24
```

#### Service and OS Detection
```bash
# Service version detection
nmap -sV 192.168.1.0/24

# OS detection (requires root/privileged)
nmap -O 192.168.1.0/24

# Comprehensive scan
nmap -sV -O -p- 192.168.1.0/24
```

#### Save Results
```bash
# Save in multiple formats
nmap -sV 192.168.1.0/24 -oA /scans/network-scan

# This creates:
# - network-scan.nmap (normal output)
# - network-scan.xml (XML format)
# - network-scan.gnmap (grepable format)
```

## Common Use Cases for Infrastructure Planning

### 1. Discover Available IP Addresses
```bash
nmap -sn -n 192.168.1.0/24 -oG - | grep "Status: Down" | awk '{print $2}'
```

### 2. Identify Existing DHCP/DNS Servers
```bash
nmap -sU -p 67,68,53 192.168.1.0/24
```

### 3. Find Network Devices (Routers, Switches)
```bash
nmap -p 22,23,80,443,8080 --script snmp-info 192.168.1.0/24
```

### 4. Map Subnet Usage
```bash
nmap -sn 10.0.0.0/8 --excludefile exclude.txt -oA /scans/subnet-map
```

## Excluding Hosts

Create an `exclude.txt` file in the `scans` directory:

```
# Production servers - do not scan
192.168.1.10
192.168.1.11
10.0.0.0/24
```

Then use with nmap:
```bash
nmap 192.168.1.0/24 --excludefile /scans/exclude.txt
```

## Output Files

All scans save to `/scans` directory which is mounted to `./scans` on your host.

Results include:
- `.nmap` - Human-readable output
- `.xml` - Machine-readable XML (import into other tools)
- `.gnmap` - Grep-friendly format

## Timing and Performance

Nmap timing templates (use with `-T` flag):
- `-T0` Paranoid (very slow, IDS evasion)
- `-T1` Sneaky (slow, IDS evasion)
- `-T2` Polite (slower, less bandwidth)
- `-T3` Normal (default)
- `-T4` Aggressive (faster, assumes good network)
- `-T5` Insane (very fast, may miss hosts)

For infrastructure discovery, `-T4` is usually appropriate.

## Network Modes

This container uses `--network host` mode which:
- Gives direct access to host network interfaces
- Required for accurate network scanning
- Allows the container to see the actual network topology

## Security Notes

1. **Authorization**: Only scan networks you own or have written permission to scan
2. **Documentation**: Keep records of scan authorization and scope
3. **Timing**: Schedule scans during maintenance windows when possible
4. **Exclusions**: Always exclude critical production systems
5. **Notification**: Inform relevant teams before scanning

## Troubleshooting

### Permission Denied Errors
Ensure container runs with `--privileged` and `--cap-add=NET_ADMIN,NET_RAW`

### Can't See Network
Verify `--network host` is used when running the container

### Slow Scans
- Use `-T4` for faster scanning
- Reduce scope to specific subnets
- Use `-F` for fast scan (top 1000 ports only)

## Stop and Cleanup

```bash
# Stop container
docker-compose down

# Remove container and image
docker-compose down --rmi all

# Clean up scan results (be careful!)
rm -rf scans/*
```

## Additional Tools Included

- `netdiscover` - Active/passive network discovery
- `masscan` - Fast port scanner
- `arp-scan` - ARP-based host discovery
- `tcpdump` - Packet capture and analysis

## Example Workflow for New Infrastructure

1. **Initial Discovery**
   ```bash
   ./network-discovery.sh 192.168.1.0/24
   ```

2. **Review Results**
   - Check `SUMMARY.txt` for overview
   - Review live hosts in `01_ping_sweep.nmap`
   - Identify services in `03_service_detection.nmap`

3. **Plan Infrastructure**
   - Document used IP ranges
   - Identify potential conflicts
   - Plan new IP allocations
   - Note existing services to avoid

4. **Document Findings**
   - Export XML to network management tools
   - Create network diagrams
   - Update IPAM systems
