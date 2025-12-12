# Dashboard Data Flow Diagrams

This document contains data flow diagrams for all dashboards in the platform.

## CIPP Dashboard

```mermaid
graph TD
    A[User Opens CIPP Dashboard] --> B{Authenticated?}
    B -->|No| C[Redirect to Auth]
    B -->|Yes| D[Load User Profile]
    D --> E[Fetch Customer ID]
    E --> F[Query cipp_tenants Table]
    F --> G[Query cipp_tenant_health Table]
    G --> H[Display Tenant List]
    H --> I{User Action}
    I -->|Sync Tenants| J[Call cipp-sync Edge Function]
    J --> K[cipp-sync Calls CIPP API]
    K --> L[Update cipp_tenants Table]
    L --> M[Reload Dashboard Data]
    I -->|View Tenant| N[Navigate to Tenant Detail]
    M --> H
```

## CMDB Dashboard

```mermaid
graph TD
    A[User Opens CMDB Dashboard] --> B{Authenticated?}
    B -->|No| C[Redirect to Auth]
    B -->|Yes| D[Load User Profile]
    D --> E[Fetch Customer ID]
    E --> F[Query cmdb_items Table]
    F --> G[Apply Filters & Search]
    G --> H[Display Asset List]
    H --> I{User Action}
    I -->|Add Item| J[Navigate to Add Form]
    I -->|Edit Item| K[Navigate to Edit Form]
    I -->|View Item| L[Navigate to Item Detail]
    I -->|Delete Item| M[Delete from cmdb_items]
    M --> N[Refresh List]
    I -->|Sync NinjaOne| O[Call ninjaone-sync Function]
    O --> P[Fetch Data from NinjaOne API]
    P --> Q[Update cmdb_items Table]
    Q --> N
```

## Change Management Dashboard

```mermaid
graph TD
    A[User Opens Change Management] --> B{Authenticated?}
    B -->|No| C[Redirect to Auth]
    B -->|Yes| D[Load User Profile]
    D --> E[Fetch Customer ID]
    E --> F[Query change_requests Table]
    F --> G[Apply Status Filter]
    G --> H[Display Change Requests]
    H --> I{User Action}
    I -->|Create Change| J[Navigate to New Change Form]
    I -->|View Change| K[Navigate to Change Detail]
    I -->|Update Status| L[Update change_requests Table]
    L --> M[Log to audit_logs]
    M --> N[Trigger Notifications]
    N --> O[Call change-impact-analyzer]
    O --> P[Update Risk Assessment]
    P --> Q[Refresh Dashboard]
```

## Compliance Dashboard

### Scorecard Architecture
The compliance scorecard is calculated by comparing **framework requirements** (what controls need to be met) against **audit logs** (past compliance actions taken). The score measures actual compliance activities performed versus required framework controls.

**Data Flow:**
1. **Load Frameworks** - Defines required compliance controls and standards
2. **Load Audit Logs** - Shows historical compliance actions and activities
3. **Score Calculation** - Compares audit log entries (tagged with compliance activities) against framework's required controls to generate compliance percentage
4. **Evidence Upload** - Creates new audit log entries that feed back into the next score calculation

```mermaid
graph TD
    A[User Opens Compliance Dashboard] --> B{Authenticated?}
    B -->|No| C[Redirect to Auth]
    B -->|Yes| D[Load User Profile]
    D --> E[Fetch Customer ID]
    E --> F[Query compliance_frameworks Table]
    E --> G[Query audit_logs Table]
    F --> H[Calculate Compliance Score]
    G --> H
    H --> I[Display Dashboard with Score]
    I --> J{User Action}
    J -->|Select Framework| K[Navigate to Framework Detail]
    J -->|View Control| L[Navigate to Control Detail]
    J -->|Upload Evidence| M[Navigate to Evidence Upload]
    M --> N[Upload to Storage Bucket]
    N --> O[Create compliance_evidence Record]
    O --> P[Create audit_log Entry]
    P --> Q[Update Control Status]
    Q --> R[Recalculate Compliance Score]
    R --> I
```

## Admin Dashboard

```mermaid
graph TD
    A[User Opens Admin Dashboard] --> B{Authenticated?}
    B -->|No| C[Redirect to Auth]
    B -->|Yes| D[Check Admin Role]
    D -->|Not Admin| E[Redirect to Portal]
    D -->|Admin| F[Load System Stats]
    F --> G[Query Multiple Tables]
    G --> H[Query audit_logs]
    H --> I[Query mcp_execution_logs]
    I --> J[Query workflow_executions]
    J --> K[Display Dashboard]
    K --> L{Admin Action}
    L -->|Manage Users| M[Navigate to User Management]
    L -->|View Logs| N[Navigate to Log Viewer]
    L -->|Manage Integrations| O[Navigate to Integration Settings]
    L -->|System Settings| P[Navigate to Settings]
```

## IT Dashboard

```mermaid
graph TD
    A[User Opens IT Dashboard] --> B{Authenticated?}
    B -->|No| C[Redirect to Auth]
    B -->|Yes| D[Load User Profile]
    D --> E[Fetch Customer ID]
    E --> F[Query cmdb_items for Assets]
    F --> G[Query change_requests]
    G --> H[Query NinjaOne via Edge Function]
    H --> I[Calculate IT Metrics]
    I --> J[Display Dashboard]
    J --> K{User Action}
    K -->|View Assets| L[Navigate to CMDB]
    K -->|Create Ticket| M[Call ninjaone-ticket Function]
    M --> N[Create Ticket in NinjaOne]
    N --> O[Log to audit_logs]
    K -->|View Changes| P[Navigate to Change Management]
```

## Executive Dashboard

```mermaid
graph TD
    A[User Opens Executive Dashboard] --> B{Authenticated?}
    B -->|No| C[Redirect to Auth]
    B -->|Yes| D[Load User Profile]
    D --> E[Fetch Customer ID]
    E --> F[Aggregate Data from All Modules]
    F --> G[Query Compliance Score]
    G --> H[Query Financial Data]
    H --> I[Query HR Metrics]
    I --> J[Query Operations KPIs]
    J --> K[Query Sales Data]
    K --> L[Display Executive Summary]
    L --> M{User Action}
    M -->|Drill Down| N[Navigate to Specific Dashboard]
    M -->|Export Report| O[Generate PDF/Excel Report]
    M -->|View Trends| P[Display Time-Series Charts]
```

## Sales Dashboard

```mermaid
graph TD
    A[User Opens Sales Dashboard] --> B{Authenticated?}
    B -->|No| C[Redirect to Auth]
    B -->|Yes| D[Load User Profile]
    D --> E[Fetch Customer ID]
    E --> F[Query Revio via revio-data Function]
    F --> G[Fetch Invoices]
    G --> H[Fetch Customers]
    H --> I[Calculate Sales Metrics]
    I --> J[Display Dashboard]
    J --> K{User Action}
    K -->|View Customer| L[Navigate to Customer Detail]
    K -->|View Invoice| M[Display Invoice Detail]
    K -->|Generate Quote| N[Create New Quote]
    K -->|Sync Revio| O[Refresh Data from Revio API]
```

## HR Dashboard

```mermaid
graph TD
    A[User Opens HR Dashboard] --> B{Authenticated?}
    B -->|No| C[Redirect to Auth]
    B -->|Yes| D[Load User Profile]
    D --> E[Fetch Customer ID]
    E --> F[Query employee_records Table]
    F --> G[Query onboarding_tasks]
    G --> H[Query time_off_requests]
    H --> I[Calculate HR Metrics]
    I --> J[Display Dashboard]
    J --> K{User Action}
    K -->|Add Employee| L[Navigate to Add Form]
    K -->|Onboarding| M[Navigate to Onboarding Dashboard]
    K -->|Approve Time Off| N[Update time_off_requests]
    N --> O[Send Notification]
```

## Finance Dashboard

```mermaid
graph TD
    A[User Opens Finance Dashboard] --> B{Authenticated?}
    B -->|No| C[Redirect to Auth]
    B -->|Yes| D[Load User Profile]
    D --> E[Fetch Customer ID]
    E --> F[Query Revio via revio-data Function]
    F --> G[Fetch Invoices]
    G --> H[Fetch Payment Data]
    H --> I[Calculate Financial Metrics]
    I --> J[Display Dashboard]
    J --> K{User Action}
    K -->|View Invoice| L[Display Invoice Detail]
    K -->|Generate Report| M[Create Financial Report]
    K -->|Sync Data| N[Refresh from Revio API]
    K -->|Export| O[Generate Excel/CSV Export]
```

## Operations Dashboard

```mermaid
graph TD
    A[User Opens Operations Dashboard] --> B{Authenticated?}
    B -->|No| C[Redirect to Auth]
    B -->|Yes| D[Load User Profile]
    D --> E[Fetch Customer ID]
    E --> F[Query workflow_executions]
    F --> G[Query mcp_execution_logs]
    G --> H[Query change_requests]
    H --> I[Calculate Operations Metrics]
    I --> J[Display Dashboard]
    J --> K{User Action}
    K -->|View Workflow| L[Navigate to Workflow Detail]
    K -->|Execute Workflow| M[Call workflow-executor Function]
    M --> N[Log to mcp_execution_logs]
    N --> O[Update Dashboard]
    K -->|View Changes| P[Navigate to Change Management]
```

## SOC Dashboard

```mermaid
graph TD
    A[User Opens SOC Dashboard] --> B{Authenticated?}
    B -->|No| C[Redirect to Auth]
    B -->|Yes| D[Load User Profile]
    D --> E[Fetch Customer ID]
    E --> F[Query security_incidents]
    F --> G[Query audit_logs]
    G --> H[Query CIPP Security Scores]
    H --> I[Calculate Security Metrics]
    I --> J[Display Dashboard]
    J --> K{User Action}
    K -->|View Incident| L[Navigate to Incident Detail]
    K -->|Create Incident| M[Navigate to Create Form]
    K -->|View Logs| N[Display Audit Logs]
    K -->|Run Security Scan| O[Trigger Security Assessment]
```

## Workflow Automation Dashboard

```mermaid
graph TD
    A[User Opens Workflow Dashboard] --> B{Authenticated?}
    B -->|No| C[Redirect to Auth]
    B -->|Yes| D[Load User Profile]
    D --> E[Fetch Customer ID]
    E --> F[Query workflows Table]
    F --> G[Query workflow_executions]
    G --> H[Display Workflow List]
    H --> I{User Action}
    I -->|Create Workflow| J[Navigate to Workflow Builder]
    I -->|Edit Workflow| K[Navigate to Workflow Builder with ID]
    I -->|Execute Workflow| L[Call workflow-executor Function]
    L --> M[Process Workflow Steps]
    M --> N[Log to workflow_executions]
    N --> O[Log to mcp_execution_logs]
    O --> P[Refresh Dashboard]
    I -->|View Execution| Q[Navigate to Execution Detail]
```

## MCP Server Dashboard

```mermaid
graph TD
    A[User Opens MCP Dashboard] --> B{Authenticated?}
    B -->|No| C[Redirect to Auth]
    B -->|Yes| D[Load User Profile]
    D --> E[Fetch Customer ID]
    E --> F[Query mcp_servers Table]
    F --> G[Query mcp_execution_logs]
    G --> H[Display Server List]
    H --> I{User Action}
    I -->|Configure Server| J[Update mcp_servers Table]
    J --> K[Log Configuration Change]
    I -->|Test Connection| L[Call mcp-server Function]
    L --> M[Test MCP Server Endpoint]
    M --> N[Update Server Status]
    N --> O[Refresh Dashboard]
    I -->|View Logs| P[Display Execution Logs]
    I -->|Generate AI MCP| Q[Call ai-mcp-generator Function]
    Q --> R[Create New MCP Server Config]
```

## Onboarding Dashboard

```mermaid
graph TD
    A[User Opens Onboarding Dashboard] --> B{Authenticated?}
    B -->|No| C[Redirect to Auth]
    B -->|Yes| D[Load User Profile]
    D --> E[Fetch Customer ID]
    E --> F[Query onboarding_tasks Table]
    F --> G[Query employee_records]
    G --> H[Calculate Completion Stats]
    H --> I[Display Dashboard]
    I --> J{User Action}
    J -->|Create Task| K[Insert into onboarding_tasks]
    K --> L[Assign to Employee]
    L --> M[Send Notification]
    J -->|Complete Task| N[Update Task Status]
    N --> O[Log to audit_logs]
    O --> P[Recalculate Progress]
    J -->|Use Template| Q[Navigate to Templates]
    Q --> R[Clone Template Tasks]
```
