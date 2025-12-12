# Privileged Access Audit Logging

## 📋 Overview

The OberaConnect platform includes comprehensive audit logging for privileged access to RMM (Remote Monitoring and Management) systems and other critical infrastructure. This feature ensures compliance with SOC2, HIPAA, and other regulatory frameworks that require tracking of privileged system access.

## 🎯 Purpose

**Audit logging tracks:**
- Who accessed privileged systems (user identification)
- When access occurred (timestamp)
- What system was accessed (NinjaOne, Azure, etc.)
- What actions were performed (view devices, modify settings, etc.)
- Why access was granted (business context)
- How access was obtained (authentication method, IP address)

## 🏗️ Architecture

### Components

#### 1. **Database Table: `audit_logs`**
Stores all audit events with complete context.

**Schema:**
```typescript
interface AuditLog {
  id: string;                  // Unique log entry ID
  created_at: string;          // Auto-generated timestamp
  user_id: string;             // User who performed the action
  customer_id: string;         // Customer organization
  action_type: string;         // Type of action (e.g., 'privileged_view_devices')
  system_name: string;         // System accessed (e.g., 'ninjaone', 'azure')
  action_details: object;      // JSONB with action-specific data
  compliance_tags: string[];   // Categorization tags
  timestamp: string;           // Action timestamp
  ip_address?: string;         // IP address (optional)
  user_agent?: string;         // Browser/client info (optional)
}
```

#### 2. **Hook: `useAuditLog`**
Centralized logging hook for frontend components.

**Location:** `src/hooks/useAuditLog.tsx`

**Functions:**
- `logAction(entry)` - Log any audit event
- `logPrivilegedAccess(system, action, details)` - Log privileged system access

**Auto-populated fields:**
- `user_id` - Retrieved from Supabase Auth
- `customer_id` - Retrieved from user profile
- `timestamp` - Auto-generated

#### 3. **Page: `PrivilegedAccessAudit`**
Dashboard for viewing and filtering audit logs.

**Location:** `src/pages/PrivilegedAccessAudit.tsx`

**Features:**
- Display all audit logs with user information
- Filter by search term (user, system, action)
- Filter by system (NinjaOne, Azure, etc.)
- Export logs to CSV
- Statistics summary cards
- Action type badges for visual categorization

**Route:** `/privileged-access-audit`

## 📚 Usage Guide

### For Developers

#### Logging Privileged Access

```typescript
import { useAuditLog } from '@/hooks/useAuditLog';

const NinjaOneIntegration = () => {
  const { logPrivilegedAccess } = useAuditLog();

  const handleDeviceView = async (deviceId: string) => {
    // Log the privileged access
    await logPrivilegedAccess('ninjaone', 'view_device', {
      device_id: deviceId,
      device_name: 'Server-01',
      alert_count: 2
    });

    // Perform the actual action
    // ... your code here
  };

  return (
    // ... your UI
  );
};
```

#### Logging Custom Actions

```typescript
const MyComponent = () => {
  const { logAction } = useAuditLog();

  const handleConfigChange = async () => {
    await logAction({
      action_type: 'config_update',
      system_name: 'platform',
      action_details: {
        setting: 'theme',
        old_value: 'light',
        new_value: 'dark'
      },
      compliance_tags: ['configuration', 'user_settings']
    });
  };
};
```

### For Compliance Teams

#### Viewing Audit Logs

1. Navigate to `/privileged-access-audit`
2. View all logs with timestamps and user information
3. Use search to find specific users, systems, or actions
4. Filter by system using the dropdown
5. Export to CSV for reporting

#### Common Queries

**All NinjaOne access:**
- Filter by system: "NinjaOne"

**Specific user activity:**
- Search: user's email or name

**Date range:**
- Logs are displayed in reverse chronological order
- Use export feature and filter in Excel/sheets

#### Compliance Reports

Export logs and filter by:
- Compliance tags: `privileged_access`, `rmm`, `security`
- Time period: Last 30/60/90 days
- Specific systems: NinjaOne, Azure, Keeper

## 🔐 Security Considerations

### Row Level Security (RLS)

Audit logs are protected by RLS policies:
- Users can only view logs for their customer organization
- Admin and compliance roles have full read access
- No user can modify or delete audit logs
- System automatically creates logs (no manual entry)

### Data Retention

- Logs are retained indefinitely by default
- Implement retention policy based on compliance requirements
- Consider archiving old logs for performance

### Sensitive Data

**Do NOT log:**
- Passwords or API keys
- Credit card numbers
- Social Security Numbers
- Protected health information (PHI)

**DO log:**
- User IDs and names
- System accessed
- Action performed
- Business justification
- Timestamp and IP address

## 📊 Compliance Mapping

### SOC2 Type II

**Control:** Access Control & Monitoring
- **CC6.1**: Logical access controls are implemented
- **CC6.2**: Privileged access is monitored and logged
- **CC6.6**: Audit logs are protected from unauthorized access

### HIPAA

**Standard:** 164.312(b) - Audit Controls
- Implement audit trails to record and examine activity
- Track user access to ePHI systems

### ISO 27001

**Control:** A.12.4.1 - Event Logging
- Record user activities, exceptions, and security events
- Include timestamps, user IDs, and system identifiers

## 🔄 Integration Points

### Current Integrations with Audit Logging

1. **NinjaOne RMM** (`src/pages/NinjaOneIntegration.tsx`)
   - Connection attempts
   - Device list views
   - Alert views
   - Configuration changes

### Future Integrations

2. **Azure/Microsoft 365**
   - Admin portal access
   - User permission changes
   - License modifications

3. **Keeper Security**
   - Vault access
   - Password retrieval
   - Shared folder access

4. **Network Security Systems**
   - Firewall rule changes
   - VPN access logs
   - Network configuration updates

## 🚀 Extending Audit Logging

### Adding New Systems

1. **Import the hook:**
   ```typescript
   import { useAuditLog } from '@/hooks/useAuditLog';
   ```

2. **Add logging calls:**
   ```typescript
   const { logPrivilegedAccess } = useAuditLog();
   
   await logPrivilegedAccess('your_system_name', 'action_type', {
     // system-specific details
   });
   ```

3. **Update compliance tags:**
   ```typescript
   compliance_tags: ['privileged_access', 'your_category', 'your_system']
   ```

### Adding Custom Action Types

Define action types in your component:

```typescript
type AuditAction = 
  | 'privileged_view_devices'
  | 'privileged_modify_settings'
  | 'privileged_access_granted'
  | 'privileged_access_denied'
  | 'connection_attempt'
  | 'connection_success'
  | 'connection_failure';
```

## 📈 Monitoring & Alerting

### Recommended Alerts

1. **High-Volume Access**
   - Alert if single user accesses RMM > 50 times/hour
   
2. **After-Hours Access**
   - Alert for privileged access outside business hours
   
3. **Failed Connection Attempts**
   - Alert after 3 failed authentication attempts

4. **Multiple System Access**
   - Alert if user accesses 5+ systems in short timespan

### Dashboard Metrics

Track these KPIs:
- Total privileged access events per day
- Unique users accessing privileged systems
- Most accessed systems
- Access patterns by time of day
- Failed vs. successful access attempts

## 🛠️ Troubleshooting

### Logs Not Appearing

**Check:**
1. User is authenticated (`supabase.auth.getUser()` returns user)
2. User has `customer_id` in profile
3. No RLS policy errors in console
4. Supabase client is properly configured

### Missing User Information

**Cause:** User profile not created during signup

**Fix:**
```sql
-- Check if profile exists
SELECT * FROM user_profiles WHERE user_id = 'user-uuid';

-- Create if missing
INSERT INTO user_profiles (user_id, customer_id, full_name)
VALUES ('user-uuid', 'customer-uuid', 'User Name');
```

### Export Not Working

**Check:**
1. Browser allows downloads
2. Pop-up blocker is not blocking download
3. Logs exist (filteredLogs.length > 0)

## 📝 Best Practices

### Do's

✅ Log all privileged system access
✅ Include business context in action_details
✅ Use descriptive action_type names
✅ Tag logs with relevant compliance_tags
✅ Review logs regularly
✅ Export logs for external audits

### Don'ts

❌ Log sensitive credentials
❌ Modify existing audit logs
❌ Skip logging for "small" actions
❌ Use generic action types
❌ Ignore log failures silently
❌ Store logs without retention policy

## 🔗 Related Documentation

- [ARCHITECTURE.md](./ARCHITECTURE.md) - Overall system architecture
- [API_REFERENCE.md](./API_REFERENCE.md) - Database API and queries
- [DEVELOPER_HANDOFF.md](./DEVELOPER_HANDOFF.md) - Knowledge transfer guide
- [README.md](./README.md) - Platform overview

## 📞 Support

For questions about audit logging implementation:
1. Review this guide and related documentation
2. Check existing implementations (NinjaOneIntegration.tsx)
3. Consult with compliance team for specific requirements

---

**Last Updated:** 2025-10-05
**Version:** 1.0
**Maintained By:** OberaConnect Development Team
