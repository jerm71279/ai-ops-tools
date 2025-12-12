# CIPP Integration Guide

## 📋 Overview

The CIPP (CyberDrain Improved Partner Portal) integration provides centralized Microsoft 365 tenant management, security automation, and policy deployment for MSPs managing multiple customer tenants.

## 🎯 Key Capabilities

### 1. Multi-Tenant Management
- **Tenant Registry**: Centralized view of all Microsoft 365 tenants
- **Bulk Operations**: Apply changes across multiple tenants simultaneously
- **Tenant Health Monitoring**: Real-time security and compliance scoring
- **Sync Status**: Track synchronization state with CIPP instance

### 2. Security Automation
- **Security Baselines**: Pre-configured security standards (CIS, NIST, custom)
- **Automated Deployment**: Apply baselines across tenant portfolio
- **Policy Templates**: Reusable policy configurations
- **Compliance Tracking**: Monitor security posture across all tenants

### 3. Policy Management
- **Conditional Access**: Centralized CA policy deployment
- **Intune Configuration**: Device management policies
- **Exchange Settings**: Email security configurations
- **SharePoint Policies**: Data protection settings

### 4. Monitoring & Alerts
- **Health Scores**: Overall tenant health metrics (0-100)
- **Security Scores**: Microsoft Secure Score integration
- **Compliance Scores**: Framework compliance tracking
- **Automated Alerts**: Proactive issue detection

## 🏗️ Architecture

### Database Schema

```sql
-- Tenant Registry
cipp_tenants (
  id UUID PRIMARY KEY,
  customer_id UUID,           -- Links to OberaConnect customer
  tenant_id TEXT,             -- Microsoft 365 tenant ID
  tenant_name TEXT,           -- Display name
  default_domain_name TEXT,   -- Primary domain
  status TEXT,                -- 'active', 'inactive', 'error'
  last_sync_at TIMESTAMPTZ,   -- Last sync timestamp
  sync_status TEXT,           -- 'success', 'pending', 'error'
  metadata JSONB              -- Additional tenant data
)

-- Security Baselines
cipp_security_baselines (
  id UUID PRIMARY KEY,
  customer_id UUID,
  baseline_name TEXT,         -- 'CIS Microsoft 365', 'Custom Security'
  baseline_type TEXT,         -- 'security', 'compliance', 'custom'
  settings JSONB,             -- Baseline configuration
  applied_to_tenants UUID[]   -- Array of tenant IDs
)

-- Policy Management
cipp_policies (
  id UUID PRIMARY KEY,
  customer_id UUID,
  tenant_id UUID,
  policy_type TEXT,           -- 'conditional_access', 'intune', 'exchange'
  policy_name TEXT,
  configuration JSONB,        -- Policy settings
  status TEXT,                -- 'active', 'pending', 'error'
  last_applied_at TIMESTAMPTZ
)

-- Health Monitoring
cipp_tenant_health (
  id UUID PRIMARY KEY,
  tenant_id UUID,
  health_score INTEGER,       -- Overall health (0-100)
  security_score INTEGER,     -- Microsoft Secure Score
  compliance_score INTEGER,   -- Compliance rating
  alerts JSONB,               -- Active alerts
  recommendations JSONB,      -- Improvement suggestions
  last_checked_at TIMESTAMPTZ
)

-- Audit Trail
cipp_audit_logs (
  id UUID PRIMARY KEY,
  customer_id UUID,
  tenant_id UUID,
  action_type TEXT,           -- 'sync', 'apply_baseline', 'deploy_policy'
  action_description TEXT,
  performed_by UUID,
  result TEXT,                -- 'success', 'error'
  details JSONB,
  created_at TIMESTAMPTZ
)
```

### Edge Function: `cipp-sync`

**Endpoint**: `supabase/functions/cipp-sync/index.ts`

**Authentication**: JWT required (admin role)

**Actions**:

#### 1. Sync Tenants
```typescript
const { data } = await supabase.functions.invoke('cipp-sync', {
  body: {
    action: 'sync_tenants',
    customerId: 'uuid-string'
  }
});
```

**Flow**:
1. Calls CIPP `/api/ListTenants` endpoint
2. Retrieves all managed Microsoft 365 tenants
3. Upserts to `cipp_tenants` table
4. Returns sync results

#### 2. Get Tenant Health
```typescript
const { data } = await supabase.functions.invoke('cipp-sync', {
  body: {
    action: 'get_tenant_health',
    tenantId: 'tenant-id',
    customerId: 'uuid-string'
  }
});
```

**Flow**:
1. Calls CIPP `/api/ListGraphRequest` with `reports/getSecureScore`
2. Fetches Microsoft Secure Score data
3. Calculates health metrics
4. Inserts into `cipp_tenant_health` table

#### 3. Apply Security Baseline
```typescript
const { data } = await supabase.functions.invoke('cipp-sync', {
  body: {
    action: 'apply_baseline',
    baselineId: 'uuid-string',
    targetTenantIds: ['tenant-1', 'tenant-2'],
    customerId: 'uuid-string'
  }
});
```

**Flow**:
1. Fetches baseline settings from database
2. Calls CIPP `/api/AddStandardsDeploy` for each tenant
3. Logs results to `cipp_audit_logs`
4. Returns application results

## 🔧 Setup Instructions

### Prerequisites
1. Active CIPP instance (self-hosted or CyberDrain-hosted)
2. CIPP API key with tenant management permissions
3. Microsoft 365 admin access for target tenants

### Configuration Steps

#### 1. Add CIPP Credentials
Store credentials securely in Lovable Cloud secrets:
- `CIPP_URL` - Your CIPP instance URL (e.g., `https://cipp.yourdomain.com`)
- `CIPP_API_KEY` - CIPP API key with appropriate permissions

#### 2. Navigate to CIPP Dashboard
Access the CIPP management portal at `/cipp` (requires authentication)

#### 3. Sync Tenants
Click "Sync Tenants" button to import all managed tenants from CIPP

#### 4. Monitor Health
View tenant health scores, security metrics, and compliance status

## 📊 CIPP Dashboard Features

### Tenant Overview
- **Total Tenants**: Count of managed Microsoft 365 tenants
- **Health Distribution**: Healthy, warning, and critical tenant counts
- **Average Security Score**: Aggregate Microsoft Secure Score
- **Status Indicators**: Real-time sync status per tenant

### Tenant Management
- **Tenant Cards**: Visual display with health and security scores
- **Domain Information**: Primary domain and display name
- **Last Sync Timestamp**: Track data freshness
- **Quick Actions**: Manage button for tenant-specific operations

### Security Baselines Tab
- Create custom security baselines
- Apply pre-configured standards (CIS, NIST)
- Track baseline deployment status
- View applied tenants per baseline

### Policies Tab
- Conditional Access policy management
- Intune configuration deployment
- Exchange and SharePoint policies
- Policy status tracking

### Audit Logs Tab
- Complete action history
- User attribution
- Success/failure tracking
- Detailed operation logs

## 🔒 Security & Access Control

### Row Level Security (RLS)
```sql
-- Users can view tenants in their organization
CREATE POLICY "Users can view tenants in their organization"
  ON cipp_tenants FOR SELECT
  USING (customer_id IN (
    SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
  ));

-- Admins can manage all CIPP resources
CREATE POLICY "Admins can manage tenants"
  ON cipp_tenants FOR ALL
  USING (has_role(auth.uid(), 'admin'::app_role));
```

### Audit Logging
All CIPP actions are logged to `cipp_audit_logs`:
- Tenant synchronization
- Baseline applications
- Policy deployments
- Health check requests

## 🔍 CIPP API Reference

### Authentication
CIPP uses API key authentication via `X-API-KEY` header:
```typescript
headers: {
  'Content-Type': 'application/json',
  'X-API-KEY': cippApiKey
}
```

### Key Endpoints

#### List Tenants
**Endpoint**: `GET /api/ListTenants`

**Response**:
```json
[
  {
    "customerId": "tenant-guid",
    "tenantId": "tenant-guid",
    "displayName": "Customer Name",
    "defaultDomainName": "customer.onmicrosoft.com"
  }
]
```

#### Get Secure Score
**Endpoint**: `POST /api/ListGraphRequest`

**Request**:
```json
{
  "TenantFilter": "tenant-id",
  "Endpoint": "reports/getSecureScore"
}
```

**Response**:
```json
{
  "currentScore": 85,
  "maxScore": 100,
  "controlScores": [...]
}
```

#### Apply Standards
**Endpoint**: `POST /api/AddStandardsDeploy`

**Request**:
```json
{
  "TenantFilter": "tenant-id",
  "Standards": {
    "enableMFA": true,
    "blockLegacyAuth": true,
    "requireDeviceCompliance": true
  }
}
```

## 📈 Usage Workflow

### Initial Setup
1. **Configure Credentials**: Add CIPP_URL and CIPP_API_KEY via secrets
2. **Navigate to Dashboard**: Go to `/cipp`
3. **Sync Tenants**: Click "Sync Tenants" to import from CIPP
4. **Verify Health**: Check tenant health scores and security metrics

### Regular Operations
1. **Monitor Health**: Review tenant health dashboard daily
2. **Apply Baselines**: Deploy security standards to new tenants
3. **Manage Policies**: Update Conditional Access and Intune policies
4. **Review Alerts**: Check recommendations and security alerts
5. **Audit Trail**: Review action logs for compliance

### Security Baseline Deployment
1. Create baseline in "Security Baselines" tab
2. Configure desired security settings
3. Select target tenants
4. Click "Apply Baseline"
5. Monitor deployment status in audit logs

## 🐛 Troubleshooting

### Issue: Tenants Not Syncing
**Symptoms**: Empty tenant list after sync
**Solutions**:
1. Verify CIPP_URL and CIPP_API_KEY are configured
2. Check CIPP API key permissions
3. Review edge function logs for API errors
4. Ensure CIPP instance is accessible

### Issue: Health Scores Not Updating
**Symptoms**: Missing or outdated health scores
**Solutions**:
1. Manually trigger health check for specific tenant
2. Verify Microsoft Graph API permissions in CIPP
3. Check tenant status in CIPP interface
4. Review `cipp_tenant_health` table data

### Issue: Baseline Application Fails
**Symptoms**: Error when applying security baseline
**Solutions**:
1. Verify tenant has required licenses
2. Check baseline configuration validity
3. Review CIPP audit logs for detailed error
4. Ensure no conflicting policies exist

## 📊 Monitoring & Metrics

### Key Metrics
- **Total Managed Tenants**: Track portfolio size
- **Health Score Average**: Overall security posture
- **Critical Alerts**: High-priority security issues
- **Baseline Coverage**: % of tenants with baselines applied

### Health Score Interpretation
- **80-100**: Healthy - Good security posture
- **60-79**: Warning - Action recommended
- **0-59**: Critical - Immediate attention required

## 🔄 Integration Points

### With Change Management
- Create change requests for tenant modifications
- Track security baseline deployments as changes
- Link CIPP actions to change records

### With Compliance Portal
- Map security baselines to compliance controls
- Generate evidence from tenant health data
- Track framework compliance across tenants

### With Audit Logging
- All CIPP actions logged to `audit_logs`
- Privileged access tracking
- Compliance tag integration

## 📚 Additional Resources

- **CIPP Documentation**: [https://docs.cipp.app/](https://docs.cipp.app/)
- **Microsoft 365 Security**: [https://learn.microsoft.com/en-us/microsoft-365/security/](https://learn.microsoft.com/en-us/microsoft-365/security/)
- **Architecture**: See `ARCHITECTURE.md` for system design
- **API Reference**: See `API_REFERENCE.md` for edge function details

## 🚀 Future Enhancements

### Planned Features
- **Automated Health Checks**: Scheduled health score updates
- **Alert Notifications**: Email/SMS alerts for critical issues
- **Policy Templates**: Pre-built policy configurations
- **Bulk Policy Deployment**: Multi-policy deployment workflows
- **Tenant Comparison**: Side-by-side security comparison
- **Compliance Reporting**: Framework-specific reports per tenant

### Integration Opportunities
- **NinjaOne Integration**: Link RMM data with tenant health
- **Workflow Automation**: Automated baseline deployment workflows
- **AI Recommendations**: ML-powered security suggestions

---

**Last Updated**: October 6, 2025  
**Status**: Initial implementation complete, credentials pending configuration
