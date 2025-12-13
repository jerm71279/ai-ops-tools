# UniFi Fleet Management Skill

## Overview
This skill enables natural language querying of OberaConnect's UniFi fleet data. The fleet consists of 98+ customer sites with 492+ devices managed through Ubiquiti's Site Manager.

## Data Schema

### Site Object Structure
```javascript
{
  // Identifiers
  id: string,              // Site UUID
  deviceId: string,        // Host device ID
  
  // Names
  name: string,            // Display name (e.g., "Setco Services - Corporate")
  internalName: string,    // System name
  
  // Location/Time
  timezone: string,        // e.g., "America/Chicago"
  
  // Device Counts
  totalDevices: number,    // Total UniFi devices at site
  offlineDevices: number,  // Devices currently offline
  onlineDevices: number,   // Devices currently online (derived)
  wifiDevices: number,     // Access points
  wiredDevices: number,    // Switches
  gatewayDevices: number,  // UDM/USG devices
  
  // Offline Breakdown
  offlineWifi: number,     // Offline APs
  offlineWired: number,    // Offline switches
  offlineGateway: number,  // Offline gateways (critical!)
  
  // Client Counts
  wifiClients: number,     // Wireless clients
  wiredClients: number,    // Wired clients
  totalClients: number,    // All connected clients
  guestClients: number,    // Guest network clients
  
  // Alerts
  criticalAlerts: number,  // Critical notifications
  warningAlerts: number,   // Warning notifications
  
  // Network Config
  ssidCount: number,       // Configured SSIDs
  vlanCount: number,       // Configured VLANs
  
  // WAN Details
  isp: string,             // Primary ISP name
  wanUptime: number,       // WAN uptime percentage (0-100)
  externalIp: string,      // Public IP address
  wans: [{                 // All WAN connections
    name: string,
    uptime: number,
    externalIp: string,
    isp: string
  }],
  
  // Performance Metrics
  txRetry: number,         // WiFi TX retry rate (%)
  satisfaction: number,    // Client satisfaction score
  
  // Computed Fields
  healthScore: number,     // 0-100 overall health
  isHealthy: boolean,      // No critical issues
  hasIssues: boolean,      // Has offline devices or alerts
  deviceOnlinePercent: number,  // % devices online
}
```

### Health Score Calculation
```javascript
healthScore = (
  (deviceOnlinePercent * 0.4) +    // 40% weight: device availability
  (wanUptime * 0.3) +               // 30% weight: WAN uptime
  ((100 - txRetry) * 0.15) +        // 15% weight: WiFi quality
  ((criticalAlerts === 0 ? 100 : 0) * 0.15)  // 15% weight: no critical alerts
)
```

## Query Capabilities

### Filter Operations
| Natural Language | Field | Operation |
|-----------------|-------|-----------|
| "more than 5 offline devices" | offlineDevices | > 5 |
| "at least 100 clients" | totalClients | >= 100 |
| "less than 90% uptime" | wanUptime | < 90 |
| "exactly 3 APs" | wifiDevices | === 3 |
| "offline" / "down" / "issues" | hasIssues | === true |
| "healthy" / "online" / "good" | isHealthy | === true |

### Aggregation Operations
| Query Pattern | Function |
|--------------|----------|
| "total clients" | sum(totalClients) |
| "average health score" | avg(healthScore) |
| "how many sites" | count() |
| "top 10 by clients" | top(10, 'totalClients') |
| "worst uptime" | bottom(5, 'wanUptime') |

### ISP Filters (OberaConnect Common ISPs)
- **Verizon**
- **Lumen** / Level3 / CenturyLink
- **AT&T**
- **Spectrum** / Charter
- **Comcast** / Xfinity
- **Cox**
- **Mediacom**
- **Brightspeed**

### Site Name Patterns (OberaConnect Customers)
Common customer name patterns for filtering:
- Setco, Hoods, Kinder Morgan, Anne's
- Celebration, Jubilee, Tracery
- Coastal, Fairhope, Freeport
- Panama City, Destin, Pensacola
- Dirt Works, Fulcrum, Clauger
- OberaConnect (internal)

## Response Formatting

### Site Detail Response
```
📍 [Site Name]
━━━━━━━━━━━━━━━━━━━━━━━━━━━
Health Score: [##%] [emoji based on score]
ISP: [provider] | Uptime: [##%]

Devices: [online]/[total] online
  • APs: [#] ([offline] offline)
  • Switches: [#] ([offline] offline)
  • Gateways: [#] ([offline] offline)

Clients: [total] connected
  • WiFi: [#] | Wired: [#] | Guest: [#]

Alerts: [critical] critical, [warning] warnings
Networks: [ssids] SSIDs, [vlans] VLANs
```

### Fleet Summary Response
```
🌐 OberaConnect Fleet Status
━━━━━━━━━━━━━━━━━━━━━━━━━━━
Sites: [total] | Devices: [total] | Clients: [total]

Health Overview:
  🟢 Healthy: [#] sites ([%])
  🟡 Warning: [#] sites ([%])
  🔴 Critical: [#] sites ([%])

Top Issues:
  1. [site] - [issue]
  2. [site] - [issue]
```

### Filter Results Response
```
Found [#] sites matching "[query]":

1. [Site Name] - [key metric]
2. [Site Name] - [key metric]
...

Quick stats: [aggregate relevant to query]
```

## Example Queries

### Status Queries
- "What's offline?"
- "Show me sites with issues"
- "Which sites are healthy?"
- "Any critical alerts?"

### Specific Filters
- "Sites with more than 5 offline devices"
- "Show Verizon customers"
- "Which sites have under 95% uptime?"
- "Find sites with over 200 clients"
- "Sites using AT&T"

### Rankings
- "Top 10 sites by clients"
- "Worst performing sites"
- "Sites with highest retry rates"
- "Biggest sites by device count"

### Site-Specific
- "Status of Setco Corporate"
- "How is Celebration Church doing?"
- "Show me details for Fairhope location"

### Aggregations
- "Total clients across all sites"
- "Average health score"
- "How many sites have issues?"
- "Sum of all offline devices"

## Integration Notes

### Data Source
- API Endpoint: `https://cloudaccess.svc.ui.com/api/cloud-access/sites`
- Authentication: AWS SigV4 with browser session tokens
- Refresh: Every 5 minutes recommended

### Token Extraction (Browser DevTools)
Required headers from authenticated session:
- `x-amz-date`
- `x-amz-security-token`
- `authorization`
- `x-amz-user-agent`

### Python Client Location
`/path/to/oberaconnect-ai-ops/tools/unifi/unifi_client.py`

### n8n Integration
Workflow template available for scheduled data pulls and alerting.
