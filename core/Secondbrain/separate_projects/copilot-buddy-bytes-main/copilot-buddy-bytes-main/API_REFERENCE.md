# OberaConnect API Reference

**Last Updated:** October 9, 2025  
**API Version:** 2.0  
**Total Edge Functions:** 17

## 🆕 Recent Updates (October 9, 2025)

### New Database Tables
- **`products`**: Product catalog with pricing, features, and billing cycles
- **`customer_subscriptions`**: Customer product subscription management
- **`applications`**: New app added - Keeper Security for password management

### New Hooks
- **`useProducts`**: Complete CRUD operations for product management

### Enhanced Features
- Products Admin page for catalog management
- Keeper Security integration in employee portal
- Updated audit logging for product changes

---

## 🌐 Overview

OberaConnect uses **Supabase** as its backend platform, providing:
- **PostgreSQL Database**: Accessed via Supabase client (55+ tables)
- **Edge Functions**: Serverless functions for custom logic and AI integration (17 functions)
- **Authentication**: Managed by Supabase Auth (Email + OAuth)
- **Storage**: File storage with secure buckets
- **Realtime**: Real-time subscriptions for live data

All API access is authenticated and protected by Row Level Security (RLS) policies.

## 🔐 Authentication

### Supabase Client Setup

```typescript
import { supabase } from '@/integrations/supabase/client';
```

The client is pre-configured with your project credentials and available globally.

### Auth Methods

#### Sign Up
```typescript
const { data, error } = await supabase.auth.signUp({
  email: 'user@example.com',
  password: 'securepassword123',
  options: {
    data: {
      full_name: 'John Doe',
      department: 'compliance'
    }
  }
});

// Returns: { user, session }
```

#### Sign In
```typescript
const { data, error } = await supabase.auth.signInWithPassword({
  email: 'user@example.com',
  password: 'securepassword123'
});

// Returns: { user, session }
```

#### Get Session
```typescript
const { data: { session } } = await supabase.auth.getSession();

// Returns: { session: { user, access_token, ... } } or { session: null }
```

#### Sign Out
```typescript
const { error } = await supabase.auth.signOut();
```

---

## 📊 Database API

### Core Tables

#### Customers
```typescript
// Fetch all customers (admin only, RLS enforced)
const { data, error } = await supabase
  .from('customers')
  .select('*')
  .order('created_at', { ascending: false });

// Fetch specific customer
const { data, error } = await supabase
  .from('customers')
  .select('*')
  .eq('id', customerId)
  .single();

// Create customer
const { data, error } = await supabase
  .from('customers')
  .insert({
    company_name: 'Acme Corp',
    contact_email: 'contact@acme.com',
    plan: 'professional',
    status: 'active'
  })
  .select()
  .single();
```

#### Products **NEW**
```typescript
// Fetch all active products
const { data, error } = await supabase
  .from('products')
  .select('*')
  .eq('is_active', true)
  .order('created_at', { ascending: false });

// Create product
const { data, error } = await supabase
  .from('products')
  .insert({
    product_name: 'Enterprise Plan',
    base_price: 199.99,
    billing_cycle: 'monthly',
    enabled_features: ['compliance', 'workflows', 'ai'],
    max_users: 100,
    max_storage_gb: 1000,
    is_active: true
  })
  .select()
  .single();

// Update product
const { data, error } = await supabase
  .from('products')
  .update({ base_price: 249.99 })
  .eq('id', productId)
  .select()
  .single();
```

#### Customer Subscriptions **NEW**
```typescript
// Fetch customer's active subscriptions
const { data, error } = await supabase
  .from('customer_subscriptions')
  .select(`
    *,
    product:products(*)
  `)
  .eq('customer_id', customerId)
  .eq('status', 'active');

// Create subscription
const { data, error } = await supabase
  .from('customer_subscriptions')
  .insert({
    customer_id: customerId,
    product_id: productId,
    status: 'active',
    start_date: new Date().toISOString(),
    auto_renew: true
  })
  .select()
  .single();
```

#### Applications **UPDATED**
```typescript
// Fetch all active applications
const { data, error } = await supabase
  .from('applications')
  .select('*')
  .eq('is_active', true)
  .order('display_order');

// NEW: Keeper Security application added
// Fetch security applications
const { data, error } = await supabase
  .from('applications')
  .select('*')
  .eq('category', 'security')
  .eq('is_active', true);
```

#### User Profiles
```typescript
// Fetch user's own profile
const { data, error } = await supabase
  .from('user_profiles')
  .select(`
    *,
    customers (
      company_name,
      plan,
      status
    )
  `)
  .eq('user_id', userId)
  .single();

// Update profile
const { data, error } = await supabase
  .from('user_profiles')
  .update({
    full_name: 'Jane Doe',
    role: 'manager'
  })
  .eq('user_id', userId);
```

#### Customer Customizations
```typescript
// Fetch customization for customer
const { data, error } = await supabase
  .from('customer_customizations')
  .select('*')
  .eq('customer_id', customerId)
  .single();

// Update customization
const { data, error } = await supabase
  .from('customer_customizations')
  .update({
    primary_color: '210 100% 50%',  // HSL format
    secondary_color: '180 80% 45%',
    accent_color: '30 95% 55%',
    enabled_integrations: ['azure', 'ninjaone', 'keeper'],
    enabled_features: ['compliance', 'ml_insights']
  })
  .eq('customer_id', customerId);
```

#### Integrations
```typescript
// Fetch all integrations (public)
const { data, error } = await supabase
  .from('integrations')
  .select('*')
  .is('customer_id', null);  // System-wide integrations

// Fetch customer-specific integrations
const { data, error } = await supabase
  .from('integrations')
  .select('*')
  .eq('customer_id', customerId);

// Create integration
const { data, error } = await supabase
  .from('integrations')
  .insert({
    customer_id: customerId,
    system_name: 'NinjaOne',
    integration_type: 'rmm',
    status: 'active',
    config: {
      api_key: 'encrypted_key',
      region: 'us-east-1'
    }
  });
```

#### MCP Servers
```typescript
// Fetch all MCP servers
const { data, error } = await supabase
  .from('mcp_servers')
  .select('*')
  .order('name');

// Check server status
const { data, error } = await supabase
  .from('mcp_servers')
  .select('name, status, capabilities')
  .eq('status', 'online');
```

#### Compliance Frameworks
```typescript
// Fetch frameworks for customer
const { data, error } = await supabase
  .from('compliance_frameworks')
  .select('*')
  .eq('customer_id', customerId);

// Get framework with controls
const { data, error } = await supabase
  .from('compliance_frameworks')
  .select(`
    *,
    compliance_controls (
      id,
      control_name,
      status
    )
  `)
  .eq('id', frameworkId)
  .single();
```

#### Workflows
```typescript
// Fetch workflows for customer
const { data, error } = await supabase
  .from('workflows')
  .select('*')
  .eq('customer_id', customerId);

// Count workflows
const { count, error } = await supabase
  .from('workflows')
  .select('*', { count: 'exact', head: true })
  .eq('customer_id', customerId);
```

#### ML Insights
```typescript
// Fetch recent insights
const { data, error } = await supabase
  .from('ml_insights')
  .select('*')
  .eq('customer_id', customerId)
  .order('created_at', { ascending: false })
  .limit(10);

// Count insights by type
const { data, error } = await supabase
  .from('ml_insights')
  .select('insight_type')
  .eq('customer_id', customerId);
```

#### Audit Logs
```typescript
// Fetch all audit logs for customer (with user profile data)
const { data, error } = await supabase
  .from('audit_logs')
  .select(`
    *,
    user_profiles (
      full_name,
      department
    )
  `)
  .eq('customer_id', customerId)
  .order('timestamp', { ascending: false })
  .limit(100);

// Fetch privileged access logs only
const { data, error } = await supabase
  .from('audit_logs')
  .select('*')
  .eq('customer_id', customerId)
  .contains('compliance_tags', ['privileged_access'])
  .order('timestamp', { ascending: false });

// Filter by system (e.g., NinjaOne)
const { data, error } = await supabase
  .from('audit_logs')
  .select('*')
  .eq('customer_id', customerId)
  .eq('system_name', 'ninjaone')
  .order('timestamp', { ascending: false });

// Create audit log entry using hook
import { useAuditLog } from '@/hooks/useAuditLog';

const MyComponent = () => {
  const { logPrivilegedAccess } = useAuditLog();
  
  const handleRMMAccess = async () => {
    await logPrivilegedAccess('ninjaone', 'view_devices', {
      device_count: 150,
      alert_count: 3
    });
  };
};
```

**Audit Log Schema**:
```typescript
interface AuditLog {
  id: string;
  created_at: string;
  user_id: string;
  customer_id: string;
  action_type: string;        // e.g., 'privileged_view_devices', 'connection_attempt'
  system_name: string;         // e.g., 'ninjaone', 'azure', 'keeper'
  action_details: object;      // JSONB with context-specific data
  compliance_tags: string[];   // e.g., ['privileged_access', 'rmm', 'ninjaone']
  timestamp: string;
  ip_address?: string;
  user_agent?: string;
}
```

**Common Compliance Tags**:
- `privileged_access`: Any RMM or admin-level system access
- `rmm`: Remote monitoring and management actions
- `ninjaone`: Specific to NinjaOne platform
- `security`: Security-related actions
- `compliance`: Compliance framework actions

### Query Patterns

#### Filtering
```typescript
// Single condition
.eq('status', 'active')
.neq('status', 'deleted')
.gt('created_at', '2025-01-01')
.lt('revenue', 10000)

// Multiple conditions (AND)
.eq('customer_id', customerId)
.eq('status', 'active')

// OR conditions
.or('status.eq.active,status.eq.pending')
```

#### Sorting
```typescript
.order('created_at', { ascending: false })
.order('name', { ascending: true })
```

#### Pagination
```typescript
.range(0, 9)  // First 10 records
.limit(20)    // Limit to 20 records
```

#### Aggregation
```typescript
// Count
const { count } = await supabase
  .from('customers')
  .select('*', { count: 'exact', head: true });

// Sum (use custom SQL or aggregate in code)
```

---

## ⚡ Edge Functions

### Department Assistant

**Endpoint**: `department-assistant`

**Purpose**: AI-powered department-specific assistant

**Request**:
```typescript
const { data, error } = await supabase.functions.invoke('department-assistant', {
  body: {
    department: 'compliance',  // Required
    message: 'What frameworks are we tracking?',  // Required
    customerId: 'uuid-string',  // Optional
    context: {  // Optional
      frameworks: ['SOC2', 'GDPR'],
      controls: 120
    }
  }
});
```

**Response**:
```typescript
{
  response: string;  // AI-generated response
  model: string;     // Model used (e.g., 'google/gemini-2.5-flash')
  timestamp: string;
}
```

**Supported Departments**:
- `compliance`: Frameworks, controls, evidence
- `it`: Integrations, servers, security
- `operations`: Workflows, efficiency, bottlenecks
- `hr`: Employees, sessions, department stats
- `finance`: Revenue, subscriptions, customers
- `sales`: Pipeline, deals, forecasts
- `executive`: KPIs, strategic metrics

**Example Usage**:
```typescript
import { supabase } from '@/integrations/supabase/client';

const askAI = async (message: string) => {
  const { data, error } = await supabase.functions.invoke('department-assistant', {
    body: {
      department: 'compliance',
      message: message,
      context: {
        frameworks: 3,
        controls: 45,
        evidence_files: 230
      }
    }
  });

  if (error) {
    console.error('AI Error:', error);
    return;
  }

  console.log('AI Response:', data.response);
};
```

---

### MCP Server

**Endpoint**: `mcp-server`

**Purpose**: Model Context Protocol integration for advanced AI capabilities

**Request**:
```typescript
const { data, error } = await supabase.functions.invoke('mcp-server', {
  body: {
    action: 'execute_tool',  // Required
    server_id: 'uuid-string',  // Required
    tool_name: 'analyze_data',  // Required
    parameters: {  // Optional
      dataset: 'compliance_metrics',
      timeframe: '30d'
    }
  }
});
```

**Response**:
```typescript
{
  result: any;       // Tool execution result
  server: string;    // MCP server name
  status: string;    // 'success' | 'error'
  timestamp: string;
}
```

**Available Actions**:
- `execute_tool`: Run a tool on MCP server
- `list_capabilities`: Get server capabilities
- `check_status`: Health check

**Example Usage**:
```typescript
const executeMCPTool = async () => {
  const { data, error } = await supabase.functions.invoke('mcp-server', {
    body: {
      action: 'execute_tool',
      server_id: 'mcp-123',
      tool_name: 'risk_analysis',
      parameters: {
        customer_id: customerId,
        frameworks: ['SOC2', 'HIPAA']
      }
    }
  });

  if (error) {
    console.error('MCP Error:', error);
    return;
  }

  console.log('Analysis Result:', data.result);
};
```

---

## 🔄 Realtime Subscriptions

Supabase supports realtime updates for table changes.

### Subscribe to Table Changes

```typescript
const channel = supabase
  .channel('integrations-changes')
  .on(
    'postgres_changes',
    {
      event: '*',  // 'INSERT' | 'UPDATE' | 'DELETE' | '*'
      schema: 'public',
      table: 'integrations',
      filter: `customer_id=eq.${customerId}`  // Optional
    },
    (payload) => {
      console.log('Change detected:', payload);
      // Update UI with new data
    }
  )
  .subscribe();

// Cleanup
channel.unsubscribe();
```

### Realtime Use Cases

- **Integration Status**: Live updates when integrations change state
- **MCP Server Health**: Real-time server status monitoring
- **Compliance Updates**: Notify when frameworks/controls are updated
- **Chat/Collaboration**: Multi-user dashboard updates

---

### Revio Data Integration

**Endpoint**: `revio-data`

**Purpose**: Customer billing and revenue data aggregation from Revio

**Current Status**: Infrastructure complete with placeholder data until OneBill → Revio migration

**Request**:
```typescript
const { data, error } = await supabase.functions.invoke('revio-data', {
  body: {
    dataType: 'all'  // Required: 'all', 'customers_by_ticket', 'customers_by_sla', 'customers_by_revenue', 'subscriptions', 'recent_interactions'
  }
});
```

**Response**:
```typescript
{
  success: boolean;
  message?: string;
  data: {
    customers_by_ticket: CustomersByTicket[];
    customers_by_sla: CustomersBySLA[];
    customers_by_revenue: CustomersByRevenue[];
    subscriptions: SubscriptionStats;
    recent_interactions: CustomerInteraction[];
  }
}
```

**Example Usage**:
```typescript
import { useRevioData } from '@/hooks/useRevioData';

const SalesDashboard = () => {
  const { data, loading, error } = useRevioData();
  
  if (loading) return <div>Loading revenue data...</div>;
  if (error) return <div>Error: {error}</div>;
  
  return (
    <div>
      <h2>Active Subscriptions: {data.subscriptions.active}</h2>
      <h2>Revenue by Tier:</h2>
      {data.customers_by_revenue.map(tier => (
        <div key={tier.revenue_tier}>
          {tier.revenue_tier}: ${tier.total_revenue}
        </div>
      ))}
    </div>
  );
};
```

**Documentation**: See `API_REFERENCE_REVIO.md` for complete Revio API documentation

---

### CIPP Sync

**Endpoint**: `cipp-sync`

**Purpose**: Centralized Microsoft 365 tenant management via CIPP API

**Authentication**: Requires JWT (admin role recommended)

**Request**:
```typescript
// Sync all tenants from CIPP
const { data, error } = await supabase.functions.invoke('cipp-sync', {
  body: {
    action: 'sync_tenants',
    customerId: 'uuid-string'
  }
});

// Get tenant health scores
const { data, error } = await supabase.functions.invoke('cipp-sync', {
  body: {
    action: 'get_tenant_health',
    tenantId: 'tenant-id-string',
    customerId: 'uuid-string'
  }
});

// Apply security baseline to tenants
const { data, error } = await supabase.functions.invoke('cipp-sync', {
  body: {
    action: 'apply_baseline',
    baselineId: 'uuid-string',
    targetTenantIds: ['tenant-id-1', 'tenant-id-2'],
    customerId: 'uuid-string'
  }
});
```

**Response**:
```typescript
{
  success: boolean;
  message?: string;
  data?: any;
  results?: Array<{
    tenant: string;
    status: 'success' | 'error';
    error?: string;
  }>;
}
```

**Supported Actions**:
- `sync_tenants` - Import all Microsoft 365 tenants from CIPP instance
- `get_tenant_health` - Fetch security scores and health metrics
- `apply_baseline` - Deploy security baseline to multiple tenants

**Database Integration**:
```typescript
// Fetching tenant data
const { data: tenants } = await supabase
  .from('cipp_tenants')
  .select('*')
  .eq('customer_id', customerId)
  .order('tenant_name');

// Fetching health data
const { data: health } = await supabase
  .from('cipp_tenant_health')
  .select('*')
  .in('tenant_id', tenantIds)
  .order('last_checked_at', { ascending: false });

// Creating security baseline
const { data } = await supabase
  .from('cipp_security_baselines')
  .insert({
    customer_id: customerId,
    baseline_name: 'CIS Microsoft 365',
    baseline_type: 'security',
    settings: { /* baseline config */ },
    created_by: userId
  });
```

**CIPP API Integration**:
- **ListTenants**: GET `/api/ListTenants` - Retrieves all managed tenants
- **GetSecureScore**: POST `/api/ListGraphRequest` - Tenant security scoring
- **ApplyStandards**: POST `/api/AddStandardsDeploy` - Deploy security standards

**Required Secrets**:
- `CIPP_URL` - CIPP instance URL
- `CIPP_API_KEY` - CIPP API key with tenant management permissions

**Example Usage**:
```typescript
const CIPPTenantManager = () => {
  const handleSync = async () => {
    const { data, error } = await supabase.functions.invoke('cipp-sync', {
      body: {
        action: 'sync_tenants',
        customerId: currentCustomerId
      }
    });
    
    if (data?.success) {
      console.log(`Synced ${data.message}`);
      // Refresh tenant list
    }
  };
  
  return (
    <Button onClick={handleSync}>
      Sync Tenants from CIPP
    </Button>
  );
};
```

---

### 13. `snmp-collector` - SNMP Trap Collection

**Endpoint**: POST `/functions/v1/snmp-collector`  
**Auth**: ❌ Public webhook endpoint  
**Purpose**: Receives and processes SNMP trap notifications from network devices

**Request Body**:
```typescript
{
  device_ip: string;          // Source device IP
  trap_oid: string;           // SNMP trap OID
  trap_type: string;          // Trap type (e.g., 'linkDown', 'authenticationFailure')
  severity: string;           // 'critical' | 'high' | 'medium' | 'low' | 'info'
  message: string;            // Human-readable trap description
  varbinds?: Array<{          // Optional variable bindings
    oid: string;
    type: string;
    value: any;
  }>;
  customer_id: string;        // Customer UUID
}
```

**Response**:
```typescript
{
  success: boolean;
  message: string;
  trap_id?: string;           // Created trap record UUID
  alert_id?: string;          // Created alert UUID (if rules matched)
  matched_rules?: number;     // Number of alert rules matched
}
```

**Example Usage**:
```typescript
// Called from network monitoring system
const response = await fetch('https://your-project.supabase.co/functions/v1/snmp-collector', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    device_ip: '192.168.1.1',
    trap_oid: '1.3.6.1.6.3.1.1.5.3',
    trap_type: 'linkDown',
    severity: 'critical',
    message: 'Interface GigabitEthernet0/1 is down',
    varbinds: [
      { oid: '1.3.6.1.2.1.2.2.1.1', type: 'INTEGER', value: 1 }
    ],
    customer_id: 'customer-uuid'
  })
});
```

---

### 14. `syslog-collector` - Syslog Message Collection

**Endpoint**: POST `/functions/v1/syslog-collector`  
**Auth**: ❌ Public webhook endpoint  
**Purpose**: Receives and analyzes syslog messages from network devices and servers

**Request Body**:
```typescript
{
  device_ip: string;          // Source device IP
  facility: string;           // Syslog facility (e.g., 'kern', 'user', 'daemon')
  severity: string;           // 'emergency' | 'alert' | 'critical' | 'error' | 'warning' | 'notice' | 'info' | 'debug'
  message: string;            // Syslog message content
  timestamp?: string;         // ISO timestamp (defaults to now())
  hostname?: string;          // Source hostname
  app_name?: string;          // Application name
  proc_id?: string;           // Process ID
  msg_id?: string;            // Message ID
  customer_id: string;        // Customer UUID
}
```

**Response**:
```typescript
{
  success: boolean;
  message: string;
  syslog_id?: string;         // Created syslog record UUID
  alert_id?: string;          // Created alert UUID (if patterns matched)
  security_pattern?: boolean; // True if security pattern detected
  matched_rules?: number;     // Number of alert rules matched
}
```

**Security Pattern Detection**:
- Authentication failures: `failed.*auth|authentication.*failed|invalid.*password`
- Unauthorized access: `denied|unauthorized|forbidden|access.*denied`
- Configuration changes: `config.*change|configuration.*modified`
- Critical system events: `shutdown|reboot|kernel.*panic|system.*crash`

**Example Usage**:
```typescript
// Called from syslog forwarder
const response = await fetch('https://your-project.supabase.co/functions/v1/syslog-collector', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    device_ip: '192.168.1.10',
    facility: 'auth',
    severity: 'warning',
    message: 'Failed password for user admin from 10.0.0.5',
    hostname: 'firewall01',
    customer_id: 'customer-uuid'
  })
});
```

---

### 15. `device-poller` - Network Device SNMP Polling

**Endpoint**: POST `/functions/v1/device-poller`  
**Auth**: ✅ JWT Required  
**Purpose**: Polls network devices for metrics via SNMP and generates alerts based on thresholds

**Request Body**:
```typescript
{
  device_id?: string;         // Poll specific device (UUID)
  customer_id?: string;       // Poll all devices for customer
  metrics?: string[];         // Specific metrics to poll ['cpu', 'memory', 'interfaces']
}
```

**Response**:
```typescript
{
  success: boolean;
  message: string;
  results: Array<{
    device_id: string;
    device_name: string;
    device_ip: string;
    status: 'success' | 'error';
    metrics?: {
      cpu_usage?: number;
      memory_usage?: number;
      interface_status?: Record<string, 'up' | 'down'>;
      uptime?: number;
    };
    alerts_generated?: number;
    error?: string;
  }>;
  total_polled: number;
  total_alerts: number;
}
```

**Automatic Alert Generation**:
- CPU usage > 90%: Critical alert
- CPU usage > 80%: High alert
- Memory usage > 90%: Critical alert
- Memory usage > 85%: High alert
- Interface down: Medium alert

**Example Usage**:
```typescript
// Poll all devices for a customer
const { data, error } = await supabase.functions.invoke('device-poller', {
  body: {
    customer_id: 'customer-uuid',
    metrics: ['cpu', 'memory', 'interfaces']
  },
  headers: {
    Authorization: `Bearer ${session.access_token}`
  }
});

// Poll specific device
const { data, error } = await supabase.functions.invoke('device-poller', {
  body: {
    device_id: 'device-uuid'
  },
  headers: {
    Authorization: `Bearer ${session.access_token}`
  }
});
```

**Database Integration**:
```typescript
// Fetch network devices
const { data: devices } = await supabase
  .from('network_devices')
  .select('*')
  .eq('customer_id', customerId)
  .eq('status', 'active');

// Fetch recent SNMP traps
const { data: traps } = await supabase
  .from('snmp_traps')
  .select('*')
  .eq('customer_id', customerId)
  .order('timestamp', { ascending: false })
  .limit(100);

// Fetch syslog messages with filtering
const { data: syslogs } = await supabase
  .from('syslog_messages')
  .select('*')
  .eq('customer_id', customerId)
  .gte('severity_level', 3)  // Warning and above
  .order('timestamp', { ascending: false })
  .limit(100);

// Fetch active alerts
const { data: alerts } = await supabase
  .from('network_alerts')
  .select('*')
  .eq('customer_id', customerId)
  .eq('status', 'active')
  .order('created_at', { ascending: false });

// Fetch device metrics
const { data: metrics } = await supabase
  .from('device_metrics')
  .select('*')
  .eq('device_id', deviceId)
  .order('timestamp', { ascending: false })
  .limit(100);

// Configure alert rules
const { data } = await supabase
  .from('network_alert_rules')
  .insert({
    customer_id: customerId,
    rule_name: 'High CPU Usage',
    rule_type: 'threshold',
    severity: 'high',
    conditions: {
      metric: 'cpu_usage',
      operator: '>',
      threshold: 80
    },
    is_enabled: true
  });
```

---

## 🛡️ Row Level Security (RLS)

All tables have RLS policies enforcing data isolation.

### Customer Isolation

Users can only access data belonging to their customer:

```sql
-- Example: user_profiles table
CREATE POLICY "Users view own customer data"
ON user_profiles FOR SELECT
USING (
  customer_id = (
    SELECT customer_id 
    FROM user_profiles 
    WHERE user_id = auth.uid()
  )
);
```

### Department-Based Access

Some data is further restricted by department:

```sql
-- Example: compliance_frameworks (compliance dept only)
CREATE POLICY "Compliance users access frameworks"
ON compliance_frameworks FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM user_profiles
    WHERE user_id = auth.uid()
    AND department = 'compliance'
    AND customer_id = compliance_frameworks.customer_id
  )
);
```

### Admin Override

Admins can view all customers:

```sql
CREATE POLICY "Admins view all customers"
ON customers FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM user_profiles
    WHERE user_id = auth.uid()
    AND department = 'admin'
  )
);
```

---

## 📈 Rate Limits & Best Practices

### Rate Limits
- **Database Queries**: 100 requests/second per project
- **Edge Functions**: 500 requests/minute per function
- **Auth**: 30 requests/hour per IP (signup/login)

### Best Practices

1. **Use Supabase Client**: Don't make raw HTTP requests
2. **Batch Queries**: Combine related queries with `select()`
3. **Cache Results**: Use TanStack Query for client-side caching
4. **Limit Results**: Always use `.limit()` for large tables
5. **Index Queries**: Ensure foreign keys are indexed
6. **Handle Errors**: Check `error` object on every call

### Example: Efficient Data Fetching

```typescript
// ❌ BAD: Multiple queries
const customer = await supabase.from('customers').select('*').eq('id', id).single();
const profiles = await supabase.from('user_profiles').select('*').eq('customer_id', id);
const customization = await supabase.from('customer_customizations').select('*').eq('customer_id', id).single();

// ✅ GOOD: Single query with relationships
const { data, error } = await supabase
  .from('customers')
  .select(`
    *,
    user_profiles (*),
    customer_customizations (*)
  `)
  .eq('id', id)
  .single();
```

---

## 🧪 Testing APIs

### Using Supabase Dashboard

1. Navigate to backend UI (View Backend in Lovable)
2. Go to SQL Editor
3. Run test queries

### Using Frontend

```typescript
// Add to component for debugging
useEffect(() => {
  const testAPI = async () => {
    const { data, error } = await supabase
      .from('your_table')
      .select('*');
    
    console.log('Test Data:', data);
    console.log('Test Error:', error);
  };
  
  testAPI();
}, []);
```

---

## 🔗 Related Documentation

- [ARCHITECTURE.md](./ARCHITECTURE.md) - Database schema details
- [MODULE_STRUCTURE.md](./MODULE_STRUCTURE.md) - How modules use these APIs
- [Supabase Docs](https://supabase.com/docs) - Official Supabase documentation

---

**API Stability**: These APIs are designed for long-term stability. Breaking changes will be versioned and documented. All changes are traceable via Git history and migration files.