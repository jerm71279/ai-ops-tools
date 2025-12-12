# SNMP & Syslog Infrastructure Implementation

## Overview
Comprehensive network monitoring infrastructure for centralized SNMP trap collection, syslog message processing, device polling, and intelligent alerting.

## Database Schema

### Tables Created

1. **network_devices** - SNMP-enabled devices
   - Device inventory with SNMP credentials
   - Polling configuration (intervals, versions)
   - Syslog enablement per device
   - Links to CMDB configuration items
   - Tracks last poll/syslog timestamps

2. **snmp_traps** - Incoming SNMP traps
   - Trap OID and type classification
   - Varbind data storage (JSONB)
   - Severity assessment
   - Acknowledgment workflow
   - Links to created incidents

3. **syslog_messages** - Syslog event storage
   - RFC 5424 compliant structure
   - Facility/severity/priority parsing
   - Full-text search indexing
   - Security event tagging
   - Structured data support

4. **device_metrics** - Time-series polling data
   - CPU, memory, interface metrics
   - OID-based data collection
   - Metric units and metadata
   - Optimized for time-series queries

5. **network_alerts** - Derived alerts
   - Correlated from traps/logs/metrics
   - Severity classification
   - Assignment and status tracking
   - Auto-remediation integration
   - Incident escalation

6. **network_alert_rules** - Alerting policies
   - Pattern matching for syslog
   - Trap OID matching
   - Metric threshold definitions
   - Notification channels
   - Auto-remediation triggers

## Edge Functions

### 1. snmp-collector
**Purpose**: Receive and process SNMP traps

**Endpoint**: `/functions/v1/snmp-collector`

**Features**:
- Device identification by source IP
- Trap type classification (linkDown, linkUp, etc.)
- Severity determination
- Alert rule matching
- Automatic alert creation
- Device timestamp updates

**Example Request**:
```json
{
  "sourceIp": "192.168.1.1",
  "trapOid": "1.3.6.1.6.3.1.1.5.3",
  "trapType": "linkDown",
  "varbinds": [
    { "oid": "1.3.6.1.2.1.2.2.1.1", "value": "2", "type": "integer" }
  ],
  "customerId": "uuid"
}
```

### 2. syslog-collector
**Purpose**: Receive and process syslog messages

**Endpoint**: `/functions/v1/syslog-collector`

**Features**:
- RFC 5424 compliant parsing
- Security event pattern detection
- Device association by IP
- Priority calculation
- Alert rule evaluation
- Anomaly detection integration

**Security Patterns Detected**:
- Authentication failures
- Unauthorized access attempts
- Firewall blocks
- Malware detection
- Port scans
- Brute force attacks

**Example Request**:
```json
{
  "sourceIp": "192.168.1.100",
  "hostname": "firewall-01",
  "facility": 16,
  "severity": 4,
  "timestamp": "2025-01-08T10:00:00Z",
  "appName": "iptables",
  "message": "Denied connection from 10.0.0.5 to 192.168.1.10:22",
  "customerId": "uuid"
}
```

### 3. device-poller
**Purpose**: Poll SNMP devices for metrics

**Endpoint**: `/functions/v1/device-poller`

**Features**:
- Standard OID collection (CPU, memory, interfaces)
- Configurable polling intervals
- Threshold alert generation
- Device status updates
- Metric storage optimization

**Standard OIDs Polled**:
- sysUpTime: 1.3.6.1.2.1.1.3.0
- hrProcessorLoad: 1.3.6.1.2.1.25.3.3.1.2
- hrStorageUsed: 1.3.6.1.2.1.25.2.3.1.6
- ifOperStatus: 1.3.6.1.2.1.2.2.1.8
- ifInOctets: 1.3.6.1.2.1.2.2.1.10
- ifOutOctets: 1.3.6.1.2.1.2.2.1.16

**Example Request**:
```json
{
  "device_id": "uuid"
}
```

## UI Dashboard

### Network Monitoring Page (`/network-monitoring`)

**Features**:
- Device inventory management
- Real-time alert dashboard
- Syslog message search and filtering
- Device polling on-demand
- Multi-tab interface (Devices, Alerts, Logs)

**Stats Cards**:
- Total Devices
- Active Devices
- Open Alerts
- Critical Alerts

**Device Management**:
- Add/edit network devices
- Configure SNMP credentials
- Enable/disable polling
- View device metrics
- Manual poll triggering

**Alert Management**:
- View open alerts by severity
- Acknowledge alerts
- View alert details
- Filter by device/type

**Log Search**:
- Full-text search across syslog messages
- Severity filtering
- Security event highlighting
- Timestamp-based browsing
- Export capabilities

## Integration Points

### CMDB Integration
- Link network devices to configuration items
- Track dependencies
- Impact analysis for changes
- Asset tracking

### SOC Integration
- Security event correlation
- Anomaly detection triggers
- Incident escalation
- Threat intelligence enrichment

### Incidents Module
- Automatic incident creation
- Alert-to-incident linking
- Severity inheritance
- Workflow automation

### Compliance Integration
- Audit log generation
- Security event tracking
- Compliance tag support
- Evidence collection

## Alert Rules Configuration

### Rule Types

1. **SNMP Trap Rules**
   ```json
   {
     "rule_type": "snmp_trap",
     "conditions": {
       "trapOid": "1.3.6.1.6.3.1.1.5.3",
       "trapType": "linkDown"
     },
     "severity": "high",
     "notification_channels": ["email", "webhook"]
   }
   ```

2. **Syslog Pattern Rules**
   ```json
   {
     "rule_type": "syslog_pattern",
     "conditions": {
       "pattern": "authentication failed",
       "severity": 4
     },
     "severity": "critical",
     "notification_channels": ["email", "sms"]
   }
   ```

3. **Metric Threshold Rules**
   ```json
   {
     "rule_type": "metric_threshold",
     "conditions": {
       "metric_type": "cpu",
       "threshold": 90
     },
     "severity": "warning",
     "auto_remediation_workflow_id": "uuid"
   }
   ```

## Security Features

### Row Level Security (RLS)
- All tables protected by customer_id isolation
- Users can only view their organization's data
- System functions can insert without authentication
- Fine-grained access control

### Data Protection
- SNMP community strings stored securely
- Credential encryption for SNMPv3
- Audit logging for all access
- Privileged access tracking

### Compliance Support
- Audit trail for all events
- Retention policies configurable
- Compliance tags on all data
- Security event classification

## Performance Optimizations

### Indexing Strategy
- Full-text search on syslog messages (GIN index)
- Time-series optimized indexes
- Source IP lookup optimization
- Customer isolation indexes

### Data Retention
- Time-series data partitioning
- Automated archival policies
- Configurable retention periods
- Storage optimization

## Future Enhancements

### Phase 2 Features
1. **SNMP v3 Support**
   - User-based security
   - Authentication protocols (MD5, SHA)
   - Privacy protocols (DES, AES)

2. **MIB Browser**
   - Visual OID navigation
   - Custom OID queries
   - MIB file uploads

3. **Advanced Correlation**
   - Multi-event correlation
   - Behavioral analysis
   - Anomaly scoring
   - ML-based predictions

4. **Network Discovery**
   - Automatic device discovery
   - Topology mapping
   - Dependency visualization
   - CDP/LLDP integration

5. **Performance Analytics**
   - Bandwidth utilization trends
   - Capacity planning
   - Baseline establishment
   - Predictive alerting

## API Endpoints Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/network-monitoring` | GET | View dashboard |
| `/functions/v1/snmp-collector` | POST | Receive SNMP traps |
| `/functions/v1/syslog-collector` | POST | Receive syslog messages |
| `/functions/v1/device-poller` | POST | Poll device metrics |

## Configuration Examples

### Firewall Syslog Configuration (SonicWall)
```
Log > Syslog Settings
- Enable Syslog
- Server: <your-instance>.functions.supabase.co
- Port: 514 (or custom)
- Protocol: UDP
- Format: RFC 5424
```

### Switch SNMP Configuration (Cisco)
```
snmp-server community public RO
snmp-server trap-source GigabitEthernet0/0
snmp-server enable traps snmp linkdown linkup
snmp-server host <your-endpoint> version 2c public
```

### Network Device Setup
1. Navigate to `/network-monitoring`
2. Click "Add Device"
3. Enter device details:
   - Device Name
   - IP Address
   - Device Type (switch/router/firewall)
   - SNMP Version & Community
   - Enable polling/syslog
4. Configure polling interval
5. Save and test connectivity

## Monitoring Best Practices

1. **Device Organization**
   - Group by location/department
   - Use consistent naming conventions
   - Link to CMDB items
   - Document critical devices

2. **Alert Tuning**
   - Start with critical alerts only
   - Gradually add informational alerts
   - Tune thresholds based on baselines
   - Avoid alert fatigue

3. **Log Retention**
   - Keep security logs longer
   - Archive non-critical logs
   - Comply with regulations
   - Balance storage costs

4. **Performance Monitoring**
   - Monitor collector performance
   - Track database growth
   - Optimize queries regularly
   - Scale infrastructure as needed

## Troubleshooting

### No Traps Received
- Verify firewall rules allow UDP 162
- Check device trap configuration
- Validate endpoint URL
- Review edge function logs

### No Syslog Messages
- Verify firewall rules allow UDP 514
- Check syslog server configuration
- Validate endpoint URL
- Review message format

### Polling Failures
- Verify SNMP credentials
- Check network connectivity
- Validate SNMP version compatibility
- Review device status

## Documentation & Support

- [SNMP RFC 3416](https://tools.ietf.org/html/rfc3416)
- [Syslog RFC 5424](https://tools.ietf.org/html/rfc5424)
- [Net-SNMP Documentation](http://www.net-snmp.org/docs/)
- Edge Function Logs: Backend > Edge Functions > Logs

## Implementation Status

✅ Database schema created
✅ Edge functions deployed
✅ UI dashboard implemented
✅ Basic alert rules
✅ Security event detection
✅ CMDB integration
✅ SOC integration
✅ Navigation added

🚧 Pending:
- SNMPv3 support
- MIB browser
- Network discovery
- Advanced correlation
- Performance analytics dashboard