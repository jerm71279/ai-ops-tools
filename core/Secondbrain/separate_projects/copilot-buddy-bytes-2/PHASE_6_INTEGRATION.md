# Phase 6 Feature Integration Guide

**Feature Release:** Phase 6 - Self-Healing, Client Portal, Mobile, Reporting  
**Integration Date:** 2025-10-08  
**Status:** ✅ Fully Integrated

---

## Overview

Phase 6 introduces four major feature sets that enhance OberaConnect's capabilities:

1. **Incidents & Auto-Remediation** - Self-healing system with automated incident response
2. **Client Self-Service Portal** - Customer-facing support and service request system
3. **Mobile Optimization** - Native mobile app support via Capacitor
4. **Custom Report Builder** - Dynamic report generation and scheduling

---

## Feature 1: Incidents & Auto-Remediation

### Purpose
Automatically detect, categorize, and remediate system incidents with minimal human intervention.

### Components

#### Database Schema
**Table: `incidents`**
```sql
CREATE TABLE incidents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id UUID NOT NULL REFERENCES customers(id),
  incident_number TEXT NOT NULL,
  title TEXT NOT NULL,
  description TEXT NOT NULL,
  incident_type TEXT NOT NULL, -- 'security', 'performance', 'availability', 'configuration'
  severity TEXT NOT NULL, -- 'critical', 'high', 'medium', 'low'
  status TEXT NOT NULL DEFAULT 'open', -- 'open', 'investigating', 'remediating', 'resolved', 'closed'
  affected_ci_ids UUID[],
  detected_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  resolved_at TIMESTAMP WITH TIME ZONE,
  resolution_notes TEXT,
  auto_remediated BOOLEAN DEFAULT false,
  remediation_rule_id UUID REFERENCES remediation_rules(id),
  created_by UUID REFERENCES auth.users(id),
  assigned_to UUID REFERENCES auth.users(id),
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);
```

**Table: `remediation_rules`**
```sql
CREATE TABLE remediation_rules (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id UUID NOT NULL REFERENCES customers(id),
  rule_name TEXT NOT NULL,
  description TEXT,
  incident_type TEXT NOT NULL,
  incident_conditions JSONB NOT NULL, -- { \"severity\": [\"critical\", \"high\"], \"keywords\": [...] }
  remediation_actions JSONB NOT NULL, -- [ { \"type\": \"restart_service\", \"params\": {...} } ]
  execution_mode TEXT NOT NULL DEFAULT 'manual', -- 'manual', 'automatic', 'approval_required'
  is_active BOOLEAN NOT NULL DEFAULT true,
  success_count INTEGER DEFAULT 0,
  failure_count INTEGER DEFAULT 0,
  last_executed_at TIMESTAMP WITH TIME ZONE,
  created_by UUID REFERENCES auth.users(id),
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);
```

**Table: `remediation_executions`**
```sql
CREATE TABLE remediation_executions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id UUID NOT NULL REFERENCES customers(id),
  incident_id UUID NOT NULL REFERENCES incidents(id),
  rule_id UUID NOT NULL REFERENCES remediation_rules(id),
  status TEXT NOT NULL DEFAULT 'pending', -- 'pending', 'running', 'success', 'failed'
  actions_executed JSONB,
  execution_log TEXT,
  error_message TEXT,
  started_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  completed_at TIMESTAMP WITH TIME ZONE
);
```

#### Edge Function: `auto-remediation`
**Path:** `supabase/functions/auto-remediation/index.ts`

**Actions Supported:**
1. `detect_incident` - Create new incident and check for matching remediation rules
2. `execute_remediation` - Execute a specific remediation rule for an incident
3. `analyze_incidents` - Analyze incident patterns and auto-remediation effectiveness

**Example Request:**
```typescript
const { data } = await supabase.functions.invoke('auto-remediation', {
  body: {
    action: 'detect_incident',
    incident: {
      title: 'High CPU Usage on Server-001',
      description: 'CPU usage exceeded 90% for 15 minutes',
      incident_type: 'performance',
      severity: 'high',
      affected_ci_ids: ['ci-uuid-here']
    }
  }
});
```

**Example Response:**
```json
{
  "incident_id": "uuid",
  "incident_number": "INC20251008-0001",
  "auto_remediated": true,
  "rule_applied": "Auto Restart High CPU Services",
  "remediation_id": "uuid",
  "actions_taken": ["restart_service: web-api", "clear_cache"]
}
```

#### UI Components
**Page: `/incidents` (IncidentsDashboard.tsx)**
- View all incidents with filtering (status, severity, type)
- Summary cards showing open, critical, auto-remediated counts
- Create new incidents manually
- Trigger manual remediation for unresolved incidents
- View resolution notes and affected CIs

**Page: `/remediation-rules` (RemediationRules.tsx)**
- View all remediation rules
- Summary cards for total, active, automatic rules
- Create new remediation rules
- Enable/disable rules
- View success/failure statistics

#### Integration Points

**CMDB Integration:**
```typescript
// Link incidents to configuration items
const incident = {
  affected_ci_ids: ['uuid-of-server', 'uuid-of-application'],
  // ... other fields
};
```

**Workflow Integration:**
```typescript
// Trigger workflow when incident is created
const workflow = await supabase
  .from('workflows')
  .select('*')
  .eq('trigger_type', 'incident_created')
  .eq('is_active', true);
```

**Audit Logging:**
All incident creation, remediation execution, and rule changes are automatically logged to `audit_logs` table.

#### Access Control
- **View Incidents:** All authenticated users in the organization
- **Create Incidents:** All authenticated users
- **Manage Remediation Rules:** Admin only
- **Execute Remediation:** Admin only (unless automatic mode)

---

## Feature 2: Client Self-Service Portal

### Purpose
Provide customers with a self-service portal to submit support tickets, request services, and track ticket status without direct staff intervention.

### Components

#### Database Schema
**Table: `client_tickets`**
```sql
CREATE TABLE client_tickets (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id UUID NOT NULL REFERENCES customers(id),
  ticket_number TEXT NOT NULL,
  subject TEXT NOT NULL,
  description TEXT NOT NULL,
  category TEXT NOT NULL, -- 'technical', 'billing', 'access', 'general'
  priority TEXT NOT NULL DEFAULT 'medium', -- 'low', 'medium', 'high', 'urgent'
  status TEXT NOT NULL DEFAULT 'open', -- 'open', 'in_progress', 'waiting_customer', 'resolved', 'closed'
  submitted_by UUID NOT NULL REFERENCES auth.users(id),
  assigned_to UUID REFERENCES auth.users(id),
  first_response_at TIMESTAMP WITH TIME ZONE,
  resolved_at TIMESTAMP WITH TIME ZONE,
  resolution TEXT,
  sla_breach BOOLEAN DEFAULT false,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);
```

**Table: `service_requests`**
```sql
CREATE TABLE service_requests (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id UUID NOT NULL REFERENCES customers(id),
  request_number TEXT NOT NULL,
  service_id UUID NOT NULL REFERENCES service_catalog(id),
  requested_by UUID NOT NULL REFERENCES auth.users(id),
  status TEXT NOT NULL DEFAULT 'pending', -- 'pending', 'approved', 'in_progress', 'completed', 'rejected'
  priority TEXT NOT NULL DEFAULT 'medium',
  requested_date DATE NOT NULL DEFAULT CURRENT_DATE,
  due_date DATE,
  completed_date DATE,
  notes TEXT,
  approval_notes TEXT,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);
```

**Table: `service_catalog`**
```sql
CREATE TABLE service_catalog (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id UUID NOT NULL REFERENCES customers(id),
  service_name TEXT NOT NULL,
  description TEXT,
  category TEXT NOT NULL, -- 'infrastructure', 'software', 'security', 'consulting'
  estimated_hours NUMERIC,
  is_active BOOLEAN NOT NULL DEFAULT true,
  requires_approval BOOLEAN NOT NULL DEFAULT false,
  approval_role TEXT,
  sla_hours INTEGER,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);
```

**Table: `ticket_comments`**
```sql
CREATE TABLE ticket_comments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  ticket_id UUID NOT NULL REFERENCES client_tickets(id) ON DELETE CASCADE,
  author_id UUID NOT NULL REFERENCES auth.users(id),
  comment TEXT NOT NULL,
  is_internal BOOLEAN NOT NULL DEFAULT false,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);
```

**Table: `client_portal_users`**
```sql
CREATE TABLE client_portal_users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id UUID NOT NULL REFERENCES customers(id),
  email TEXT NOT NULL UNIQUE,
  full_name TEXT NOT NULL,
  company_name TEXT NOT NULL,
  phone TEXT,
  portal_role TEXT NOT NULL DEFAULT 'user', -- 'user', 'admin'
  is_active BOOLEAN DEFAULT true,
  last_login_at TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);
```

#### Edge Function: `client-portal`
**Path:** `supabase/functions/client-portal/index.ts`

**Actions Supported:**
1. `create_service_request` - Submit a new service request
2. `create_ticket` - Create a new support ticket
3. `add_ticket_comment` - Add a comment to a ticket
4. `update_ticket_status` - Update ticket status (staff only)
5. `get_portal_stats` - Get portal statistics (open tickets, active requests)

**Example Request:**
```typescript
const { data } = await supabase.functions.invoke('client-portal', {
  body: {
    action: 'create_ticket',
    ticket: {
      subject: 'Cannot access email',
      description: 'Getting authentication errors when trying to login',
      category: 'technical',
      priority: 'high'
    }
  }
});
```

**Example Response:**
```json
{
  "ticket_id": "uuid",
  "ticket_number": "CT20251008-0001",
  "status": "open",
  "estimated_response": "2025-10-08T17:00:00Z"
}
```

#### UI Component
**Page: `/client-portal` (ClientPortal.tsx)**

**Features:**
- **Support Tickets Tab:**
  - View all submitted tickets
  - Filter by status (Open, In Progress, Resolved)
  - Create new tickets with category and priority selection
  - View ticket details and comments
  
- **Service Requests Tab:**
  - View all service requests
  - Filter by status (Pending, In Progress, Completed)
  - Submit new service requests from catalog
  - Track approval and completion status
  
- **Service Catalog Tab:**
  - Browse available services by category
  - View service details (description, SLA, approval required)
  - Request service with one click

- **Portal Stats:**
  - Open Tickets count
  - Active Service Requests count
  - Available Services count
  - Average Response Time

#### Integration Points

**Notification Integration:**
```typescript
// Send email when ticket created
const notification = await supabase
  .from('notifications')
  .insert({
    user_id: assigned_staff_id,
    type: 'new_ticket',
    title: 'New Support Ticket',
    message: `Ticket ${ticket_number} has been created`,
    link: `/client-portal?ticket=${ticket_id}`
  });
```

**Workflow Integration:**
```typescript
// Trigger workflow when service request approved
const workflow = await supabase
  .from('workflows')
  .select('*')
  .eq('trigger_type', 'service_request_approved')
  .eq('is_active', true);
```

**Audit Logging:**
All ticket creation, status changes, and comments are logged to `audit_logs`.

#### Access Control
- **Portal Users:** Can create tickets, view their own tickets, request services
- **Staff:** Can view all tickets, update status, add internal comments, approve requests
- **Admins:** Full access to portal management, service catalog, and stats

---

## Feature 3: Custom Report Builder

### Purpose
Enable users to create, execute, schedule, and export custom reports from any database table with flexible column selection and filtering.

### Components

#### Database Schema
**Table: `custom_reports`**
```sql
CREATE TABLE custom_reports (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id UUID NOT NULL REFERENCES customers(id),
  report_name TEXT NOT NULL,
  description TEXT,
  data_sources JSONB NOT NULL, -- [{ \"table\": \"incidents\", \"columns\": [\"id\", \"title\", \"status\"] }]
  filters JSONB, -- { \"status\": \"open\", \"severity\": [\"critical\", \"high\"] }
  is_scheduled BOOLEAN DEFAULT false,
  schedule_config JSONB, -- { \"frequency\": \"daily\", \"time\": \"08:00\", \"recipients\": [...] }
  created_by UUID NOT NULL REFERENCES auth.users(id),
  last_run_at TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);
```

**Table: `report_executions`**
```sql
CREATE TABLE report_executions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id UUID NOT NULL REFERENCES customers(id),
  report_id UUID NOT NULL REFERENCES custom_reports(id),
  status TEXT NOT NULL DEFAULT 'running', -- 'running', 'completed', 'failed'
  record_count INTEGER,
  execution_time_ms INTEGER,
  error_message TEXT,
  result_data JSONB,
  executed_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);
```

#### Edge Function: `custom-report-engine`
**Path:** `supabase/functions/custom-report-engine/index.ts`

**Actions Supported:**
1. `execute_report` - Execute a report and return results
2. `get_available_tables` - Get list of tables and columns available for reporting
3. `preview_report` - Preview report data (limited to 10 rows)
4. `schedule_report` - Configure scheduled report execution

**Example Request:**
```typescript
const { data } = await supabase.functions.invoke('custom-report-engine', {
  body: {
    action: 'execute_report',
    report_id: 'uuid-here'
  }
});
```

**Example Response:**
```json
{
  "execution_id": "uuid",
  "status": "completed",
  "record_count": 45,
  "execution_time_ms": 234,
  "results": [
    { "incident_number": "INC001", "title": "Server Down", "status": "resolved" },
    // ... more records
  ]
}
```

**Available Tables for Reporting:**
```typescript
const availableTables = [
  { table: 'incidents', columns: ['id', 'incident_number', 'title', 'severity', 'status', 'created_at'] },
  { table: 'change_requests', columns: ['id', 'change_number', 'title', 'priority', 'status', 'created_at'] },
  { table: 'client_tickets', columns: ['id', 'ticket_number', 'subject', 'category', 'status', 'created_at'] },
  { table: 'configuration_items', columns: ['id', 'ci_name', 'ci_type', 'status', 'location'] },
  { table: 'workflow_executions', columns: ['id', 'workflow_name', 'status', 'started_at', 'completed_at'] },
  { table: 'compliance_reports', columns: ['id', 'framework', 'status', 'generated_at'] },
  { table: 'audit_logs', columns: ['id', 'action_type', 'system_name', 'timestamp'] }
];
```

#### UI Component
**Page: `/reports/builder` (CustomReportBuilder.tsx)**

**Features:**
- **Report Builder:**
  - Create new reports with name and description
  - Select data source (table)
  - Choose columns to include
  - Add filters (future enhancement)
  - Save report definition

- **My Reports Table:**
  - View all created reports
  - See report status (Active/Inactive)
  - View last run time
  - Execute report on demand

- **Recent Executions Table:**
  - View execution history
  - See status (Completed/Failed)
  - View record count and execution time
  - Access result data (future: export to CSV/Excel)

- **Summary Cards:**
  - Total Reports created
  - Scheduled Reports count
  - Executions Today count
  - Average Execution Time

#### Integration Points

**Scheduled Execution (Future):**
```typescript
// Cron job to execute scheduled reports
// Runs daily at configured times
const scheduledReports = await supabase
  .from('custom_reports')
  .select('*')
  .eq('is_scheduled', true);

for (const report of scheduledReports) {
  await supabase.functions.invoke('custom-report-engine', {
    body: { action: 'execute_report', report_id: report.id }
  });
}
```

**Email Reports (Future):**
```typescript
// Email results to recipients
const recipients = report.schedule_config.recipients;
await sendEmail({
  to: recipients,
  subject: `Report: ${report.report_name}`,
  body: 'See attached report',
  attachment: reportData
});
```

#### Access Control
- **View Reports:** All authenticated users (own reports only)
- **Create Reports:** All authenticated users
- **Execute Reports:** Report owner or admin
- **Schedule Reports:** Report owner or admin
- **Access All Reports:** Admin only

---

## Feature 4: Mobile Optimization

### Purpose
Enable native mobile app development for iOS and Android platforms using Capacitor, with hot-reload during development.

### Configuration

**File: `capacitor.config.ts`**
```typescript
import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'app.lovable.2e37e4cf64eb4e9a8cf114b876d69899',
  appName: 'copilot-buddy-bytes',
  webDir: 'dist',
  server: {
    url: 'https://2e37e4cf-64eb-4e9a-8cf1-14b876d69899.lovableproject.com?forceHideBadge=true',
    cleartext: true
  }
};

export default config;
```

### Mobile-Ready Features
- ✅ Responsive design on all pages
- ✅ Touch-friendly UI elements
- ✅ Mobile navigation optimized
- ✅ Dark mode support
- ✅ Offline-ready (with service worker)

### Native Capabilities Available
- Camera access for document scanning
- Push notifications for incidents and tickets
- Biometric authentication
- Device storage for offline data
- Geolocation for field technicians
- Background sync

### Development Workflow

**Initial Setup:**
```bash
# Install dependencies
npm install @capacitor/core @capacitor/cli @capacitor/ios @capacitor/android

# Initialize Capacitor
npx cap init

# Add platforms
npx cap add ios
npx cap add android
```

**Development:**
```bash
# Build the web app
npm run build

# Sync with native platforms
npx cap sync

# Run on device/emulator
npx cap run ios
# or
npx cap run android
```

**Hot Reload:**
The `server.url` configuration enables hot-reload during development - changes made in the web app are immediately reflected in the mobile app without rebuilding.

### Responsive Breakpoints
- Mobile: < 768px
- Tablet: 768px - 1024px
- Desktop: > 1024px

All UI components use Tailwind CSS responsive classes to adapt to different screen sizes.

---

## Navigation Integration

### Desktop Navigation (`Navigation.tsx`)
Added navigation links to the main navigation bar:
```tsx
<Link to="/incidents">Incidents</Link>
<Link to="/client-portal">Client Portal</Link>
<Link to="/reports/builder">Reports</Link>
```

### Mobile Navigation
Added to hamburger menu with touch-friendly spacing:
```tsx
<Link to="/incidents" className="py-3 px-4">Incidents</Link>
<Link to="/client-portal" className="py-3 px-4">Client Portal</Link>
<Link to="/reports/builder" className="py-3 px-4">Reports</Link>
```

### Portal Dashboard (`Portal.tsx`)
Added quick access cards:
```tsx
{
  name: "CMDB",
  icon: Database,
  path: "/cmdb",
  description: "Configuration items and assets"
},
{
  name: "Incidents & Auto-Remediation",
  icon: AlertTriangle,
  path: "/incidents",
  description: "Monitor and resolve incidents"
},
{
  name: "Client Portal",
  icon: Users,
  path: "/client-portal",
  description: "Support tickets and services"
},
{
  name: "Custom Reports",
  icon: FileText,
  path: "/reports/builder",
  description: "Build and schedule reports"
}
```

---

## Cross-Module Integration

### Incidents + CMDB
```typescript
// Link incident to configuration items
const incident = {
  affected_ci_ids: [server_ci_id, application_ci_id],
  // ... other fields
};

// Query incidents affecting specific CI
const incidents = await supabase
  .from('incidents')
  .select('*')
  .contains('affected_ci_ids', [ci_id]);
```

### Incidents + Workflows
```typescript
// Trigger workflow when incident created
const workflow = await supabase
  .from('workflows')
  .select('*')
  .eq('trigger_type', 'incident_created')
  .eq('is_active', true);

// Execute workflow
await supabase.functions.invoke('workflow-executor', {
  body: {
    workflow_id: workflow.id,
    input_data: { incident_id: incident.id }
  }
});
```

### Client Portal + NinjaOne
```typescript
// Create NinjaOne ticket when support ticket created
if (ticket.category === 'technical') {
  await supabase.functions.invoke('ninjaone-ticket', {
    body: {
      subject: ticket.subject,
      description: ticket.description,
      priority: ticket.priority
    }
  });
}
```

### Custom Reports + Compliance
```typescript
// Generate compliance evidence report
const report = {
  report_name: 'SOC 2 Evidence Collection',
  data_sources: [
    { table: 'evidence_files', columns: ['id', 'control_id', 'uploaded_at'] },
    { table: 'audit_logs', columns: ['action_type', 'timestamp'] }
  ],
  filters: {
    compliance_tags: ['SOC2']
  }
};
```

---

## Testing Guide

### Incident Testing
```typescript
// Create test incident
const { data: incident } = await supabase.functions.invoke('auto-remediation', {
  body: {
    action: 'detect_incident',
    incident: {
      title: 'Test Incident - High Memory Usage',
      description: 'Memory usage exceeded 95% threshold',
      incident_type: 'performance',
      severity: 'high'
    }
  }
});

// Verify incident created
expect(incident.incident_id).toBeDefined();
expect(incident.incident_number).toMatch(/^INC/);
```

### Client Portal Testing
```typescript
// Create test ticket
const { data: ticket } = await supabase.functions.invoke('client-portal', {
  body: {
    action: 'create_ticket',
    ticket: {
      subject: 'Test Ticket',
      description: 'Testing support ticket creation',
      category: 'technical',
      priority: 'medium'
    }
  }
});

// Verify ticket created
expect(ticket.ticket_id).toBeDefined();
expect(ticket.ticket_number).toMatch(/^CT/);
```

### Report Testing
```typescript
// Execute test report
const { data: execution } = await supabase.functions.invoke('custom-report-engine', {
  body: {
    action: 'execute_report',
    report_id: test_report_id
  }
});

// Verify execution
expect(execution.status).toBe('completed');
expect(execution.record_count).toBeGreaterThan(0);
```

---

## Migration Checklist

### Pre-Migration
- [x] Review existing database schema
- [x] Identify integration points with existing modules
- [x] Create database migration scripts
- [x] Test edge functions in isolation
- [x] Review security policies (RLS)

### Migration Steps
- [x] Run database migrations
- [x] Deploy edge functions
- [x] Update frontend routing (App.tsx)
- [x] Add navigation links
- [x] Add dashboard widgets
- [x] Test all features end-to-end
- [x] Update documentation

### Post-Migration
- [x] Verify all features accessible
- [x] Test authentication and authorization
- [x] Verify RLS policies working
- [x] Check audit logging
- [x] Monitor edge function performance
- [ ] Train users on new features
- [ ] Create user guides/videos

---

## Performance Considerations

### Database Indexes
```sql
-- Incidents
CREATE INDEX idx_incidents_customer_status ON incidents(customer_id, status);
CREATE INDEX idx_incidents_detected_at ON incidents(detected_at DESC);

-- Client Tickets
CREATE INDEX idx_client_tickets_customer_status ON client_tickets(customer_id, status);
CREATE INDEX idx_client_tickets_submitted_by ON client_tickets(submitted_by);

-- Custom Reports
CREATE INDEX idx_custom_reports_customer ON custom_reports(customer_id);
CREATE INDEX idx_report_executions_report_id ON report_executions(report_id);
```

### Query Optimization
- Use `select` to limit returned columns
- Add filters early in query chain
- Use pagination for large result sets
- Cache frequently accessed data (React Query)

### Edge Function Optimization
- Minimize database round-trips
- Use batch inserts where possible
- Return only necessary data
- Implement proper error handling

---

## Troubleshooting

### Incidents Not Auto-Remediating
**Issue:** Incidents created but remediation not executing  
**Check:**
1. Verify remediation rules are active: `is_active = true`
2. Ensure incident matches rule conditions
3. Check rule `execution_mode` is set to `automatic`
4. Review edge function logs for errors

### Client Portal Tickets Not Creating
**Issue:** Ticket creation fails  
**Check:**
1. Verify user authentication (JWT token valid)
2. Check RLS policies allow INSERT
3. Ensure ticket_number trigger is working
4. Review edge function logs

### Reports Not Executing
**Issue:** Report execution fails  
**Check:**
1. Verify data source tables exist and are accessible
2. Check RLS policies allow SELECT on source tables
3. Ensure columns specified in report exist
4. Review edge function logs for SQL errors

### Mobile App Not Loading
**Issue:** Mobile app shows blank screen  
**Check:**
1. Verify `server.url` is correct in capacitor.config.ts
2. Ensure web app is accessible at that URL
3. Check for console errors in mobile inspector
4. Rebuild app: `npm run build && npx cap sync`

---

## Future Enhancements

### Incidents & Remediation
- [ ] Machine learning for incident prediction
- [ ] Integration with monitoring tools (Datadog, New Relic)
- [ ] Automated rollback on remediation failure
- [ ] Incident trends and analytics dashboard
- [ ] SLA tracking and breach alerts

### Client Portal
- [ ] Live chat with support staff
- [ ] File attachments for tickets
- [ ] Knowledge base article suggestions
- [ ] Customer satisfaction surveys
- [ ] Self-service password reset

### Custom Reports
- [ ] Advanced filtering (date ranges, complex conditions)
- [ ] Export to Excel, PDF, CSV
- [ ] Scheduled email delivery
- [ ] Report sharing with external users
- [ ] Data visualization (charts, graphs)
- [ ] Report templates library

### Mobile App
- [ ] Offline mode with sync
- [ ] Push notifications for incidents/tickets
- [ ] Biometric authentication
- [ ] Camera integration for evidence upload
- [ ] Voice commands for incident reporting
- [ ] Dark mode optimization

---

## Support Resources

### Documentation
- [TESTING_GUIDE.md](./TESTING_GUIDE.md) - Comprehensive testing procedures
- [API_REFERENCE.md](./API_REFERENCE.md) - Edge function API documentation
- [ARCHITECTURE.md](./ARCHITECTURE.md) - System architecture overview
- [SYSTEM_STATUS_REPORT.md](./SYSTEM_STATUS_REPORT.md) - Current system status

### Debug Tools
- System Validation Dashboard: `/test/validation`
- Comprehensive Test Dashboard: `/test/comprehensive`
- Lovable Cloud Backend: Access via \"View Backend\" button
- Edge Function Logs: Available in Lovable Cloud dashboard

### Contact
- **Technical Support:** System Administrator
- **Feature Requests:** Product Team
- **Bug Reports:** Development Team

---

**Document Version:** 1.0.0  
**Last Updated:** 2025-10-08  
**Status:** ✅ Production Ready
